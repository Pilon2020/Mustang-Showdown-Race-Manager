// src/App.jsx
import React, { useEffect, useRef, useState } from 'react';
// import EventForm from './components/EventForm.jsx';
import EventList from './components/EventList.jsx';
import { Storage } from './lib/storage.js';

// Tauri event helper
import { listen } from '@tauri-apps/api/event';

export default function App() {
  const [events, setEvents] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const formRef = useRef(null);

  useEffect(() => {
    (async () => {
      const data = await Storage.load();
      setEvents(data.events || []);
      setLoaded(true);
    })();
  }, []);

  async function save(nextEvents) {
    await Storage.save({ events: nextEvents });
  }

  function createEvent(e) {
    const next = [...events, e];
    setEvents(next); save(next);
  }

  // Listen for File → New Event… or ⌘N
  useEffect(() => {
    let unlisten;
    (async () => {
      unlisten = await listen('menu://new-event', () => {
        // Option A: just focus the form
        formRef.current?.focus();

        // Option B (optional): prefill something
        // formRef.current?.prefill({ name: '', date: '', location: '' });
      });
    })();
    return () => { if (unlisten) unlisten(); };
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Tri Heats</h1>
      </header>

      {/* <EventForm ref={formRef} onCreate={createEvent} /> */}
      <EventList events={events} setEvents={setEvents} save={save} />

    </div>
  );
}
