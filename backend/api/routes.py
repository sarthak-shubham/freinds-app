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

@router.get("/users")
def list_users():
    """Returns all seeded users for the account selector."""
    try:
        users = crud.get_all_users()
        return {"success": True, "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")

@router.get("/users/me")
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

@router.get("/stories/feed")
def get_feed(user_email: str = Header(...)):
    """Returns all stories visible to the authenticated user."""
    try:
        client = crud.login_as(user_email)
        res = crud.get_visible_stories(client)
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/stories")
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

@router.get("/stories/{target_owner_id}")
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

@router.delete("/stories")
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

@router.get("/close-friends")
def get_close_friends(user_email: str = Header(...)):
    """Returns the current user's close friends list."""
    try:
        client = crud.login_as(user_email)
        res = crud.get_close_friends_list(client)
        return res
    except Exception as e:
        raise HTTPException(status_code=401, detail="Authentication failed")

@router.post("/close-friends")
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

@router.put("/close-friends/batch")
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

@router.delete("/close-friends/{member_id}")
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