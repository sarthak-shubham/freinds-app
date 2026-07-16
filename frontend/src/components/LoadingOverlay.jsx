import React from 'react';

export default function LoadingOverlay({ visible }) {
  if (!visible) return null;

  return (
    <div className="loading-overlay" id="loading-overlay">
      <div className="loading-spinner" />
    </div>
  );
}
