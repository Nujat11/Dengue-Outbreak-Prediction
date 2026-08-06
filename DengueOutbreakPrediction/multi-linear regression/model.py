"""
Dengue Outbreak Prediction using Multiple Linear Regression Formula
Formula: y = θ0 + θ1*x1 + θ2*x2 + ... + θn*xn
Features: Full Monthly/Seasonal analysis, Correlation, 3 Detailed Visualizations, and Summary Report.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['figure.dpi'] = 120

# 1. LOAD AND PREPARE DATA

print("="*70)
print("DENGUE OUTBREAK PREDICTION - MULTIPLE LINEAR REGRESSION")
print("="*70)

# Load data
script_dir = os.path.dirname(os.path.realpath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, os.pardir))
possible_paths = [
    os.path.join(script_dir, 'Dataset', 'DengueAndClimateBangladesh.csv'),
    os.path.join(script_dir, 'DengueOutbreakPrediction', 'Dataset', 'DengueAndClimateBangladesh.csv'),
    os.path.join(script_dir, '..', 'Dataset', 'DengueAndClimateBangladesh.csv'),
    os.path.join(repo_root, 'DengueOutbreakPrediction', 'Dataset', 'DengueAndClimateBangladesh.csv'),
    os.path.join(repo_root, 'Dataset', 'DengueAndClimateBangladesh.csv')
]

data_path = None
for path in possible_paths:
    if os.path.exists(path):
        data_path = os.path.abspath(path)
        break

if data_path is None:
    raise FileNotFoundError(
        'Could not find Dataset/DengueAndClimateBangladesh.csv. '
        'Please ensure the dataset is located in the Dataset folder next to this script.'
    )

df = pd.read_csv(data_path)
print("\n✓ Data loaded successfully!")
print(f"Dataset shape: {df.shape}")
print(f"\nFirst few rows:\n{df.head()}")

# Create date column and sort
df['Date'] = pd.to_datetime(df[['YEAR', 'MONTH']].assign(DAY=1))
df = df.sort_values('Date').reset_index(drop=True)

# Define seasons (Bangladesh)
def get_season(month):
    if month in [3, 4, 5]:
        return 'Pre-Monsoon'
    elif month in [6, 7, 8, 9]:
        return 'Monsoon'
    elif month in [10, 11]:
        return 'Post-Monsoon'
    else:
        return 'Winter'

df['SEASON'] = df['MONTH'].apply(get_season)

print("\n" + "="*70)
print("SEASONAL DISTRIBUTION")
print("="*70)
print(df['SEASON'].value_counts())

# 2. MULTIPLE LINEAR REGRESSION MODEL & FORMULA COMPUTATION

print("\n" + "="*70)
print("MULTIPLE LINEAR REGRESSION FORMULA EVALUATION")
print("="*70)

# Feature matrix X and target vector y
feature_names = ['MIN', 'MAX', 'HUMIDITY', 'RAINFALL']
features = ['MIN Temp', 'MAX Temp', 'HUMIDITY', 'RAINFALL']
X = df[feature_names].values
y = df['DENGUE'].values

# 80/20 train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Fit linear regression model
mlr_model = LinearRegression()
mlr_model.fit(X_train, y_train)

# Model Parameters for Formula: y = θ0 + θ1*x1 + θ2*x2 + θ3*x3 + θ4*x4
theta_0 = mlr_model.intercept_
theta_1, theta_2, theta_3, theta_4 = mlr_model.coef_

print("\nLearned Parameters:")
print(f"  θ0 (Intercept) : {theta_0:.4f}")
print(f"  θ1 (MIN)       : {theta_1:.4f}")
print(f"  θ2 (MAX)       : {theta_2:.4f}")
print(f"  θ3 (HUMIDITY)  : {theta_3:.4f}")
print(f"  θ4 (RAINFALL)  : {theta_4:.4f}")

print("\nMathematical Equation:")
print(f"  y = {theta_0:.4f} + ({theta_1:.4f} * MIN) + ({theta_2:.4f} * MAX) + "
      f"({theta_3:.4f} * HUMIDITY) + ({theta_4:.4f} * RAINFALL)")

# Predict using the manual formula dot-product formulation: y = θ0 + X @ θ
y_train_pred = theta_0 + np.dot(X_train, [theta_1, theta_2, theta_3, theta_4])
y_test_pred = theta_0 + np.dot(X_test, [theta_1, theta_2, theta_3, theta_4])

# Train-set metrics
train_mse = mean_squared_error(y_train, y_train_pred)
train_rmse = np.sqrt(train_mse)
train_mae = mean_absolute_error(y_train, y_train_pred)
train_r2 = r2_score(y_train, y_train_pred)

# Test-set metrics
test_mse = mean_squared_error(y_test, y_test_pred)
test_rmse = np.sqrt(test_mse)
test_mae = mean_absolute_error(y_test, y_test_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"\nTrain Set Performance ({len(X_train)} samples):")
print(f"  • R² Score:        {train_r2:.4f}")
print(f"  • RMSE:            {train_rmse:.4f}")
print(f"  • MAE:             {train_mae:.4f}")
print(f"  • MSE:             {train_mse:.4f}")

print(f"\nTest Set Performance ({len(X_test)} samples):")
print(f"  • R² Score:        {test_r2:.4f}")
print(f"  • RMSE:            {test_rmse:.4f}")
print(f"  • MAE:             {test_mae:.4f}")
print(f"  • MSE:             {test_mse:.4f}")

# Full dataset fit for analysis and forecasting
mlr_full = LinearRegression()
mlr_full.fit(X, y)
theta_0_full = mlr_full.intercept_
theta_full = mlr_full.coef_
y_pred = theta_0_full + np.dot(X, theta_full)

# 3. MONTHLY ANALYSIS

print("\n" + "="*70)
print("MONTHLY ANALYSIS")
print("="*70)

print("\nAverage Dengue Cases by Month:")
monthly_dengue = df.groupby('MONTH')['DENGUE'].mean().round(2)
for month, cases in monthly_dengue.items():
    month_name = pd.Timestamp(year=2020, month=int(month), day=1).strftime('%B')
    print(f"  • {month_name:12s}: {cases:8.2f} cases")

# 4. SEASONAL ANALYSIS

print("\n" + "="*70)
print("SEASONAL ANALYSIS")
print("="*70)

print("\nDengue Cases by Season:")
seasonal_dengue = df.groupby('SEASON')['DENGUE'].mean().sort_values(ascending=False)
for season, cases in seasonal_dengue.items():
    print(f"  • {season:20s}: {cases:8.2f} cases (avg)")

# 5. FUTURE PREDICTIONS (Next 12 Months using Formula)

print("\n" + "="*70)
print("FUTURE PREDICTIONS (Next 12 Months)")
print("="*70)

last_year = df['YEAR'].max()
last_month = df[df['YEAR'] == last_year]['MONTH'].max()

future_months = []
future_data = []

for i in range(1, 13):
    month = ((last_month + i - 1) % 12) + 1
    year = last_year + (last_month + i - 1) // 12
    
    month_hist = df[df['MONTH'] == month]
    
    if len(month_hist) > 0:
        min_temp = month_hist['MIN'].mean()
        max_temp = month_hist['MAX'].mean()
        humidity = month_hist['HUMIDITY'].mean()
        rainfall = month_hist['RAINFALL'].mean()
    else:
        min_temp = df['MIN'].mean()
        max_temp = df['MAX'].mean()
        humidity = df['HUMIDITY'].mean()
        rainfall = df['RAINFALL'].mean()
    
    future_data.append([min_temp, max_temp, humidity, rainfall])
    future_months.append((year, month))

future_array = np.array(future_data)
# Applying y = θ0 + Σ(θi * xi)
future_predictions = theta_0_full + np.dot(future_array, theta_full)
future_predictions = np.maximum(future_predictions, 0)

future_df = pd.DataFrame({
    'Year': [m[0] for m in future_months],
    'Month': [m[1] for m in future_months],
    'Predicted_Cases': future_predictions.astype(int)
})

for idx, row in future_df.iterrows():
    month_name = pd.Timestamp(year=int(row['Year']), month=int(row['Month']), day=1).strftime('%B')
    print(f"  • {month_name} {int(row['Year'])}: {int(row['Predicted_Cases']):6d} cases (predicted)")

# 6. VISUALIZATIONS

print("\n" + "="*70)
print("GENERATING VISUALIZATIONS...")
print("="*70)

# Figure 1: Actual vs Predicted & Forecast
# Increase figure height to give more room for the suptitle
fig, axes = plt.subplots(2, 2, figsize=(16, 14))

# Plot 1: Actual vs Predicted Time Series (formatted to avoid overlaps)
axes[0, 0].plot(df['Date'], y, color='tab:blue', label='Actual Cases', linewidth=1.5, alpha=0.8)
axes[0, 0].plot(df['Date'], y_pred, color='tab:red', linestyle='--', label='MLR Prediction Formula', linewidth=1.5, alpha=0.8)
axes[0, 0].set_ylabel('Number of Cases', fontsize=11, fontweight='bold')
axes[0, 0].set_title('Dengue Cases: Actual vs MLR Predictions', fontsize=12, fontweight='bold')
# Use year ticks and rotate labels to prevent overlapping text
axes[0, 0].set_xlim(df['Date'].min(), df['Date'].max())
axes[0, 0].xaxis.set_major_locator(mdates.YearLocator())
axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
for lbl in axes[0, 0].get_xticklabels():
    lbl.set_rotation(45)
# Move legend outside plot area to avoid overlapping with the plot
axes[0, 0].legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=10)
axes[0, 0].grid(True, alpha=0.3)

# Plot 2: Monthly Average Dengue Cases
monthly_order = range(1, 13)
monthly_avg = df.groupby('MONTH')['DENGUE'].mean().reindex(monthly_order)
colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(monthly_avg)))
bars = axes[0, 1].bar(range(len(monthly_avg)), monthly_avg.values, color=colors, edgecolor='black', linewidth=1.2)
axes[0, 1].set_xticks(range(len(monthly_avg)))
axes[0, 1].set_xticklabels([pd.Timestamp(year=2020, month=m, day=1).strftime('%b') for m in monthly_order])
axes[0, 1].set_xlabel('Month', fontsize=11, fontweight='bold')
axes[0, 1].set_ylabel('Average Cases', fontsize=11, fontweight='bold')
axes[0, 1].set_title('Average Dengue Cases by Month', fontsize=12, fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='y')
for bar in bars:
    height = bar.get_height()
    axes[0, 1].text(bar.get_x() + bar.get_width() / 2., height + 10,
                    f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 3: Seasonal Analysis (Pie Chart) - move percentages to legend to avoid overlap
seasonal_total = df.groupby('SEASON')['DENGUE'].sum()
colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
# Draw pie without in-slice percentage labels
wedges, _texts = axes[1, 0].pie(
    seasonal_total.values,
    labels=None,
    colors=colors_pie,
    startangle=90,
    radius=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1}
)
# remove subplot title (use figure-level suptitle to avoid overlap)
axes[1, 0].axis('equal')
# Build legend labels that include counts and percentage values to avoid overlapping text
total = seasonal_total.values.sum()
percentages = 100.0 * seasonal_total.values / total
counts = seasonal_total.values.astype(int)
legend_labels = [f"{s}: {c} ({p:.1f}%)" for s, c, p in zip(seasonal_total.index, counts, percentages)]
# Place legend outside to the right and ensure plot area has room
axes[1, 0].legend(wedges, legend_labels, title='Season', loc='center left', bbox_to_anchor=(1.05, 0.5), fontsize=11, frameon=False)

# Plot 4: Future Predictions Bar Chart
month_labels = [pd.Timestamp(year=int(future_df.iloc[i]['Year']), 
                             month=int(future_df.iloc[i]['Month']), 
                             day=1).strftime('%b %y') for i in range(len(future_df))]
future_colors = plt.cm.Spectral(np.linspace(0, 1, len(future_df)))
bars_future = axes[1, 1].bar(range(len(future_df)), future_df['Predicted_Cases'].values, 
                           color=future_colors, edgecolor='black', linewidth=1.5)
axes[1, 1].set_xticks(range(len(future_df)))
axes[1, 1].set_xticklabels(month_labels, rotation=45, ha='right')
axes[1, 1].set_xlabel('Month-Year', fontsize=11, fontweight='bold')
axes[1, 1].set_ylabel('Predicted Cases', fontsize=11, fontweight='bold')
axes[1, 1].set_title('Dengue Case Predictions (Next 12 Months)', fontsize=12, fontweight='bold')
axes[1, 1].grid(True, alpha=0.3, axis='y')
for bar in bars_future:
    height = bar.get_height()
    axes[1, 1].text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontsize=8, fontweight='bold')

# Add a figure-level title so it sits above all subplots without overlapping
fig.suptitle('Total Dengue Cases Distribution by Season', fontsize=14, fontweight='bold', y=1.02)
# Ensure subplots have room under the suptitle
fig.subplots_adjust(top=0.88)
plt.tight_layout(rect=[0, 0, 0.78, 0.86])
plt.savefig('dengue_mlr_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Main analysis plot saved: dengue_mlr_analysis.png")
plt.close()

# Figure 2: Feature Importance & Climate
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

coef_data = pd.DataFrame({
    'Feature': features,
    'Coefficient': theta_full
})
coef_data = coef_data.sort_values('Coefficient', key=abs, ascending=False)
colors_coef = ['#FF6B6B' if x < 0 else '#4ECDC4' for x in coef_data['Coefficient']]
bars_coef = axes[0].barh(coef_data['Feature'], coef_data['Coefficient'], color=colors_coef, edgecolor='black', linewidth=1.5)
axes[0].set_xlabel('Coefficient Value (θ Parameters)', fontsize=11, fontweight='bold')
axes[0].set_title('Feature Parameters (Impact on Dengue)', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='x')
axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.8)
for bar in bars_coef:
    width = bar.get_width()
    axes[0].text(width, bar.get_y() + bar.get_height()/2.,
                 f' {width:.2f}', ha='left' if width > 0 else 'right', va='center', fontsize=10, fontweight='bold')

# Plot 2: Rainfall vs Dengue Cases
scatter = axes[1].scatter(df['RAINFALL'], df['DENGUE'], c=df['MONTH'], cmap='viridis', 
                          s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
axes[1].set_xlabel('Rainfall (mm)', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Dengue Cases', fontsize=11, fontweight='bold')
axes[1].set_title('Rainfall vs Dengue Cases (colored by month)', fontsize=12, fontweight='bold')
cbar = plt.colorbar(scatter, ax=axes[1])
cbar.set_label('Month', fontsize=10, fontweight='bold')
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('dengue_feature_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Feature analysis plot saved: dengue_feature_analysis.png")
plt.close()

# Figure 3: Seasonal Comparison
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

season_order = ['Winter', 'Pre-Monsoon', 'Monsoon', 'Post-Monsoon']
seasonal_data = [df[df['SEASON'] == s]['DENGUE'].values for s in season_order]
bp = axes[0].boxplot(seasonal_data, patch_artist=True)
axes[0].set_xticks(range(1, len(season_order) + 1))
axes[0].set_xticklabels(season_order)
for patch, color in zip(bp['boxes'], colors_pie):
    patch.set_facecolor(color)
axes[0].set_ylabel('Dengue Cases', fontsize=11, fontweight='bold')
axes[0].set_title('Dengue Distribution by Season (Box Plot)', fontsize=12, fontweight='bold')
axes[0].grid(True, alpha=0.3, axis='y')

seasonal_avg = df.groupby('SEASON')['DENGUE'].mean().reindex(season_order)
bars_seasonal = axes[1].bar(range(len(seasonal_avg)), seasonal_avg.values, color=colors_pie, edgecolor='black', linewidth=1.5)
axes[1].set_xticks(range(len(seasonal_avg)))
axes[1].set_xticklabels(seasonal_avg.index, rotation=0)
axes[1].set_ylabel('Average Cases', fontsize=11, fontweight='bold')
axes[1].set_title('Average Dengue Cases by Season', fontsize=12, fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

pivot_data = df.pivot_table(values='DENGUE', index='MONTH', columns='SEASON', aggfunc='mean').reindex(columns=season_order)
sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=axes[2], cbar_kws={'label': 'Avg Cases'}, linewidths=1)
axes[2].set_title('Average Dengue Cases (Month × Season)', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('dengue_seasonal_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Seasonal analysis plot saved: dengue_seasonal_analysis.png")
plt.close()

# 7. SUMMARY REPORT

print("\n" + "="*70)
print("SUMMARY REPORT")
print("="*70)

print(f"\nDataset Overview:")
print(f"  • Total records: {len(df)}")
print(f"  • Time period: {df['YEAR'].min()} - {df['YEAR'].max()}")
print(f"  • Total dengue cases: {df['DENGUE'].sum():,.0f}")
print(f"  • Average cases per month: {df['DENGUE'].mean():.2f}")

print(f"\nClimate-Dengue Correlations:")
correlations = df[['MIN', 'MAX', 'HUMIDITY', 'RAINFALL', 'DENGUE']].corr()['DENGUE'].drop('DENGUE')
for feature, corr in correlations.sort_values(key=abs, ascending=False).items():
    direction = "↑ Positive" if corr > 0 else "↓ Negative"
    strength = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
    print(f"  • {feature:12s}: {corr:7.4f} ({strength} {direction})")

print("\n" + "="*70)
print("ANALYSIS COMPLETE!")
print("="*70)