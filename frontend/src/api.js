// Use VITE_API_URL from environment if available (production), otherwise use local proxy
const API_BASE = import.meta.env.VITE_API_URL || "/api";
async function fetchWithAuth(endpoint, options = {}, userEmail, isFormData = false) {
  const headers = {
    "user-email": userEmail,
    "Bypass-Tunnel-Reminder": "true",
    ...(options.headers || {}),
  };

  // Only set application/json if we are NOT sending a file
  if (!isFormData) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  
  if (!response.ok) {
    let detail = "API Request Failed";
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      // Response wasn't JSON
    }
    throw new Error(detail);
  }
  
  return response.json();
}

export const api = {
  // User endpoints
  getUsers: () => 
    fetch(`${API_BASE}/users`, { headers: { "Bypass-Tunnel-Reminder": "true" } }).then(r => {
      if (!r.ok) throw new Error("Failed to fetch users");
      return r.json();
    }),

  getMe: (userEmail) => 
    fetchWithAuth("/users/me", {}, userEmail),

  // Story endpoints
  getFeed: (userEmail) => 
    fetchWithAuth("/stories/feed", {}, userEmail),

  createStory: (file, userEmail) => {
    const formData = new FormData();
    formData.append("file", file);
    
    return fetchWithAuth("/stories", {
      method: "POST",
      body: formData
    }, userEmail, true);
  },

  getStory: (targetOwnerId, userEmail) => 
    fetchWithAuth(`/stories/${targetOwnerId}`, {}, userEmail),

  deleteStory: (userEmail) => 
    fetchWithAuth("/stories", { method: "DELETE" }, userEmail),

  // Close friends endpoints
  getCloseFriends: (userEmail) => 
    fetchWithAuth("/close-friends", {}, userEmail),

  addCloseFriend: (memberId, userEmail) => 
    fetchWithAuth("/close-friends", {
      method: "POST",
      body: JSON.stringify({ member_id: memberId })
    }, userEmail),

  removeCloseFriend: (memberId, userEmail) => 
    fetchWithAuth(`/close-friends/${memberId}`, { method: "DELETE" }, userEmail),

  batchUpdateCloseFriends: (memberIds, userEmail) => 
    fetchWithAuth("/close-friends/batch", {
      method: "PUT",
      body: JSON.stringify({ member_ids: memberIds })
    }, userEmail),
};