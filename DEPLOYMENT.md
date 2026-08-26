# Production Deployment Guide - Render & Netlify

This guide explains how to deploy the Dengue Outbreak Prediction system to production, with the **Backend hosted on Render** and the **Frontend hosted on Netlify**.

---

## 📦 Step 1: Push Code to GitHub

1. Initialize git in your project root:
   ```bash
   git init
   git add .
   git commit -m "initial commit: dengue outbreak prediction dashboard"
   ```
2. Create a new repository on your GitHub account.
3. Link and push the code to your GitHub repository:
   ```bash
   git remote add origin <your-github-repo-url>
   git branch -M main
   git push -u origin main
   ```

---

## 🐍 Step 2: Deploy Backend to Render

1. Log in to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New** (top right) -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following configurations:
   * **Name:** `dengue-prediction-backend` (or custom name)
   * **Region:** Choose the region closest to you
   * **Branch:** `main`
   * **Runtime:** `Python`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. *(Optional)* Scroll down to **Environment Variables** if you want to connect a MySQL database instead of the default SQLite:
   * **Add Env Var:**
     * Key: `DATABASE_URL`
     * Value: `mysql+pymysql://username:password@hostname:3306/db_name`
6. Click **Create Web Service**.
7. Once deployed, note down your Render Web Service URL (e.g. `https://dengue-prediction-backend.onrender.com`).

---

## ⚛️ Step 3: Deploy Frontend to Netlify

1. Log in to the [Netlify Dashboard](https://app.netlify.com/).
2. Click **Add new site** -> **Import an existing project**.
3. Connect to your GitHub provider and select your repository.
4. Netlify will automatically detect the build settings from the `netlify.toml` file in the repository root.
5. Click **Environment Variables** (or configure under Site Settings -> Environment variables after creating) and add:
   * **Key:** `VITE_API_URL`
   * **Value:** `<your-render-backend-url>` (e.g., `https://dengue-prediction-backend.onrender.com` - *Make sure not to add a trailing slash*)
6. Click **Deploy Site**.

---

## 🔗 How it Works in Production

* **CORS Support:** The backend FastAPI server has CORS headers enabled (`allow_origins=["*"]`), which allows the Netlify frontend domain to securely call the Render APIs.
* **Global Fetch Override:** The frontend contains a global fetch interceptor that automatically redirects all relative API requests (`/api/...`) to the value specified in `VITE_API_URL` in production, maintaining standard routing.
* **Redirections:** Netlify is configured via `frontend/public/_redirects` to handle SPA browser refreshes on routes like `/login` or `/inspector` without throwing 404 errors.
