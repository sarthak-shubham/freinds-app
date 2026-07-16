import React from 'react';

export default function ConfirmDialog({ isOpen, title, message, confirmLabel, confirmVariant, onConfirm, onCancel }) {
  if (!isOpen) return null;

  return (
    <div className="overlay-backdrop" onClick={onCancel} id="confirm-dialog-overlay">
      <div className="modal-content confirm-dialog" onClick={e => e.stopPropagation()}>
        <h3 className="confirm-dialog-title">{title}</h3>
        <p className="confirm-dialog-message">{message}</p>
        <div className="confirm-dialog-actions">
          <button
            className="btn btn--outline"
            onClick={onCancel}
            style={{ flex: 1 }}
            id="confirm-cancel-btn"
          >
            Cancel
          </button>
          <button
            className={`btn ${confirmVariant === 'danger' ? 'btn--danger' : 'btn--primary'}`}
            onClick={onConfirm}
            style={{ flex: 1 }}
            id="confirm-action-btn"
          >
            {confirmLabel || 'Confirm'}
          </button>
        </div>
      </div>
    </div>
  );
}
