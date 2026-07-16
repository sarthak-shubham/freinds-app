import React from 'react';
import { useAuth } from '../context/AuthContext';

function CheckIcon() {
  return (
    <svg className="account-list-check" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export default function AccountSelector({ isOpen, onClose, onSwitch }) {
  const { allUsers, currentUser } = useAuth();

  if (!isOpen) return null;

  const handleSelect = (user) => {
    if (user.id !== currentUser?.id) {
      onSwitch(user);
    }
    onClose();
  };

  return (
    <div className="overlay-backdrop overlay-backdrop--bottom" onClick={onClose} id="account-selector-overlay">
      <div className="modal-content modal-content--bottom" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Switch Account</h2>
          <button className="modal-close" onClick={onClose} id="account-selector-close">
            <CloseIcon />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {allUsers.map(user => {
            const isActive = currentUser?.id === user.id;
            return (
              <button
                key={user.id}
                className={`account-list-item ${isActive ? 'account-list-item--active' : ''}`}
                onClick={() => handleSelect(user)}
                id={`account-select-${user.id}`}
              >
                <div className="account-avatar">
                  {user.name.charAt(0).toUpperCase()}
                </div>
                <div className="account-list-detail">
                  <span className="account-list-name">{user.name}</span>
                  <span className="account-list-email">{user.email}</span>
                </div>
                {isActive && <CheckIcon />}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
