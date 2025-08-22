// src/components/EventList.jsx
import React, { useMemo, useState, useCallback, useEffect } from 'react';
import { WebviewWindow } from '@tauri-apps/api/webviewWindow';

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

export default function EventList({ events, setEvents, save }) {
  const [selectedId, setSelectedId] = useState(null);
  const [menu, setMenu] = useState({ open: false, x: 0, y: 0, targetId: null });

  const rows = useMemo(
    () =>
      (events || []).map((ev) => ({
        id: ev.id,
        name: ev.name || 'Untitled',
        date: ev.date || '',
        participants: getParticipantCount(ev),
        raw: ev,
      })),
    [events]
  );

  // Close context menu on click/esc/resize/scroll
  useEffect(() => {
    const close = () => setMenu((m) => ({ ...m, open: false }));
    const onKey = (e) => { if (e.key === 'Escape') close(); };
    window.addEventListener('click', close);
    window.addEventListener('blur', close);
    window.addEventListener('resize', close);
    window.addEventListener('scroll', close, true);
    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('click', close);
      window.removeEventListener('blur', close);
      window.removeEventListener('resize', close);
      window.removeEventListener('scroll', close, true);
      window.removeEventListener('keydown', onKey);
    };
  }, []);

  const openEventWindow = useCallback((ev) => {
    const label = `event-${ev.id}`;

    // If already open, focus + fullscreen it.
    const existing = WebviewWindow.getByLabel?.(label);
    if (existing) {
      existing.setFocus();
      existing.setFullscreen(true);
      return;
    }

    // Create new window and fullscreen once it's created.
    const win = new WebviewWindow(label, {
      url: 'index.html',
      title: ev.name ? `Event • ${ev.name}` : 'Event',
      visible: true,
      // Some runtimes also respect { fullscreen: true }, but we set it after creation for reliability.
    });
    win.once('tauri://created', () => {
      win.setFullscreen(true);
      win.setFocus();
    });
    // Optional:
    // win.once('tauri://error', (e) => console.error('Failed to open event window', e));
  }, []);

  const onRowContextMenu = useCallback((e, id) => {
    e.preventDefault();
    setMenu({ open: true, x: e.clientX, y: e.clientY, targetId: id });
  }, []);

  const handleDelete = useCallback(
    (id) => {
      const ev = (events || []).find((x) => x.id === id);
      if (!ev) return setMenu((m) => ({ ...m, open: false }));
      const count = getParticipantCount(ev);
      if (count > 0) {
        const ok = confirm('Are you sure you want to delete this event?');
        if (!ok) return;
      }
      const next = (events || []).filter((e) => e.id !== id);
      setEvents(next);
      save(next); // Storage.setEvents -> broadcasts; listeners reload
      setMenu((m) => ({ ...m, open: false }));
      if (selectedId === id) setSelectedId(null);
    },
    [events, save, setEvents, selectedId]
  );

  return (
    <div className="p-4 bg-white rounded-2xl shadow">
      <table className="basic-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th className="th">Event</th>
            <th className="th">Date</th>
            <th className="th" style={{ textAlign: 'right' }}>Participants</th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td className="td" colSpan={3} style={{ textAlign: 'center', color: '#64748b', padding: '1rem' }}>
                No events yet.
              </td>
            </tr>
          ) : (
            rows.map((r) => (
              <tr
                key={r.id}
                className={`tr ${selectedId === r.id ? 'row-selected' : ''}`}
                onClick={() => setSelectedId(r.id)}
                onDoubleClick={() => openEventWindow(r.raw)}
                onContextMenu={(e) => onRowContextMenu(e, r.id)}
                style={{ cursor: 'default' }}
              >
                <td className="td">{r.name}</td>
                <td className="td">{r.date || '—'}</td>
                <td className="td" style={{ textAlign: 'right' }}>{r.participants}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {menu.open && (
        <ul
          className="ctxmenu"
          style={{ left: menu.x, top: menu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          <li className="ctxitem" onClick={() => handleDelete(menu.targetId)}>Delete Event</li>
        </ul>
      )}
    </div>
  );
}
