import os
import time
from crud import (
    login_as, get_user_id, create_story_with_file, download_story_image, delete_story,
    add_close_friend, remove_close_friend
)

def print_step(msg):
    print(f"\n[{'='*40}]")
    print(f"👉 {msg}")
    print(f"[{'='*40}]")

def create_dummy_image():
    """Creates a fake physical file on your computer to test the upload."""
    filepath = "dummy_upload.jpg"
    with open(filepath, "wb") as f:
        f.write(b"This is fake image data to prove physical file upload works!")
    return filepath

def run_demo():
    print("Generating local dummy file...")
    dummy_file = create_dummy_image()

    print("Initializing clients and logging in users...")
    rahul = login_as("rahul@example.com")
    isha = login_as("isha@example.com")

    rahul_id = get_user_id(rahul)
    isha_id = get_user_id(isha)

    print_step("1. Rahul uploads a PHYSICAL image file to his story")
    res1 = create_story_with_file(rahul, dummy_file)
    print("Result:", res1)

    print_step("2. Isha attempts to DOWNLOAD the file BEFORE being a close friend")
    res2 = download_story_image(isha, target_owner_id=rahul_id)
    print("Result:", res2)

    print_step("3. Rahul adds Isha to his Close Friends list")
    add_close_friend(rahul, member_id=isha_id)
    print("Result: Success")

    print_step("4. Isha attempts to DOWNLOAD the file AFTER being added")
    res4 = download_story_image(isha, target_owner_id=rahul_id)
    print("Result:", res4)

    print_step("5. Rahul revokes Isha's access")
    remove_close_friend(rahul, member_id=isha_id)
    print("Result: Success")

    print_step("6. Isha attempts to DOWNLOAD the file AFTER being removed")
    res6 = download_story_image(isha, target_owner_id=rahul_id)
    print("Result:", res6)

    print_step("7. Rahul DELETES his story (Clears DB + Storage)")
    res7 = delete_story(rahul)
    print("Result:", res7)

    # Cleanup the local dummy file
    if os.path.exists(dummy_file):
        os.remove(dummy_file)

if __name__ == "__main__":
    run_demo()