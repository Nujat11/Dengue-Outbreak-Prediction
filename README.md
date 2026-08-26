# Dengue-Outbreak-Prediction

An AI-integrated full-stack web application designed to predict Dengue outbreaks, classify risk levels, plan hospital resource allocations, and issue early warnings. The system integrates historical climate data and dengue cases, applies a Random Forest Regressor model, fetches real-time weather, and logs simulated SMS/Email notifications.


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

## ✨ Features Implemented

1. **Predictive Analytics:** Runs a Random Forest Regressor (R² ~ 0.87) incorporating cyclic seasonality (month sine/cosine) and interaction features (temperature difference, rain-humidity ratio) to forecast monthly dengue cases based on weather variables.
2. **Interactive Risk Map:** Color-coded SVG boundary map representing Dhaka Zones with dynamically scaled warning levels (Low, Medium, High).
3. **Live Weather Sync:** A dedicated status bar and automated form-filler that queries Dhaka's live meteorology conditions from Open-Meteo.
4. **Surge Calculator:** Automatically computes hospital bed allocations, Paracetamol tablets, IV fluid bags, and blood/platelet needs according to predicted cases.
5. **PDF Report Downloader:** Standardized health administrator summaries containing charts, predictions, and recommendations.
6. **Multi-Role Security:**
   - **Admin:** Manages accounts, retrains ML models, edits alert thresholds, and checks audit logs.
   - **Inspector:** Inserts weather/dengue records, runs predictions, and pulls PDF reports.
   - **Public:** Views trends, risk maps, and reads health advisories.
7. **Audit Trails:** Immutable activity logger capturing security, configurations, and database edits.

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

## 🚀 How to Run Locally

You can launch the entire unified application (installing requirements, building frontend, seeding database, and starting backend) in a single command:

1. Clone or open the project folder in your terminal.
2. Run the automation script:
   ```bash
   python run.py
   ```
---
3. Open your browser and navigate to: **`http://localhost:8000`**
