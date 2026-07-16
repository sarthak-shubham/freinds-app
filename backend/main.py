from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

API_DESCRIPTION = """
**Welcome to the Close Friends Sandbox Environment.**

This API is stateless. Security is enforced natively at the database layer via **Supabase Row Level Security (RLS)**.

### 🧪 How to test this API (Sandbox Mode)
This demo is locked to 3 deterministic test accounts. To authenticate your requests, you must pass one of the following emails in the `userEmail` HTTP Header:
* `isha@example.com`
* `rahul@example.com`
* `shruti@example.com`

**Guided Security Tour:**
1. Hit `GET /api/users` to fetch the UUIDs for these three users.
2. Use those UUIDs in the other endpoints to test cross-account RLS enforcement!

**Examples of how to test:**
- **Add Rahul to Isha's Close Friends:** Call `POST /api/close-friends` with the `userEmail: isha@example.com` header, and send `{"member_id": "<rahul-uuid>"}` in the JSON body.
- **Post a Story for Isha:** Call `POST /api/stories` with the `userEmail: isha@example.com` header, and attach an image file using `multipart/form-data` with the key `file`.
- **View Isha's Story as Rahul:** Call `GET /api/stories/<isha-uuid>` with the `userEmail: rahul@example.com` header. RLS will grant access because Rahul is on her close friends list!
- **View Isha's Story as Shruti:** Call `GET /api/stories/<isha-uuid>` with the `userEmail: shruti@example.com` header. RLS will block access (403 Forbidden)!

**Note on Testing Malicious Modifications:**
You might wonder how to test maliciously deleting someone else's story or adding to someone else's friend list. Because of the backend's strict design, endpoints like `POST /stories` or `DELETE /stories` do not accept a target ID in the payload. They forcefully act only on the account provided in the `userEmail` header. Therefore, the **only** endpoint where you can actively test cross-account RLS blocking is `GET /api/stories/{target_owner_id}`.
"""

app = FastAPI(
    title="Close Friends API",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url=None
)

# Configure CORS — allow all origins for dev; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the router under the /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "API is running securely"}

@app.get("/docs", include_in_schema=False)
def scalar_html():
    return HTMLResponse(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Close Friends API Docs</title>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <style>body { margin: 0; }</style>
        </head>
        <body>
            <!-- Customize the Scalar UI theme here -->
            <script id="api-reference" data-url="/openapi.json" data-theme="moon"></script>
            <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
        </body>
        </html>
        """
    )