# Dengue-Outbreak-Prediction

This repository demonstrates dengue outbreak prediction for Bangladesh using climate and historical dengue data.

Key components:
- Notebook (exploratory analysis + simple linear regression): [DengueOutbreakPrediction/Simple_Linear_Regression/DengueOutbreakPrediction.ipynb](DengueOutbreakPrediction/Simple_Linear_Regression/DengueOutbreakPrediction.ipynb)
- Multiple Linear Regression script and analysis: [DengueOutbreakPrediction/multi-linear regression/model.py](DengueOutbreakPrediction/multi-linear%20regression/model.py#L1)
- Dataset: [DengueOutbreakPrediction/Dataset/DengueAndClimateBangladesh.csv](DengueOutbreakPrediction/Dataset/DengueAndClimateBangladesh.csv)

Highlights:
- Baseline simple linear regression models investigate how each climate variable correlates with dengue cases.
- Multiple linear regression combines temperature, humidity, and rainfall to forecast dengue risk.
- Evaluation metrics include MSE, RMSE, MAE, and R².
- Generated output visualizations (saved to repository root by the script): `dengue_mlr_analysis.png`, `dengue_feature_analysis.png`, and `dengue_seasonal_analysis.png`.

Quick run
```
python "DengueOutbreakPrediction/multi-linear regression/model.py"
```

Dependencies
```
pip install pandas scikit-learn matplotlib seaborn joblib
```

Notes and limitations
- The current forecasting step in `model.py` uses historical monthly means for climate features — this is a heuristic, not a probabilistic forecast. Use a proper time-series or exogenous-variable model for production forecasts.
- The script currently uses a random 80/20 train/test split; for time series data prefer a time-based split (or `TimeSeriesSplit`) to avoid leakage.
- Consider feature scaling (e.g., `StandardScaler`) and cross-validation for more robust estimates.

Contribution / Contact
- Feel free to open issues or PRs. For questions, add a GitHub issue in this repository.

This project provides an interpretable, climate-driven baseline for dengue forecasting and supports exploratory analysis and public-health planning by highlighting seasonal and monthly risk patterns.
