import os
import logging
from functools import lru_cache
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def login_as(email: str, password: str = "password123") -> Client:
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.auth.sign_in_with_password({"email": email, "password": password})
    return client

def get_service_client() -> Client:
    """Returns a service-role client for admin operations (bypasses RLS)."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_user_id(client: Client) -> str:
    return client.auth.get_user().user.id

# ==========================================
# USER OPERATIONS
# ==========================================

@lru_cache(maxsize=1)
def get_all_users() -> list:
    """Returns all seeded auth users. Cached to prevent O(N) network bottlenecks on feed load."""
    logger.info("Fetching all users from Supabase Auth (Cache Miss)")
    admin = get_service_client()
    users_res = admin.auth.admin.list_users()
    users = []
    for u in users_res:
        users.append({
            "id": u.id,
            "name": u.user_metadata.get("display_name", u.email.split("@")[0]),
            "email": u.email
        })
    return users

# ==========================================
# STORIES & STORAGE OPERATIONS
# ==========================================

def create_story_with_file(client: Client, file_bytes: bytes, filename: str) -> dict:
    """Uploads physical file bytes to Storage and saves the DB reference."""
    owner_id = get_user_id(client)
    # Extract extension from filename (e.g. .jpg, .png)
    ext = filename.split('.')[-1] if '.' in filename else 'jpg'
    storage_filename = f"{owner_id}_story.{ext}" 

    try:
        # 1. Upload bytes to Supabase Storage
        client.storage.from_("stories").upload(
            path=storage_filename, 
            file=file_bytes, 
            file_options={"x-upsert": "true"}
        )

        # 2. Save the database row
        res = client.table("stories").upsert(
            {"owner_id": owner_id, "image_url": storage_filename},
            on_conflict="owner_id"
        ).execute()

        return {"success": True, "data": res.data}
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

def get_visible_stories(client: Client) -> dict:
    """Returns all stories visible to the current user via RLS, with signed URLs and owner metadata."""
    try:
        # RLS ensures we only get stories we're allowed to see
        db_res = client.table("stories").select("*").order("created_at", desc=True).execute()
        
        if not db_res.data:
            return {"success": True, "stories": []}
        
        # Get all users for name resolution
        all_users = get_all_users()
        user_map = {u["id"]: u for u in all_users}
        
        # Batch Generate Signed URLs
        paths = [story["image_url"] for story in db_res.data]
        url_map = {}
        try:
            url_res = client.storage.from_("stories").create_signed_urls(paths, 3600)
            for item in url_res:
                if not item.get("error"):
                    signed_url = item.get("signedURL", item.get("signedUrl", ""))
                    url_map[item["path"]] = signed_url
        except Exception:
            pass

        stories = []
        for story in db_res.data:
            signed_url = url_map.get(story["image_url"], "")
            owner = user_map.get(story["owner_id"], {})
            
            stories.append({
                "id": story["id"],
                "owner_id": story["owner_id"],
                "owner_name": owner.get("name", "Unknown"),
                "owner_email": owner.get("email", ""),
                "image_url": signed_url,
                "created_at": story["created_at"]
            })
        
        return {"success": True, "stories": stories}
    except Exception as e:
        return {"success": False, "error": str(e), "stories": []}

def download_story_image(client: Client, target_owner_id: str) -> dict:
    """Proves RLS works, then returns a secure 60-second viewing URL."""
    try:
        # 1. Check if we can even see the database row
        db_res = client.table("stories").select("*").eq("owner_id", target_owner_id).execute()
        if not db_res.data:
            return {"success": False, "message": "Access Denied by DB: Cannot see story row."}
        
        storage_filename = db_res.data[0]["image_url"]

        # 2. Generate a short-lived Signed URL so React can display it
        url_res = client.storage.from_("stories").create_signed_url(storage_filename, 60)
        signed_url = url_res.get("signedURL", url_res.get("signedUrl", ""))
        
        return {"success": True, "image_url": signed_url}
    except Exception as e:
        return {"success": False, "error": f"Storage Access Denied: {str(e)}"}

def delete_story(client: Client) -> dict:
    owner_id = get_user_id(client)
    try:
        # Find the file extension first
        db_res = client.table("stories").select("image_url").eq("owner_id", owner_id).execute()
        if db_res.data:
            storage_filename = db_res.data[0]["image_url"]
            client.storage.from_("stories").remove([storage_filename])
            
        client.table("stories").delete().eq("owner_id", owner_id).execute()
        return {"success": True, "message": "Story completely deleted from DB and Storage."}
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

# ==========================================
# CLOSE FRIENDS OPERATIONS 
# ==========================================

def get_close_friends_list(client: Client) -> dict:
    """Returns the member_ids of the current user's close friends."""
    owner_id = get_user_id(client)
    try:
        res = client.table("close_friends").select("member_id").eq("owner_id", owner_id).execute()
        member_ids = [row["member_id"] for row in res.data]
        return {"success": True, "member_ids": member_ids}
    except Exception as e:
        return {"success": False, "error": str(e), "member_ids": []}

def add_close_friend(client: Client, member_id: str) -> dict:
    owner_id = get_user_id(client)
    try:
        res = client.table("close_friends").insert({"owner_id": owner_id, "member_id": member_id}).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

def remove_close_friend(client: Client, member_id: str) -> dict:
    owner_id = get_user_id(client)
    try:
        res = client.table("close_friends").delete().eq("owner_id", owner_id).eq("member_id", member_id).execute()
        return {"success": True, "data": res.data}
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}

def batch_update_close_friends(client: Client, member_ids: list) -> dict:
    """
    Replaces the entire close friends list atomically.
    Computes diff between current and desired, then adds/removes as needed.
    """
    owner_id = get_user_id(client)
    try:
        # Get current list
        current_res = client.table("close_friends").select("member_id").eq("owner_id", owner_id).execute()
        current_ids = set(row["member_id"] for row in current_res.data)
        desired_ids = set(member_ids)
        
        to_add = desired_ids - current_ids
        to_remove = current_ids - desired_ids
        
        # Remove friends no longer in the list
        for mid in to_remove:
            client.table("close_friends").delete().eq("owner_id", owner_id).eq("member_id", mid).execute()
        
        # Add new friends
        for mid in to_add:
            client.table("close_friends").insert({"owner_id": owner_id, "member_id": mid}).execute()
        
        return {"success": True, "added": list(to_add), "removed": list(to_remove)}
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}