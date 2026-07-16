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