# Dengue-Outbreak-Prediction

This repository demonstrates dengue outbreak prediction for Bangladesh using climate and historical dengue data.

Key components:
- `DengueOutbreakPrediction/DengueOutbreakPrediction.ipynb` contains exploratory analysis and simple linear regression baselines on individual climate variables (minimum temperature, maximum temperature, humidity, and rainfall).
- `multi-linear regression/model.py` trains a multiple linear regression model on combined climate features, performs monthly/seasonal analysis, and generates visualization outputs.
- Dataset: `DengueOutbreakPrediction/Dataset/DengueAndClimateBangladesh.csv`.

Highlights:
- Baseline simple linear regression models investigate how each climate variable correlates with dengue cases.
- Multiple linear regression combines temperature, humidity, and rainfall to forecast dengue risk.
- Evaluation metrics include MSE, RMSE, MAE, and R².
- The current multiple linear regression model reports a test R² of 0.37 and a train R² of 0.18 on the held-out split.
- Generated output visualizations include `dengue_mlr_analysis.png`, `dengue_feature_analysis.png`, and `dengue_seasonal_analysis.png`.

This project provides an interpretable, climate-driven baseline for dengue forecasting and supports public health planning by highlighting seasonal and monthly risk patterns.
