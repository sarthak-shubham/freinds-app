import React, { useState, useEffect, useRef, useCallback } from 'react';
import ConfirmDialog from './ConfirmDialog';
import Tooltip from './Tooltip';
import { stringToColor } from '../utils';

function TrashIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
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

function formatTimeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function StoryViewer({ story, isOwnStory, onClose, onDelete }) {
  const [progress, setProgress] = useState(0);
  const [holding, setHolding] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const progressRef = useRef(0);
  const intervalRef = useRef(null);

  const DURATION = 5000;
  const INTERVAL = 50;
  const STEP = (INTERVAL / DURATION) * 100;

  const startProgress = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    intervalRef.current = setInterval(() => {
      progressRef.current += STEP;
      if (progressRef.current >= 100) {
        clearInterval(intervalRef.current);
        progressRef.current = 100;
        setProgress(100);
        // Auto-close after slight delay
        setTimeout(() => onClose(), 100);
        return;
      }
      setProgress(progressRef.current);
    }, INTERVAL);
  }, [onClose, STEP]);

  const pauseProgress = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  // Start progress on mount
  useEffect(() => {
    if (!story || confirmOpen) return;
    progressRef.current = 0;
    setProgress(0);
    startProgress();
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [story, confirmOpen, startProgress]);

  // Handle hold
  const handleHoldStart = useCallback((e) => {
    // Don't trigger on button clicks
    if (e.target.closest('button')) return;
    e.preventDefault();
    setHolding(true);
    pauseProgress();
  }, [pauseProgress]);

  const handleHoldEnd = useCallback(() => {
    if (!holding) return;
    setHolding(false);
    startProgress();
  }, [holding, startProgress]);

  // Attach touch/mouse listeners
  useEffect(() => {
    if (!story) return;
    
    const handleMouseUp = () => handleHoldEnd();
    const handleTouchEnd = () => handleHoldEnd();

    window.addEventListener('mouseup', handleMouseUp);
    window.addEventListener('touchend', handleTouchEnd);
    window.addEventListener('touchcancel', handleTouchEnd);

    return () => {
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('touchend', handleTouchEnd);
      window.removeEventListener('touchcancel', handleTouchEnd);
    };
  }, [story, handleHoldEnd]);

  const handleDelete = async () => {
    setDeleting(true);
    try {
      await onDelete();
    } finally {
      setDeleting(false);
      setConfirmOpen(false);
    }
  };

  if (!story) return null;

  return (
    <div
      className={`story-viewer ${holding ? 'story-viewer--holding' : ''}`}
      onMouseDown={handleHoldStart}
      onTouchStart={handleHoldStart}
      id="story-viewer"
    >
      {/* Progress bar */}
      <div className="story-viewer-progress">
        <div className="story-viewer-progress-track">
          <div
            className="story-viewer-progress-fill"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Header */}
      <div className="story-viewer-header">
        <div className="story-viewer-user">
          <div className="account-avatar account-avatar--sm" style={{ backgroundColor: stringToColor(story.owner_name), color: '#fff' }}>
            {story.owner_name?.charAt(0).toUpperCase()}
          </div>
          <span className="story-viewer-name">
            {isOwnStory ? 'You' : story.owner_name}
          </span>
          <span className="story-viewer-time">{formatTimeAgo(story.created_at)}</span>
        </div>

        <div className="story-viewer-actions">
          {isOwnStory && (
            <Tooltip label="Delete story">
              <button
                className="story-viewer-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  pauseProgress();
                  setConfirmOpen(true);
                }}
                id="story-delete-btn"
              >
                <TrashIcon />
              </button>
            </Tooltip>
          )}
          <button
            className="story-viewer-btn"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            id="story-close-btn"
          >
            <CloseIcon />
          </button>
        </div>
      </div>

      {/* Image */}
      <div className="story-viewer-image">
        {story.image_url ? (
          <img src={story.image_url} alt={`${story.owner_name}'s story`} draggable={false} />
        ) : (
          <div className="loading-spinner" style={{ borderTopColor: '#fff', borderColor: 'rgba(255,255,255,0.3)' }} />
        )}
      </div>

      {/* Delete confirmation */}
      <ConfirmDialog
        isOpen={confirmOpen}
        title="Delete Story?"
        message="This will permanently remove your story for everyone."
        confirmLabel={deleting ? "Deleting..." : "Delete"}
        confirmVariant="danger"
        onConfirm={handleDelete}
        onCancel={() => {
          setConfirmOpen(false);
          startProgress();
        }}
      />
    </div>
  );
}