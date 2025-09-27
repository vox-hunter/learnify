import React from 'react';
import ReactDOM from 'react-dom/client';
import FillInTheBlanks from './FillInTheBlanks';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <FillInTheBlanks />
  </React.StrictMode>
);
