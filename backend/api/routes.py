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

@router.get("/users", summary="List All Users", description="Fetches all seeded users in the database. Use this to grab UUIDs for testing cross-account RLS policies. No authentication headers required.")
def list_users():
    """Returns all seeded users for the account selector."""
    try:
        users = crud.get_all_users()
        return {"success": True, "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/users/me", summary="Get Current User", description="Fetches the profile of the user currently authenticated via the `userEmail` header. **Testing Note:** Pass your email in the `userEmail` header.")
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

@router.get("/stories/feed", summary="Get Story Feed", description="Fetches all active stories. **Security Note:** Supabase RLS automatically filters this list so the authenticated user only sees stories from users who have added them to their Close Friends list. **Testing Note:** Pass your email in the `userEmail` header.")
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
    description="Uploads a new story for the authenticated user. **Testing Note:** Pass the user's email in the `userEmail` header (e.g. `isha@example.com`), and provide an image file in the `multipart/form-data` payload under the `file` key. The database RLS policies ensure the story is securely created under that user's identity.",
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
    description="Attempts to generate a signed viewing URL for a specific user's story. **Testing Note:** Pass your email in the `userEmail` header, and place the target user's UUID in the `target_owner_id` URL path parameter. RLS will block access if you aren't on their list.",
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
    description="Deletes the acting user's active story. **Testing Note:** Pass your email in the `userEmail` header.",
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
    description="Returns the current user's close friends list. **Testing Note:** Pass your email in the `userEmail` header."
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
    description="Adds a user to your close friends list. **Testing Note:** Pass your email in the `userEmail` header. Provide the UUID of the user you want to add in the JSON payload under the `member_id` key. Example JSON body: `{\"member_id\": \"uuid-goes-here\"}`.",
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
    description="Replaces the entire close friends list atomically. **Testing Note:** Pass your email in the `userEmail` header. Provide an array of UUIDs in the JSON payload under the `member_ids` key. Example JSON body: `{\"member_ids\": [\"uuid-1\", \"uuid-2\"]}`.",
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
    description="Removes a user from the close friends list. **Testing Note:** Pass your email in the `userEmail` header, and place the target user's UUID in the `member_id` URL path parameter.",
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