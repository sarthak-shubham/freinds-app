import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { FeedSkeleton } from '../components/SkeletonLoader';
import StoryViewer from '../components/StoryViewer';
import CreateStoryModal from '../components/CreateStoryModal';
import AccountSelector from '../components/AccountSelector';
import LoadingOverlay from '../components/LoadingOverlay';
import Tooltip from '../components/Tooltip';
import ConfirmDialog from '../components/ConfirmDialog';

import useSWR from 'swr';

function PlusIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="5" x2="12" y2="19" />
      <line x1="5" y1="12" x2="19" y2="12" />
    </svg>
  );
}

function ChevronDown() {
  return (
    <svg className="chevron-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="6 9 12 15 18 9" />
    </svg>
  );
}

function MoreVertIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
      <circle cx="12" cy="5" r="1.5" />
      <circle cx="12" cy="12" r="1.5" />
      <circle cx="12" cy="19" r="1.5" />
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
  if (hours < 24) return `${hours} hours ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export default function HomePage() {
  const { currentUser, switchUser } = useAuth();

  const [uploading, setUploading] = useState(false);
  const [switchingAccount, setSwitchingAccount] = useState(false);

  // UI state
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [accountSelectorOpen, setAccountSelectorOpen] = useState(false);
  const [viewingStory, setViewingStory] = useState(null);
  const [deleteConfirm, setDeleteConfirm] = useState(null); // story to delete from feed

  // Fetch feed with SWR for caching and fast UX
  const { data: res, error, mutate: reloadFeed } = useSWR(
    currentUser ? `/api/stories/feed?email=${currentUser.email}` : null,
    () => api.getFeed(currentUser.email),
    {
      revalidateOnFocus: true,
      dedupingInterval: 5000,
    }
  );

  const feedLoading = !res && !error;
  const stories = res?.stories || [];

  // Derived data
  const myStory = stories.find(s => s.owner_id === currentUser?.id);
  const otherStories = stories.filter(s => s.owner_id !== currentUser?.id);

  // Unique story owners for circles (other than self)
  const storyOwnerCircles = otherStories.reduce((acc, s) => {
    if (!acc.find(x => x.owner_id === s.owner_id)) {
      acc.push(s);
    }
    return acc;
  }, []);

  // Upload story
  const handleUpload = async (file) => {
    setUploading(true);
    try {
      await api.createStory(file, currentUser.email);
      setCreateModalOpen(false);
      await reloadFeed();
    } catch (err) {
      alert('Failed to upload: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  // Delete story
  const handleDeleteStory = async () => {
    try {
      await api.deleteStory(currentUser.email);
      setViewingStory(null);
      await reloadFeed();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  // Delete from feed card menu
  const handleDeleteFromFeed = async () => {
    if (!deleteConfirm) return;
    try {
      await api.deleteStory(currentUser.email);
      setDeleteConfirm(null);
      await reloadFeed();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  // Account switch
  const handleAccountSwitch = async (user) => {
    setSwitchingAccount(true);
    switchUser(user);
    // Small delay to let context update propagate
    setTimeout(() => setSwitchingAccount(false), 300);
  };

  // Open story
  const handleOpenStory = (story) => {
    setViewingStory(story);
  };

  return (
    <>
      {/* Header */}
      <header className="page-header" id="home-header">
        <div className="page-header-left">
          <Tooltip label="Add story" position="bottom">
            <button
              className="icon-btn"
              onClick={() => setCreateModalOpen(true)}
              id="add-story-btn"
            >
              <PlusIcon />
            </button>
          </Tooltip>
        </div>

        <h1 className="page-header-title">FREINDS</h1>

        <div className="page-header-right">
          <Tooltip label="Switch account" position="bottom">
            <button
              className="account-trigger"
              onClick={() => setAccountSelectorOpen(true)}
              id="account-selector-trigger"
            >
              <div className="account-avatar account-avatar--sm">
                {currentUser?.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
              <ChevronDown />
            </button>
          </Tooltip>
        </div>
      </header>

      {/* Content */}
      {feedLoading ? (
        <FeedSkeleton />
      ) : (
        <>
          {/* Story Circles */}
          <div className="story-circles" id="story-circles">
            {/* Your Story */}
            <div className="story-circle-item">
              {myStory ? (
                <div
                  className={`story-ring ${uploading ? 'story-ring--uploading' : ''} ${uploading ? 'story-ring--disabled' : ''}`}
                  onClick={() => !uploading && handleOpenStory(myStory)}
                  id="your-story-ring"
                >
                  <div className="story-ring-inner">
                    <div className="story-ring-avatar">
                      {currentUser?.name?.charAt(0)?.toUpperCase() || '?'}
                    </div>
                  </div>
                </div>
              ) : (
                <div
                  className={`story-ring story-ring--none ${uploading ? 'story-ring--uploading' : ''} ${uploading ? 'story-ring--disabled' : ''}`}
                  onClick={() => !uploading && setCreateModalOpen(true)}
                  style={uploading ? { background: 'var(--brand-gradient)', borderStyle: 'none' } : {}}
                  id="your-story-ring"
                >
                  <div className="story-ring-inner">
                    {uploading ? (
                      <div className="story-ring-avatar">
                        {currentUser?.name?.charAt(0)?.toUpperCase() || '?'}
                      </div>
                    ) : (
                      <div className="story-ring-add">
                        <PlusIcon />
                      </div>
                    )}
                  </div>
                </div>
              )}
              <span className="story-circle-name">
                {myStory ? 'Your Story' : 'Your Story'}
              </span>
            </div>

            {/* Other users' stories */}
            {storyOwnerCircles.map(story => (
              <div key={story.owner_id} className="story-circle-item">
                <div
                  className="story-ring"
                  onClick={() => handleOpenStory(story)}
                  id={`story-ring-${story.owner_id}`}
                >
                  <div className="story-ring-inner">
                    <div className="story-ring-avatar">
                      {story.owner_name?.charAt(0).toUpperCase()}
                    </div>
                  </div>
                </div>
                <span className="story-circle-name">{story.owner_name}</span>
              </div>
            ))}
          </div>

          {/* Stories Section */}
          <div className="section-header">
            <h2 className="section-title">Stories</h2>
          </div>

          {stories.length === 0 ? (
            <div className="empty-state" id="empty-feed">
              <div className="empty-state-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="28" height="28">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
              </div>
              <h3 className="empty-state-title">No stories yet</h3>
              <p className="empty-state-text">
                Be the first to share a moment with your close friends.
              </p>
            </div>
          ) : (
            <div className="story-feed" id="story-feed">
              {stories.map(story => {
                const isOwn = story.owner_id === currentUser?.id;
                return (
                  <div
                    key={story.id}
                    className="story-card"
                    onClick={() => handleOpenStory(story)}
                    id={`story-card-${story.id}`}
                  >
                    <img
                      src={story.image_url}
                      alt={`${story.owner_name}'s story`}
                      className="story-card-image"
                      loading="lazy"
                    />

                    {isOwn && (
                      <Tooltip label="Delete">
                        <button
                          className="story-card-menu"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeleteConfirm(story);
                          }}
                          id={`story-card-menu-${story.id}`}
                        >
                          <MoreVertIcon />
                        </button>
                      </Tooltip>
                    )}

                    <div className="story-card-footer">
                      <div className="story-card-info">
                        <span className="story-card-name">{isOwn ? 'You' : story.owner_name}</span>
                        <span className="story-card-time">{formatTimeAgo(story.created_at)}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      {/* Story Viewer */}
      <StoryViewer
        story={viewingStory}
        isOwnStory={viewingStory?.owner_id === currentUser?.id}
        onClose={() => setViewingStory(null)}
        onDelete={handleDeleteStory}
      />

      {/* Create Story Modal */}
      <CreateStoryModal
        isOpen={createModalOpen}
        onClose={() => setCreateModalOpen(false)}
        onUpload={handleUpload}
        uploading={uploading}
      />

      {/* Account Selector */}
      <AccountSelector
        isOpen={accountSelectorOpen}
        onClose={() => setAccountSelectorOpen(false)}
        onSwitch={handleAccountSwitch}
      />

      {/* Delete Confirm from feed card */}
      <ConfirmDialog
        isOpen={!!deleteConfirm}
        title="Delete Story?"
        message="This will permanently remove your story for everyone."
        confirmLabel="Delete"
        confirmVariant="danger"
        onConfirm={handleDeleteFromFeed}
        onCancel={() => setDeleteConfirm(null)}
      />

      {/* Loading overlay for account switch */}
      <LoadingOverlay visible={switchingAccount} />
    </>
  );
}
