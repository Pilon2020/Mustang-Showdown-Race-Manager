// src/lib/storage.js
// Unified storage: localStorage on web; JSON file in Tauri desktop
let isTauri = false;
try { isTauri = !!window.__TAURI__; } catch (_) {}

const KEY = 'tri-heats:data';

async function readFile() {
  const { readTextFile, BaseDirectory } = await window.__TAURI__.fs;
  try {
    const txt = await readTextFile('data.json', { dir: BaseDirectory.AppData });
    return JSON.parse(txt);
  } catch {
    return { events: [] };
  }
}

async function writeFile(data) {
  const { writeTextFile, BaseDirectory, createDir, exists } = await window.__TAURI__.fs;
  try {
    const has = await exists('', { dir: BaseDirectory.AppData });
    if (!has) await createDir('', { dir: BaseDirectory.AppData, recursive: true });
  } catch {}
  await writeTextFile('data.json', JSON.stringify(data, null, 2), { dir: BaseDirectory.AppData });
}

// ---- NEW: broadcast that events were updated (works in Tauri and web) ----
async function notifyUpdated(payload = {}) {
  try {
    if (isTauri) {
      // Tauri app-wide event
      const { emit } = await import('@tauri-apps/api/event');
      await emit('events-updated', payload);
    } else if (typeof BroadcastChannel !== 'undefined') {
      // Multi-window/webview broadcast
      const ch = new BroadcastChannel('tri-heats');
      ch.postMessage({ type: 'events-updated', ...payload });
      ch.close();
    } else {
      // Fallback same-window custom event
      window.dispatchEvent(new CustomEvent('events-updated', { detail: payload }));
    }
  } catch (_) {
    // best-effort: ignore
  }
}

export const Storage = {
  async load() {
    if (isTauri) return await readFile();
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : { events: [] };
  },

  async save(data, meta = {}) {
    if (isTauri) {
      await writeFile(data);
    } else {
      localStorage.setItem(KEY, JSON.stringify(data));
    }
    await notifyUpdated({ reason: 'save', ...meta });
  },

  // Append a single event and persist (broadcasts automatically)
  async addEvent(ev) {
    const data = await this.load();
    const events = Array.isArray(data?.events) ? data.events : [];
    const next = { events: [...events, ev] };
    await this.save(next, { reason: 'add', id: ev?.id });
    return next.events;
  },

  // Replace all events (broadcasts automatically)
  async setEvents(events) {
    const next = { events: events ?? [] };
    await this.save(next, { reason: 'set' });
    return next.events;
  }
};
