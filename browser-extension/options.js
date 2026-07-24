// Copyright © 2026 liw10152-vanessa. All rights reserved. See LICENSE.md.
const endpoint = document.querySelector('#endpoint');
const pairingCode = document.querySelector('#pairingCode');
const status = document.querySelector('#status');

chrome.storage.local.get({
  endpoint: 'http://127.0.0.1:8765',
  pairingCode: ''
}).then(values => {
  endpoint.value = values.endpoint;
  pairingCode.value = values.pairingCode;
});

document.querySelector('#save').addEventListener('click', async () => {
  if (!/^https?:\/\/(127\.0\.0\.1|localhost):\d+$/.test(endpoint.value)) {
    status.textContent = '服务地址格式不正确';
    return;
  }
  if (!/^\d{6}$/.test(pairingCode.value)) {
    status.textContent = '请输入六位配对码';
    return;
  }
  await chrome.storage.local.set({
    endpoint: endpoint.value.replace(/\/$/, ''),
    pairingCode: pairingCode.value
  });
  status.textContent = '已保存';
});
