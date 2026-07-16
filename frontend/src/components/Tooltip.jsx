import React from 'react';

export default function Tooltip({ label, children, position = 'top' }) {
  return (
    <div className={`tooltip-wrapper tooltip-wrapper--${position}`}>
      {children}
      <span className="tooltip-text">{label}</span>
    </div>
  );
}
