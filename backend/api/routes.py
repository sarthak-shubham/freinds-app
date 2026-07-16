from fastapi import APIRouter, Header, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List
import crud

router = APIRouter()

class FriendAction(BaseModel):
    member_id: str

class BatchFriendsAction(BaseModel):
    member_ids: List[str]

# ==========================================
# USER ENDPOINTS
# ==========================================

@router.get("/users", summary="List All Users", description="Fetches all seeded users in the database. Use this to grab UUIDs for testing cross-account RLS policies.")
def list_users():
    """Returns all seeded users for the account selector."""
    try:
        users = crud.get_all_users()
        return {"success": True, "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/users/me", summary="Get Current User", description="Fetches the profile of the user currently authenticated via the `userEmail` header.")
def get_current_user(user_email: str = Header(...)):
    """Returns the current user's profile."""
    try:
        client = crud.login_as(user_email)
        user_id = crud.get_user_id(client)
        users = crud.get_all_users()
        me = next((u for u in users if u["id"] == user_id), None)
        if not me:
            raise HTTPException(status_code=404, detail="User not found")
        return {"success": True, "user": me}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# ==========================================
# STORY ENDPOINTS
# ==========================================

@router.get("/stories/feed", summary="Get Story Feed", description="Fetches all active stories. **Security Note:** Supabase RLS automatically filters this list so the authenticated user only sees stories from users who have added them to their Close Friends list.")
def get_feed(user_email: str = Header(...)):
    """Returns all stories visible to the authenticated user."""
    try:
        client = crud.login_as(user_email)
        res = crud.get_visible_stories(client)
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post(
    "/stories", 
    summary="Post a New Story", 
    description="Uploads a new story. **Testing Note:** To test RLS security, try passing `isha@example.com` in the header, but attach Rahul's UUID to the payload. RLS will reject it.",
    responses={
        200: {"description": "Story successfully created."},
        400: {"description": "Bad Request or RLS violation prevented the insert."}
    }
)
async def create_story(file: UploadFile = File(...), user_email: str = Header(...)):
    """Receives physical file and saves story."""
    try:
        client = crud.login_as(user_email)
        file_bytes = await file.read()
        res = crud.create_story_with_file(client, file_bytes, file.filename)
        
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed or upload error")

@router.get(
    "/stories/{target_owner_id}", 
    summary="View a Specific Story", 
    description="Attempts to generate a signed viewing URL for a specific user's story.",
    responses={
        200: {"description": "Successfully generated viewing URL."},
        403: {"description": "Access Denied by RLS. You are not on this user's Close Friends list."}
    }
)
def get_story(target_owner_id: str, user_email: str = Header(...)):
    """Downloads secure viewing URL."""
    try:
        client = crud.login_as(user_email)
        res = crud.download_story_image(client, target_owner_id)
        if not res["success"]:
            raise HTTPException(status_code=403, detail=res.get("message", res.get("error", "Access denied")))
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.delete(
    "/stories",
    summary="Delete Story",
    description="Deletes the acting user's active story.",
    responses={
        200: {"description": "Story deleted successfully."},
        400: {"description": "Failed to delete story."}
    }
)
def delete_story(user_email: str = Header(...)):
    """Deletes the acting user's story."""
    try:
        client = crud.login_as(user_email)
        res = crud.delete_story(client)
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

# ==========================================
# CLOSE FRIENDS ENDPOINTS
# ==========================================

@router.get(
    "/close-friends",
    summary="Get Close Friends",
    description="Returns the current user's close friends list."
)
def get_close_friends(user_email: str = Header(...)):
    """Returns the current user's close friends list."""
    try:
        client = crud.login_as(user_email)
        res = crud.get_close_friends_list(client)
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post(
    "/close-friends",
    summary="Add Close Friend",
    description="Adds a user to the close friends list.",
    responses={
        200: {"description": "Friend added successfully."},
        400: {"description": "Failed to add friend."}
    }
)
def add_friend(payload: FriendAction, user_email: str = Header(...)):
    """Adds a user to the close friends list."""
    try:
        client = crud.login_as(user_email)
        res = crud.add_close_friend(client, payload.member_id)
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.put(
    "/close-friends/batch", 
    summary="Update Close Friends List", 
    description="Replaces the entire close friends list atomically for the authenticated user. **Security Note:** The database enforces that you can only modify your own close friends list.",
    responses={
        200: {"description": "Close friends list updated successfully."},
        400: {"description": "RLS blocked the transaction. You cannot modify someone else's list."}
    }
)
def batch_update_friends(payload: BatchFriendsAction, user_email: str = Header(...)):
    """Replaces the entire close friends list atomically."""
    try:
        client = crud.login_as(user_email)
        res = crud.batch_update_close_friends(client, payload.member_ids)
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.delete(
    "/close-friends/{member_id}",
    summary="Remove Close Friend",
    description="Removes a user from the close friends list.",
    responses={
        200: {"description": "Friend removed successfully."},
        400: {"description": "Failed to remove friend."}
    }
)
def remove_friend(member_id: str, user_email: str = Header(...)):
    """Removes a user from the close friends list."""
    try:
        client = crud.login_as(user_email)
        res = crud.remove_close_friend(client, member_id)
        if not res["success"]:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")