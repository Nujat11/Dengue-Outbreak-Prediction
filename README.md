# 🦟 Dengue Outbreak Prediction & Early Warning System

An AI-integrated, full-stack web application that predicts monthly dengue case counts, classifies outbreak risk levels, plans hospital resource allocation, and issues early warnings for public health administrators. The system combines historical climate + dengue case data, a trained machine learning model, live weather data, and role-based dashboards into a single deployable application.

---

## 📑 Table of Contents

- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Features](#-features)
- [Dataset](#-dataset)
- [Model Evolution](#-model-evolution-old_models)
- [API Overview](#-api-overview)
- [Getting Started](#-getting-started)
- [Demo Login Credentials](#-demo-login-credentials)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment)
- [Tech Stack Summary](#-tech-stack-summary)

---

## 🏗️ System Architecture

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.13) |
| **Frontend** | React 18 + TypeScript (Vite) + Tailwind CSS |
| **Visualizations** | Recharts |
| **Database** | SQLite (zero-setup local default) — fully compatible with MySQL 8.0 via `DATABASE_URL` |
| **Auth** | JWT (PyJWT) + Passlib (bcrypt) with role-based access control |
| **AI Core** | Random Forest Regressor (scikit-learn), trained on engineered climate/seasonality features |
| **Live Climate Data** | Open-Meteo API integration |
| **Report Generation** | ReportLab (PDF compilation) |
| **Hosting (reference)** | Backend → Render, Frontend → Netlify |

The backend serves the compiled React app directly (via `StaticFiles`) for a single-command unified local run, while also being deployable as a standalone API for a separately hosted frontend.

---

## 📂 Project Structure

```
Dengue-Outbreak-Prediction/
├── backend/                     # FastAPI application
│   ├── main.py                  # App entrypoint, routes, CORS, startup seeding
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py                # Pydantic request/response schemas
│   ├── database.py              # DB engine/session setup
│   ├── auth.py                  # JWT auth, password hashing, role checks
│   ├── ml_model.py               # Training, inference & metrics for the RF model
│   ├── pdf_generator.py          # ReportLab PDF report builder
│   ├── seed_data.py              # Initial DB seeding (demo users, sample records)
│   └── dengue_model.joblib       # Serialized trained Random Forest model
│
├── frontend/                     # React + Vite + TypeScript client
│   ├── src/
│   │   ├── App.tsx               # Routing & role-based layout
│   │   ├── main.tsx              # App bootstrap
│   │   ├── index.css             # Tailwind entrypoint
│   │   └── pages/
│   │       ├── LoginRegister.tsx     # Auth screen
│   │       ├── PublicDashboard.tsx   # Public risk map, trends, advisories
│   │       ├── InspectorDashboard.tsx # Data entry, predictions, PDF reports
│   │       └── AdminDashboard.tsx    # User mgmt, retraining, config, audit logs
│   ├── public/                   # Static assets, `_redirects` for SPA routing
│   ├── dist/                     # Production build output (served by backend)
│   └── package.json
│
├── Dataset/
│   ├── DengueAndClimateBangladesh.csv   # Historical climate + dengue case dataset
│   └── DengueOutbreakPrediction_.xlsx   # Same dataset in spreadsheet form
│
├── Old_Models/                   # Earlier modeling iterations (kept for reference)
│   ├── Simple_Linear_Regression/
│   │   ├── DengueOutbreakPrediction.ipynb   # Initial linear regression notebook
│   │   ├── Dengue_Prediction_Report.pdf     # Write-up of the linear regression study
│   │   └── Overleaf_Dengue_Prediction.zip   # LaTeX source for the report
│   └── multi-linear regression/
│       └── model.py                         # Multi-linear regression experiment
│
├── dengue_feature_analysis.png    # EDA: feature relationships
├── dengue_mlr_analysis.png        # EDA: multi-linear regression analysis
├── dengue_seasonal_analysis.png   # EDA: seasonal case trends
│
├── requirements.txt               # Python dependencies
├── run.py                         # One-command local launcher (installs deps, builds, serves)
├── netlify.toml                   # Netlify build/redirect config for frontend hosting
├── DEPLOYMENT.md                  # Render + Netlify production deployment guide
└── README.md                      # You are here
```

> Note: `venv/`, `node_modules/`, `dist/`, `__pycache__/`, and `dengue.db` are local/build artifacts and should stay out of version control (see `.gitignore`).

---

## ✨ Features

1. **Predictive Analytics** — Random Forest Regressor (R² ≈ 0.87) using cyclic seasonality features (month sine/cosine) and interaction terms (temperature difference, rain–humidity ratio) to forecast monthly dengue case counts from weather variables.
2. **Interactive Risk Map** — Color-coded SVG map of Dhaka zones with dynamically scaled Low / Medium / High warning levels.
3. **Live Weather Sync** — Status bar and auto-fill form pulling Dhaka's real-time meteorological data from Open-Meteo.
4. **Surge Calculator** — Automatically estimates hospital bed allocation, paracetamol tablets, IV fluid bags, and blood/platelet needs based on predicted case volume.
5. **PDF Report Export** — Generates standardized health-administrator summaries with charts, predictions, and recommendations.
6. **Role-Based Access Control**
   - **Admin** — manages user accounts, retrains the ML model, edits alert thresholds, reviews audit logs.
   - **Inspector** — enters weather/dengue records, runs predictions, downloads PDF reports.
   - **Public** — views trends, the risk map, and public health advisories.
7. **Audit Trail** — Immutable activity log capturing security events, configuration changes, and record edits.

---

## 📊 Dataset

Located under `Dataset/`:
- `DengueAndClimateBangladesh.csv` — historical monthly climate variables (temperature, rainfall, humidity, etc.) paired with recorded dengue case counts.
- `DengueOutbreakPrediction_.xlsx` — the same data in spreadsheet form for manual inspection/analysis.

Exploratory analysis outputs are saved at the project root:
- `dengue_feature_analysis.png`, `dengue_mlr_analysis.png`, `dengue_seasonal_analysis.png`

---

## 🧪 Model Evolution (`Old_Models/`)

This folder preserves the modeling history leading up to the current Random Forest approach:

- **`Simple_Linear_Regression/`** — the original baseline model (Jupyter notebook), plus a written report (`Dengue_Prediction_Report.pdf`) and its LaTeX/Overleaf source.
- **`multi-linear regression/model.py`** — a follow-up multi-linear regression experiment that informed the feature engineering used in the current production model (`backend/ml_model.py`).

These are kept for reference and are **not** used by the running application.

---

## 🔌 API Overview

All endpoints are prefixed with `/api`. Selected routes:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/register` | Register a new (public) user |
| POST | `/api/auth/login` | Authenticate and receive a JWT |
| GET/PUT | `/api/admin/users`, `/api/admin/users/{id}/role`, `/api/admin/users/{id}/status` | Admin user management |
| GET/POST/DELETE | `/api/records/climate`, `/api/records/dengue` | Climate & dengue record CRUD (Inspector/Admin) |
| POST | `/api/predictions/predict` | Run the model on given inputs |
| GET | `/api/predictions/history` | Past predictions |
| GET | `/api/notifications` | Simulated SMS/Email alert log |
| GET/POST | `/api/admin/metrics`, `/api/admin/retrain` | Model performance metrics & retraining |
| GET/PUT | `/api/admin/config`, `/api/admin/config/{key}` | Alert threshold / system configuration |
| GET | `/api/admin/logs` | Audit log |
| GET | `/api/weather/current`, `/api/weather/realtime` | Live weather via Open-Meteo |
| GET | `/api/dashboard/summary` | Aggregated dashboard stats |
| GET | `/api/reports/pdf` | Download the generated PDF report |

The catch-all `GET /{full_path:path}` route serves the built React SPA (`frontend/dist`) for any non-API path.

---

## 🚀 Getting Started

### One-command local run (recommended)

```bash
python run.py
```

This will:
1. Install Python dependencies from `requirements.txt`
2. Install frontend npm dependencies
3. Build the production React bundle (`frontend/dist`)
4. Start the unified FastAPI server

Then open **http://localhost:8000** in your browser.

### Manual setup (for active development)

**Backend:**
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

**Frontend (separate dev server with hot reload):**
```bash
cd frontend
npm install
npm run dev
```
The Vite dev server runs on `http://localhost:5173` and proxies API calls to the backend.

---

## 🔑 Demo Login Credentials

The database is pre-seeded with these test accounts:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | **Admin** |
| `inspector` | `inspector123` | **Inspector** |
| `user` | `user123` | **Public** |

---

## ⚙️ Environment Variables

| Variable | Where | Purpose |
|---|---|---|
| `DATABASE_URL` | Backend (Render/production) | Optional. Switch from default SQLite to MySQL, e.g. `mysql+pymysql://user:pass@host:3306/db_name` |
| `VITE_API_URL` | Frontend (Netlify/production) | Base URL of the deployed backend API (no trailing slash) |

---

## ☁️ Deployment

Full step-by-step instructions for hosting the **backend on Render** and the **frontend on Netlify** are documented in [`DEPLOYMENT.md`](./DEPLOYMENT.md), including:
- Pushing the repo to GitHub
- Render web service configuration (build/start commands, optional MySQL `DATABASE_URL`)
- Netlify site configuration via `netlify.toml`, environment variables, and SPA redirect handling
- How CORS and the frontend's fetch override connect the two deployed services

---

## 🧰 Tech Stack Summary

`FastAPI` · `SQLAlchemy` · `Pydantic` · `PyJWT` · `Passlib (bcrypt)` · `scikit-learn` · `pandas` / `numpy` · `ReportLab` · `React 18` · `TypeScript` · `Vite` · `Tailwind CSS` · `Recharts` · `lucide-react`
