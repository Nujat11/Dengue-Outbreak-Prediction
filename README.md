# Dengue-Outbreak-Prediction

[![Netlify Status](https://api.netlify.com/api/v1/badges/7bb1f7b7-29a1-4785-a44b-5f78468f3597/deploy-status)](https://app.netlify.com/projects/dengueoutbreakprediction/deploys)

### 🌐 Live Deployment Links
* **Frontend (Netlify):** [https://dengueoutbreakprediction.netlify.app](https://dengueoutbreakprediction.netlify.app)
* **Backend API (Render):** [https://dengue-outbreak-prediction-backend.onrender.com](https://dengue-outbreak-prediction-backend.onrender.com)

An AI-integrated full-stack web application designed to predict Dengue outbreaks, classify risk levels, plan hospital resource allocations, and issue early warnings. The system integrates historical climate data and dengue cases, applies a Multiple Linear Regression model, fetches real-time weather, and logs simulated SMS/Email notifications.


---

## 🏗️ System Architecture

- **Backend Framework:** FastAPI (Python 3.13)
- **Frontend Framework:** React.js (Vite + TypeScript) + Tailwind CSS
- **Visualizations:** Recharts / Chart.js
- **Database:** SQLite (default for zero-setup local run) / fully compatible with MySQL 8.0
- **AI Core:** Multiple Linear Regression (scikit-learn)
- **Live Climate Data:** Open-Meteo API integration
- **Report Generator:** ReportLab (PDF compilation)

---

## ✨ Features Implemented

1. **Predictive Analytics:** Runs Multiple Linear Regression to forecast monthly dengue cases based on weather variables (Min Temp, Max Temp, Humidity, Rainfall).
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

## 🚀 How to Run Locally

You can launch the entire unified application (installing requirements, building frontend, seeding database, and starting backend) in a single command:

1. Clone or open the project folder in your terminal.
2. Run the automation script:
   ```bash
   python run.py
   ```
3. Open your browser and navigate to: **`http://localhost:8000`**

### 🔑 Demo Login Credentials

The database is pre-seeded with these testing accounts:

| Username | Password | Role |
|---|---|---|
| `admin` | `admin123` | **Admin** |
| `inspector` | `inspector123` | **Inspector** |
| `user` | `user123` | **Public** |

---

## 🌐 Production Deployment

* **Live Frontend:** [https://dengueoutbreakprediction.netlify.app](https://dengueoutbreakprediction.netlify.app)
* **Live Backend API:** [https://dengue-outbreak-prediction-backend.onrender.com](https://dengue-outbreak-prediction-backend.onrender.com) (or your specific Render service URL)

Refer to **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed hosting instructions:
* **Backend:** Deploy `backend.main:app` as a Python Web Service on **Render**.
* **Frontend:** Build the `frontend` subfolder and publish to **Netlify** with the `VITE_API_URL` environment variable.
