import os
import psycopg2
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def apply_sql_file(filename: str):
    print(f"Applying {filename}...")
    sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'supabase', filename)
    with open(sql_file_path, 'r') as file:
        sql_content = file.read()

    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ {filename} successfully applied!")
    except Exception as e:
        print(f"❌ Error applying {filename}: {e}")

def seed_users():
    print("\nSeeding auth users...")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    test_users = [
        {"email": "rahul@example.com", "password": "password123", "name": "Rahul"},
        {"email": "shruti@example.com", "password": "password123", "name": "Shruti"},
        {"email": "isha@example.com", "password": "password123", "name": "Isha"}
    ]

    for user_data in test_users:
        try:
            res = supabase.auth.admin.create_user({
                "email": user_data["email"],
                "password": user_data["password"],
                "email_confirm": True,
                "user_metadata": {"display_name": user_data["name"]}
            })
            print(f"✅ Created user: {user_data['name']}")
        except Exception as e:
            if "already exists" in str(e).lower() or "422" in str(e):
                print(f"⚠️ User {user_data['name']} already exists.")
            else:
                print(f"❌ Error creating {user_data['name']}: {e}")

if __name__ == "__main__":
    print("--- Starting Full Backend Setup ---")
    apply_sql_file('schema.sql')
    apply_sql_file('storage.sql')
    seed_users()
    print("--- Setup Complete ---")