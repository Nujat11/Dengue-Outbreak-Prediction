# Dengue-Outbreak-Prediction

An AI-integrated full-stack web application designed to predict Dengue outbreaks, classify risk levels, plan hospital resource allocations, and issue early warnings. The system integrates historical climate data and dengue cases, applies a Random Forest Regressor model, fetches real-time weather, and logs simulated SMS/Email notifications.


---

## 🏗️ System Architecture

- **Backend Framework:** FastAPI (Python 3.13)
- **Frontend Framework:** React.js (Vite + TypeScript) + Tailwind CSS
- **Visualizations:** Recharts / Chart.js
- **Database:** SQLite (default for zero-setup local run) / fully compatible with MySQL 8.0
- **AI Core:** Random Forest Regressor (scikit-learn)
- **Live Climate Data:** Open-Meteo API integration
- **Report Generator:** ReportLab (PDF compilation)

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

## 🚀 How to Run Locally

You can launch the entire unified application (installing requirements, building frontend, seeding database, and starting backend) in a single command:

1. Clone or open the project folder in your terminal.
2. Run the automation script:
   ```bash
   python run.py
   ```
3. Open your browser and navigate to: **`http://localhost:8000`**
