import React from 'react';

export function StoryCircleSkeleton() {
  return (
    <div className="story-circle-item">
      <div className="skeleton skeleton-circle" style={{ width: 64, height: 64 }} />
      <div className="skeleton skeleton-text" style={{ width: 48 }} />
    </div>
  );
}

export function StoryCardSkeleton() {
  return (
    <div className="story-card" style={{ pointerEvents: 'none' }}>
      <div className="skeleton" style={{ width: '100%', aspectRatio: '3 / 4' }} />
      <div className="story-card-footer">
        <div className="story-card-info">
          <div className="skeleton skeleton-text" style={{ width: 80 }} />
          <div className="skeleton skeleton-text skeleton-text--sm" style={{ width: 56, marginTop: 4 }} />
        </div>
      </div>
    </div>
  );
}

export function FeedSkeleton() {
  return (
    <>
      <div className="story-circles">
        <StoryCircleSkeleton />
        <StoryCircleSkeleton />
        <StoryCircleSkeleton />
      </div>
      <div className="section-header">
        <div className="skeleton skeleton-text" style={{ width: 60 }} />
      </div>
      <div className="story-feed">
        <StoryCardSkeleton />
      </div>
    </>
  );
}
