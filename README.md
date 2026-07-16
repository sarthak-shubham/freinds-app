# FREINDS - Secure Social Feed App

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)

**FREINDS** is a highly responsive, production-ready social media web application. It was built to demonstrate advanced, secure backend architecture—specifically focusing on **Database-Level Row Level Security (RLS)**—paired with a gorgeous, fluid, mobile-first frontend layout.

## 🚀 Key Features
- **Strict Data Isolation (RLS):** Feed visibility is controlled directly at the PostgreSQL database level using Supabase Row Level Security. Data is never leaked to the frontend for filtering.
- **Optimized Backend:** Built with Python FastAPI, featuring internal LRU Caching for high-speed repeated queries.
- **Fluid UI Architecture:** The frontend utilizes advanced CSS Grid and Flexbox to scale seamlessly from tiny mobile screens to ultra-wide desktop monitors without wasting space.
- **Enterprise Ready:** Fully containerized with Docker, covered by Pytest test suites, and utilizes structured logging.

---

## 🧪 Evaluator Guide: Testing the RLS "Happy Path"

To make testing easy without requiring email signups, this app features a built-in **Mock Account Switcher** located in the top right of the navigation bar. 

To verify that the Row Level Security policies are working perfectly, follow this exact testing path:

### Step 1: Set Up the Close Friends List
1. Open the app and use the top-right account switcher to log in as **Isha**.
2. Click the **Close Friends** icon (the group icon) in the navigation bar.
3. Toggle **Shruti** to be ON (added to close friends).
4. Leave **Rahul** toggled OFF (not in close friends).
5. Click **Done**.

### Step 2: Create a Secure Story
1. Return to the Home feed.
2. Click the **+** (Add Story) button.
3. Upload an image to post a new story as Isha.

### Step 3: Verify the RLS Database Rules
Now, we test if the database properly secures the data:
1. Switch your account to **Shruti**. 
   - *Result:* You should see Isha's story natively on your feed.
2. Switch your account to **Rahul**.
   - *Result:* Your feed should be completely empty ("No stories yet"). 

> **What is happening behind the scenes?** 
> Rahul's empty feed is **not** achieved by a frontend `if` statement hiding the story. When Rahul's client requests the feed, the Supabase Postgres Database intercepts the query, evaluates the relational `close_friends` table via RLS policies, and strictly denies returning the rows. The data never even reaches the backend server!

---

## 💻 Tech Stack

### Frontend
- **React.js (Vite):** Fast, modern UI rendering.
- **Vanilla CSS:** Custom design system utilizing CSS Variables, Grid, and Flexbox for native responsiveness without heavy framework bloat.
- **SWR:** Stale-while-revalidate for highly performant client-side data fetching.

### Backend
- **Python FastAPI:** Asynchronous, high-performance API routing.
- **Supabase:** PostgreSQL database, Auth, and Storage buckets.
- **Pytest:** 17+ assertions for robust test coverage.
- **Docker:** Complete `docker-compose` setup for isolated environments.

---

## 🛠️ Local Development Setup

To run this project locally, you will need Node.js, Python 3.11+, and a Supabase project.

### 1. Environment Variables
Create a `.env` file in the root directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 2. Run the Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
*(Or use `docker-compose up backend --build`)*

### 3. Run the Frontend
```bash
cd frontend
npm install
npm run dev
```

### 4. Run the Test Suite
```bash
cd backend
python -m pytest tests/ -v
```
