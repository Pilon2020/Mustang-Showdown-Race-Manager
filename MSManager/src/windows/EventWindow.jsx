// src/windows/EventWindow.jsx
import React, { useEffect, useMemo, useState } from 'react';
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';
import { listen } from '@tauri-apps/api/event';
import { Storage } from '../lib/storage.js';

function getParticipantCount(ev) {
  if (typeof ev?.participantCount === 'number') return ev.participantCount;
  if (Array.isArray(ev?.participants)) return ev.participants.length;
  if (Array.isArray(ev?.heats)) {
    return ev.heats.reduce((acc, h) => {
      const list = h?.participants || h?.athletes || [];
      return acc + (Array.isArray(list) ? list.length : 0);
    }, 0);
  }
  return 0;
}

export default function EventWindow() {
  const [eventId, setEventId] = useState(null);
  const [data, setData] = useState({ events: [] });

  // Determine the event id from the window label (event-<id>) or ?eventId=…
  useEffect(() => {
    const label = getCurrentWebviewWindow().label;
    const fromLabel = label.startsWith('event-') ? label.slice('event-'.length) : null;
    const fromQuery = new URLSearchParams(location.search).get('eventId');
    setEventId(fromLabel || fromQuery || null);
  }, []);

  // Load + live-reload when storage changes or window refocuses
  useEffect(() => {
    let unlisten;
    const load = async () => setData(await Storage.load());
    load();

    (async () => {
      try {
        unlisten = await listen('events-updated', load);
      } catch {}
    })();

    const onVisible = () => { if (document.visibilityState === 'visible') load(); };
    document.addEventListener('visibilitychange', onVisible);
    return () => { unlisten && unlisten(); document.removeEventListener('visibilitychange', onVisible); };
  }, []);

  const ev = useMemo(
    () => data.events.find(e => e.id === eventId),
    [data.events, eventId]
  );

  if (!eventId) {
    return <div className="p-6">No event id.</div>;
  }
  if (!ev) {
    return <div className="p-6">Event not found.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
          {ev.name || 'Untitled Event'}
        </h1>
        <div className="text-slate-600">
          {ev.date || 'No date'} {ev.location ? `• ${ev.location}` : null}
        </div>
      </header>

      <section className="p-4 bg-white rounded-2xl shadow">
        <div className="text-sm text-slate-600">
          Participants: <strong>{getParticipantCount(ev)}</strong>
        </div>
        {/* Add whatever detail UI you want here: heats, assignments, etc. */}
      </section>
    </div>
  );
}
