// src/components/EventForm.jsx
import React, { useState, forwardRef, useImperativeHandle, useRef } from 'react';

const EventForm = forwardRef(function EventForm({ onCreate }, ref) {
  const [name, setName] = useState('');
  const [date, setDate] = useState('');
  const [location, setLocation] = useState('');
  const nameRef = useRef(null);

  useImperativeHandle(ref, () => ({
    focus() {
      nameRef.current?.focus();
    },
    // optional: prefill
    prefill(values = {}) {
      if (values.name !== undefined) setName(values.name);
      if (values.date !== undefined) setDate(values.date);
      if (values.location !== undefined) setLocation(values.location);
      nameRef.current?.focus();
    }
  }));

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!name.trim()) return;
        onCreate({ id: crypto.randomUUID(), name, date, location, heats: [] });
        setName(''); setDate(''); setLocation('');
      }}
      className="flex flex-col gap-3 p-4 bg-white rounded-2xl shadow"
    >
      <h3 className="text-lg font-semibold mb-2">Create Event</h3>
      <div className="form-row">
        <input
          ref={nameRef}
          className="input"
          placeholder="Event name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="input"
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
        />
        <button className="btn-primary" type="submit">Add Event</button>
      </div>
    </form>
  );
});

export default EventForm;
