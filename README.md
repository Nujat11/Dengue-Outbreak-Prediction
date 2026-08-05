# Dengue-Outbreak-Prediction



This repository demonstrates a dengue outbreak prediction pipeline for Bangladesh using climate and historical dengue data. The analysis includes both Simple Linear Regression and Multiple Linear Regression:

- Simple Linear Regression is used as a baseline model to study the relationship between a single climate variable and dengue cases.
- Multiple Linear Regression is then applied to incorporate multiple climate variables together (rainfall, temperature, and humidity) for more robust dengue forecasting.

The main model script is available at `multi-linear regression/model.py`, and it runs data preparation, seasonal/monthly analysis, regression training, and forecasting.

The code loads the `DengueAndClimateBangladesh.csv` dataset, performs seasonal and monthly analysis, trains regression models, evaluates performance with MSE, RMSE, MAE, and R², and generates visual reports showing actual vs predicted cases, feature impact, and seasonal trends.

This project provides a simple, interpretable baseline for weather-driven dengue forecasting and highlights how climate variables can support early warning and public health planning.
