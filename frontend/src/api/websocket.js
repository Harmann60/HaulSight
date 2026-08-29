let ws = null;
let reconnectTimer = null;
let listeners = [];

const WS_URL = 'wss://haulsight.onrender.com/ws';
export function connectWebSocket() {
  if (ws && ws.readyState === WebSocket.OPEN) return;

  ws = new WebSocket(WS_URL);

  ws.onopen = () => {
    console.log('[WS] Connected');
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
    notify({ type: 'ws_connected', data: {} });
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      notify(msg);
    } catch (e) {
      console.warn('[WS] Failed to parse message:', e);
    }
  };

  ws.onclose = () => {
    console.log('[WS] Disconnected, reconnecting in 3s...');
    notify({ type: 'ws_disconnected', data: {} });
    reconnectTimer = setTimeout(connectWebSocket, 3000);
  };

  ws.onerror = (err) => {
    console.error('[WS] Error:', err);
  };
}

export function disconnectWebSocket() {
  if (reconnectTimer) clearTimeout(reconnectTimer);
  if (ws) ws.close();
}

export function onMessage(callback) {
  listeners.push(callback);
  return () => {
    listeners = listeners.filter((l) => l !== callback);
  };
}

function notify(msg) {
  for (const listener of listeners) {
    try {
      listener(msg);
    } catch (e) {
      console.error('[WS] Listener error:', e);
    }
  }
}
