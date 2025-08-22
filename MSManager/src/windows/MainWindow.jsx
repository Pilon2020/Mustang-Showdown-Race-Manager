// src/windows/MainWindow.jsx
import React, { useEffect, useState } from 'react';
import EventList from '../components/EventList.jsx';
import { Storage } from '../lib/storage.js';
import { listen } from '@tauri-apps/api/event';

export default function MainWindow() {
  const [events, setEvents] = useState([]);
  const [loaded, setLoaded] = useState(false);

  // initial load
  useEffect(() => {
    (async () => {
      const data = await Storage.load();
      setEvents(data.events || []);
      setLoaded(true);
    })();
  }, []);

  // one function to refresh
  const refresh = async () => {
    const data = await Storage.load();
    setEvents(data.events || []);
  };

  // live updates from:
  //  - tauri emit('events-updated')
  //  - BroadcastChannel 'tri-heats'
  //  - window CustomEvent('events-updated')
  //  - visibility/focus (safety net)
  useEffect(() => {
    let unlistenTauri;
    let bc;

    (async () => {
      try {
        unlistenTauri = await listen('events-updated', refresh);
      } catch { /* not in Tauri in web */ }
    })();

    if (typeof BroadcastChannel !== 'undefined') {
      bc = new BroadcastChannel('tri-heats');
      bc.onmessage = (msg) => {
        if (msg?.data?.type === 'events-updated') refresh();
      };
    }

    const onDomEvent = () => refresh();
    const onVisibility = () => {
      if (document.visibilityState === 'visible') refresh();
    };

    window.addEventListener('events-updated', onDomEvent);
    document.addEventListener('visibilitychange', onVisibility);

    return () => {
      unlistenTauri && unlistenTauri();
      bc && bc.close();
      window.removeEventListener('events-updated', onDomEvent);
      document.removeEventListener('visibilitychange', onVisibility);
    };
  }, []);

  // keep inline edits working (rename/delete via context menu)
  async function save(nextEvents) {
    await Storage.setEvents(nextEvents); // broadcasts internally
    setEvents(nextEvents);
  }

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Tri Heats</h1>
      </header>

      <EventList events={events} setEvents={setEvents} save={save} />

    </div>
  );
}
