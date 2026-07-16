import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import LoadingOverlay from '../components/LoadingOverlay';
import useSWR from 'swr';function ArrowLeftIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="19" y1="12" x2="5" y2="12" />
      <polyline points="12 19 5 12 12 5" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="11" cy="11" r="8" />
      <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </svg>
  );
}

function Switch({ checked, onChange }) {
  return (
    <div
      className={`toggle ${checked ? 'toggle--active' : ''}`}
      onClick={(e) => {
        e.stopPropagation();
        onChange(!checked);
      }}
    >
      <div className="toggle-knob" />
    </div>
  );
}

export default function CloseFriendsPage() {
  const navigate = useNavigate();
  const { allUsers, currentUser } = useAuth();
  const [initialFriends, setInitialFriends] = useState(new Set());
  const [currentFriends, setCurrentFriends] = useState(new Set());
  const [searchQuery, setSearchQuery] = useState('');
  const { data: res, error, mutate: reloadFriends } = useSWR(
    currentUser ? `/api/close-friends?email=${currentUser.email}` : null,
    () => api.getCloseFriends(currentUser.email),
    { revalidateOnFocus: true }
  );

  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (res?.member_ids) {
      const friendsSet = new Set(res.member_ids);
      setInitialFriends(friendsSet);
      setCurrentFriends(new Set(friendsSet));
    }
  }, [res]);

  const loading = !res && !error;

  // Filter out the current user, then filter by search query
  const displayUsers = useMemo(() => {
    if (!currentUser || !allUsers) return [];
    let users = allUsers.filter(u => u.id !== currentUser.id);
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      users = users.filter(u => u.name.toLowerCase().includes(q));
    }
    return users;
  }, [allUsers, currentUser, searchQuery]);

  const toggleFriend = useCallback((userId) => {
    setCurrentFriends(prev => {
      const next = new Set(prev);
      if (next.has(userId)) {
        next.delete(userId);
      } else {
        next.add(userId);
      }
      return next;
    });
  }, []);

  const handleSaveAndExit = async () => {
    // Calculate if there are differences
    const initialArr = Array.from(initialFriends);
    const currentArr = Array.from(currentFriends);
    
    // Sort to compare easily, or just check sets
    let hasChanges = initialArr.length !== currentArr.length;
    if (!hasChanges) {
      for (const id of currentArr) {
        if (!initialFriends.has(id)) {
          hasChanges = true;
          break;
        }
      }
    }

    if (!hasChanges) {
      navigate('/');
      return;
    }

    setSaving(true);
    try {
      await api.batchUpdateCloseFriends(currentArr, currentUser.email);
      await reloadFriends(); // Update the cache
      navigate('/');
    } catch (err) {
      alert('Failed to save close friends: ' + err.message);
      setSaving(false);
    }
  };

  return (
    <div className="cf-page">
      <header className="cf-page-header">
        <button className="cf-back-btn" onClick={handleSaveAndExit}>
          <ArrowLeftIcon />
        </button>
        <h1 className="cf-page-title">Close Friends</h1>
      </header>

      <div className="cf-page-body">
        <div className="search-wrapper">
          <SearchIcon />
          <input
            type="text"
            className="search-input"
            placeholder="Search"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>

        {loading ? (
          <div className="p-5 text-center">
            <div className="loading-spinner loading-spinner--brand mx-auto" />
          </div>
        ) : displayUsers.length === 0 ? (
          <div className="text-center p-5 text-variant py-10">
            No users found
          </div>
        ) : (
          <div className="cf-friends-list">
            {displayUsers.map(user => (
              <div key={user.id} className="friend-item" onClick={() => toggleFriend(user.id)}>
                <div className="friend-item-info">
                  <div className="account-avatar">
                    {user.name.charAt(0).toUpperCase()}
                  </div>
                  <span className="friend-item-name">{user.name}</span>
                </div>
                <Switch checked={currentFriends.has(user.id)} onChange={() => toggleFriend(user.id)} />
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="cf-page-footer">
        <button className="btn btn--primary btn--full btn--lg" onClick={handleSaveAndExit}>
          Done
        </button>
      </div>

      <LoadingOverlay visible={saving} />
    </div>
  );
}
