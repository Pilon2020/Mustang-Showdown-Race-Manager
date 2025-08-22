// src/Root.jsx
import React, { useEffect, useState } from 'react';
import { getCurrentWebviewWindow } from '@tauri-apps/api/webviewWindow';
import MainWindow from './windows/MainWindow.jsx';
import NewEventWindow from './windows/NewEventWindow.jsx';

export default function Root() {
  const [label, setLabel] = useState('main');
  useEffect(() => {
    setLabel(getCurrentWebviewWindow().label);
  }, []);
  if (label === 'new-event') return <NewEventWindow />;
  return <MainWindow />;
}
