import React, { useState, useRef, useCallback } from 'react';

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg className="drop-zone-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

export default function CreateStoryModal({ isOpen, onClose, onUpload, uploading }) {
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const file = e.dataTransfer?.files?.[0];
    if (file && file.type.startsWith('image/')) {
      onUpload(file);
    }
  }, [onUpload]);

  const handleFileSelect = useCallback((e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(file);
    }
    e.target.value = '';
  }, [onUpload]);

  if (!isOpen) return null;

  return (
    <div className="overlay-backdrop" onClick={!uploading ? onClose : undefined} id="create-story-overlay">
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create New Story</h2>
          {!uploading && (
            <button className="modal-close" onClick={onClose} id="create-story-close">
              <CloseIcon />
            </button>
          )}
        </div>

        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/heic,image/webp"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="story-file-input"
        />

        {uploading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', padding: '40px 0' }}>
            <div className="loading-spinner loading-spinner--brand" />
            <p className="body-md" style={{ color: 'var(--on-surface-variant)' }}>Uploading your story...</p>
          </div>
        ) : (
          <>
            <div
              className={`drop-zone ${dragActive ? 'drop-zone--active' : ''}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              id="story-drop-zone"
            >
              <UploadIcon />
              <span className="drop-zone-text">Drag and drop your photo here</span>
              <span className="drop-zone-sub">Supports JPG, PNG, HEIC</span>
            </div>

            <button
              className="btn btn--secondary btn--full"
              onClick={() => fileInputRef.current?.click()}
              style={{ marginTop: '16px' }}
              id="story-select-file-btn"
            >
              Select from file
            </button>
          </>
        )}

        <p className="body-sm" style={{ color: 'var(--on-surface-variant)', textAlign: 'center', marginTop: '16px' }}>
          Your stories will be visible to your friends for 24 hours.
        </p>
      </div>
    </div>
  );
}
