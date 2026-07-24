// Copyright © 2026 liw10152-vanessa. All rights reserved. See LICENSE.md.
const SPEEDS = [0.5, 1, 1.25, 1.5, 2, 3];
let previousHoldRate = null;

function activeVideo() {
  const videos = [...document.querySelectorAll('video')];
  const visible = videos.filter(video => {
    const rect = video.getBoundingClientRect();
    return rect.width > 80 && rect.height > 45 && rect.bottom > 0 && rect.right > 0;
  });
  return (visible.length ? visible : videos)
    .sort((a, b) => {
      const ar = a.getBoundingClientRect();
      const br = b.getBoundingClientRect();
      return (br.width * br.height) - (ar.width * ar.height);
    })[0];
}

function setSpeed(video, value) {
  video.defaultPlaybackRate = value;
  video.playbackRate = value;
}

async function perform(action) {
  const video = activeVideo();
  if (!video) return;

  if (action === 'playPause') {
    if (video.paused) await video.play().catch(() => {});
    else video.pause();
  } else if (action === 'seekBackward') {
    video.currentTime = Math.max(0, video.currentTime - 10);
  } else if (action === 'seekForward') {
    video.currentTime = Math.min(video.duration || Infinity, video.currentTime + 10);
  } else if (action === 'speedHalf') {
    setSpeed(video, 0.5);
  } else if (action === 'speedNormal') {
    setSpeed(video, 1);
  } else if (action === 'speed125') {
    setSpeed(video, 1.25);
  } else if (action === 'speed150') {
    setSpeed(video, 1.5);
  } else if (action === 'speedDouble') {
    setSpeed(video, 2);
  } else if (action === 'speedUp' || action === 'speedDown') {
    const direction = action === 'speedUp' ? 1 : -1;
    const nearest = SPEEDS.reduce((best, item, index) =>
      Math.abs(item - video.playbackRate) < Math.abs(SPEEDS[best] - video.playbackRate) ? index : best, 0);
    setSpeed(video, SPEEDS[Math.max(0, Math.min(SPEEDS.length - 1, nearest + direction))]);
  } else if (action === 'holdFastStart') {
    if (previousHoldRate === null) previousHoldRate = video.playbackRate;
    setSpeed(video, 3);
  } else if (action === 'holdFastEnd') {
    setSpeed(video, previousHoldRate === null ? 1 : previousHoldRate);
    previousHoldRate = null;
  } else if (action === 'mute') {
    video.muted = !video.muted;
  }
}

async function poll() {
  if (document.visibilityState !== 'visible' || !document.hasFocus() || !activeVideo()) return;
  try {
    const response = await chrome.runtime.sendMessage({type: 'poll'});
    for (const command of response?.commands || []) await perform(command.action);
  } catch (_) {
    // The background worker may restart while the tab is open; the next poll reconnects.
  }
}

setInterval(poll, 600);
poll();
