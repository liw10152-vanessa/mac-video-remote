// Copyright © 2026 liw10152-vanessa. All rights reserved. See LICENSE.md.
let cursor = null;

async function settings() {
  return chrome.storage.local.get({
    endpoint: 'http://127.0.0.1:8765',
    pairingCode: ''
  });
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.type !== 'poll') return false;
  settings()
    .then(async ({endpoint, pairingCode}) => {
      if (!/^\d{6}$/.test(pairingCode)) return {configured: false, commands: []};
      const suffix = cursor === null ? '' : `?since=${cursor}`;
      const response = await fetch(`${endpoint}/api/browser/poll${suffix}`, {
        headers: {'X-Pair-Code': pairingCode},
        cache: 'no-store'
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = await response.json();
      cursor = payload.cursor;
      return {configured: true, commands: payload.commands || []};
    })
    .then(sendResponse)
    .catch(error => sendResponse({configured: true, commands: [], error: String(error)}));
  return true;
});
