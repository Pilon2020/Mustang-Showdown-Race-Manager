// src/windows/NewEventWindow.jsx
import React, { useRef } from 'react';
import EventForm from '../components/EventForm.jsx';
import { Storage } from '../lib/storage.js';
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';

export default function NewEventWindow() {
  const formRef = useRef(null);

  async function handleCreate(ev) {
    await Storage.addEvent(ev);                 // <--- broadcasts internally
    await getCurrentWebviewWindow().close();
  }

  return (
    <div className="max-w-xl mx-auto p-4">
      <EventForm ref={formRef} onCreate={handleCreate} />
    </div>
  );
}
