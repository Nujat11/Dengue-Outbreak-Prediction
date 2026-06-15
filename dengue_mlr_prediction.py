"""
Dengue Outbreak Prediction using Multiple Linear Regression
Features: Monthly analysis, Seasonal prediction, Future forecasting, Visualizations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 8)

# ============================================================================
# 1. LOAD AND PREPARE DATA
# ============================================================================

print("="*70)
print("DENGUE OUTBREAK PREDICTION - MULTIPLE LINEAR REGRESSION")
print("="*70)

# Load data
df = pd.read_csv('DengueOutbreakPrediction/Dataset/DengueAndClimateBangladesh.csv')
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

# ============================================================================
# 2. MULTIPLE LINEAR REGRESSION MODEL
# ============================================================================

print("\n" + "="*70)
print("MULTIPLE LINEAR REGRESSION MODEL")
print("="*70)

# Features for MLR
X = df[['MIN', 'MAX', 'HUMIDITY', 'RAINFALL']].values
y = df['DENGUE'].values

# Train MLR model
mlr_model = LinearRegression()
mlr_model.fit(X, y)

# Predictions
y_pred = mlr_model.predict(X)

# Model Performance Metrics
mse = mean_squared_error(y, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"\n📊 Model Performance Metrics:")
print(f"  • R² Score:        {r2:.4f}")
print(f"  • RMSE:            {rmse:.4f}")
print(f"  • MAE:             {mae:.4f}")
print(f"  • MSE:             {mse:.4f}")

# Feature Coefficients
print(f"\n📈 Feature Coefficients (Impact on Dengue Cases):")
features = ['MIN Temp', 'MAX Temp', 'HUMIDITY', 'RAINFALL']
for feature, coef in zip(features, mlr_model.coef_):
    print(f"  • {feature:15s}: {coef:8.4f}")
print(f"  • Intercept:       {mlr_model.intercept_:8.4f}")

# ============================================================================
# 3. MONTHLY ANALYSIS
# ============================================================================

print("\n" + "="*70)
print("MONTHLY ANALYSIS")
print("="*70)

monthly_stats = df.groupby('MONTH').agg({
    'DENGUE': ['mean', 'min', 'max', 'std'],
    'RAINFALL': 'mean',
    'HUMIDITY': 'mean',
    'MIN': 'mean',
    'MAX': 'mean'
}).round(2)

print("\n📅 Average Dengue Cases by Month:")
monthly_dengue = df.groupby('MONTH')['DENGUE'].mean().round(2)
for month, cases in monthly_dengue.items():
    month_name = pd.Timestamp(year=2020, month=int(month), day=1).strftime('%B')
    print(f"  • {month_name:12s}: {cases:8.2f} cases")

# ============================================================================
# 4. SEASONAL ANALYSIS
# ============================================================================

print("\n" + "="*70)
print("SEASONAL ANALYSIS")
print("="*70)

seasonal_stats = df.groupby('SEASON').agg({
    'DENGUE': ['mean', 'min', 'max', 'count'],
    'RAINFALL': 'mean',
    'HUMIDITY': 'mean'
}).round(2)

print("\n🌍 Dengue Cases by Season:")
seasonal_dengue = df.groupby('SEASON')['DENGUE'].mean().sort_values(ascending=False)
for season, cases in seasonal_dengue.items():
    print(f"  • {season:20s}: {cases:8.2f} cases (avg)")

# ============================================================================
# 5. FUTURE PREDICTION (Next 12 months)
# ============================================================================

print("\n" + "="*70)
print("FUTURE PREDICTIONS (Next 12 Months)")
print("="*70)

# Use last available data and create future scenarios
last_year = df['YEAR'].max()
last_month = df[df['YEAR'] == last_year]['MONTH'].max()

# Create synthetic future data (using historical averages)
future_months = []
future_data = []

for i in range(1, 13):
    month = ((last_month + i - 1) % 12) + 1
    year = last_year + (last_month + i - 1) // 12
    
    # Get average values for this month
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
future_predictions = mlr_model.predict(future_array)

print("\n🔮 Predicted Dengue Cases for Next 12 Months:")
future_df = pd.DataFrame({
    'Year': [m[0] for m in future_months],
    'Month': [m[1] for m in future_months],
    'Predicted_Cases': future_predictions.astype(int)
})

for idx, row in future_df.iterrows():
    month_name = pd.Timestamp(year=int(row['Year']), month=int(row['Month']), day=1).strftime('%B')
    print(f"  • {month_name} {int(row['Year'])}: {int(row['Predicted_Cases']):6d} cases (predicted)")

# ============================================================================
# 6. VISUALIZATIONS
# ============================================================================

print("\n" + "="*70)
print("GENERATING VISUALIZATIONS...")
print("="*70)

# Figure 1: Actual vs Predicted
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Actual vs Predicted Time Series
ax1 = axes[0, 0]
ax1.plot(df['Date'], y, 'b-', label='Actual Cases', linewidth=2)
ax1.plot(df['Date'], y_pred, 'r--', label='Predicted Cases', linewidth=2)
ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
ax1.set_ylabel('Number of Cases', fontsize=11, fontweight='bold')
ax1.set_title('Dengue Cases: Actual vs MLR Predictions', fontsize=12, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# Plot 2: Monthly Average Dengue Cases
ax2 = axes[0, 1]
monthly_dengue_sorted = df.groupby('MONTH')['DENGUE'].mean().sort_values(ascending=False)
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(monthly_dengue_sorted)))
bars = ax2.bar(range(len(monthly_dengue_sorted)), monthly_dengue_sorted.values, color=colors, edgecolor='black', linewidth=1.5)
ax2.set_xticks(range(len(monthly_dengue_sorted)))
ax2.set_xticklabels([pd.Timestamp(year=2020, month=int(m), day=1).strftime('%b') for m in monthly_dengue_sorted.index])
ax2.set_xlabel('Month', fontsize=11, fontweight='bold')
ax2.set_ylabel('Average Cases', fontsize=11, fontweight='bold')
ax2.set_title('Average Dengue Cases by Month (Ranked)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}', ha='center', va='bottom', fontsize=9, fontweight='bold')

# Plot 3: Seasonal Analysis (Pie Chart)
ax3 = axes[1, 0]
seasonal_total = df.groupby('SEASON')['DENGUE'].sum()
colors_pie = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
wedges, texts, autotexts = ax3.pie(seasonal_total.values, labels=seasonal_total.index, autopct='%1.1f%%',
                                     colors=colors_pie, startangle=90, textprops={'fontsize': 10, 'fontweight': 'bold'})
ax3.set_title('Total Dengue Cases Distribution by Season', fontsize=12, fontweight='bold')
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

# Plot 4: Future Predictions Bar Chart
ax4 = axes[1, 1]
month_labels = [pd.Timestamp(year=int(future_df.iloc[i]['Year']), 
                             month=int(future_df.iloc[i]['Month']), 
                             day=1).strftime('%b %y') for i in range(len(future_df))]
future_colors = plt.cm.Spectral(np.linspace(0, 1, len(future_df)))
bars_future = ax4.bar(range(len(future_df)), future_df['Predicted_Cases'].values, 
                      color=future_colors, edgecolor='black', linewidth=1.5)
ax4.set_xticks(range(len(future_df)))
ax4.set_xticklabels(month_labels, rotation=45, ha='right')
ax4.set_xlabel('Month-Year', fontsize=11, fontweight='bold')
ax4.set_ylabel('Predicted Cases', fontsize=11, fontweight='bold')
ax4.set_title('Dengue Case Predictions (Next 12 Months)', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
for bar in bars_future:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}', ha='center', va='bottom', fontsize=8, fontweight='bold')

plt.tight_layout()
plt.savefig('dengue_mlr_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Main analysis plot saved: dengue_mlr_analysis.png")
plt.close()

# Figure 2: Feature Importance
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Plot 1: Feature Coefficients
ax1 = axes[0]
coef_data = pd.DataFrame({
    'Feature': features,
    'Coefficient': mlr_model.coef_
})
coef_data = coef_data.sort_values('Coefficient', key=abs, ascending=False)
colors_coef = ['#FF6B6B' if x < 0 else '#4ECDC4' for x in coef_data['Coefficient']]
bars_coef = ax1.barh(coef_data['Feature'], coef_data['Coefficient'], color=colors_coef, edgecolor='black', linewidth=1.5)
ax1.set_xlabel('Coefficient Value', fontsize=11, fontweight='bold')
ax1.set_title('Feature Coefficients (Impact on Dengue)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='x')
ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
for bar in bars_coef:
    width = bar.get_width()
    ax1.text(width, bar.get_y() + bar.get_height()/2.,
             f' {width:.2f}', ha='left' if width > 0 else 'right', va='center', fontsize=10, fontweight='bold')

# Plot 2: Rainfall vs Dengue Cases
ax2 = axes[1]
scatter = ax2.scatter(df['RAINFALL'], df['DENGUE'], c=df['MONTH'], cmap='viridis', 
                     s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
ax2.set_xlabel('Rainfall (mm)', fontsize=11, fontweight='bold')
ax2.set_ylabel('Dengue Cases', fontsize=11, fontweight='bold')
ax2.set_title('Rainfall vs Dengue Cases (colored by month)', fontsize=12, fontweight='bold')
cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('Month', fontsize=10, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Add trend line
z = np.polyfit(df['RAINFALL'], df['DENGUE'], 2)
p = np.poly1d(z)
x_trend = np.linspace(df['RAINFALL'].min(), df['RAINFALL'].max(), 100)
ax2.plot(x_trend, p(x_trend), "r--", linewidth=2, label='Trend')
ax2.legend(fontsize=10)

plt.tight_layout()
plt.savefig('dengue_feature_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Feature analysis plot saved: dengue_feature_analysis.png")
plt.close()

# Figure 3: Seasonal Comparison
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Plot 1: Seasonal Box Plot
ax1 = axes[0]
season_order = ['Winter', 'Pre-Monsoon', 'Monsoon', 'Post-Monsoon']
seasonal_data = [df[df['SEASON'] == s]['DENGUE'].values for s in season_order]
bp = ax1.boxplot(seasonal_data, labels=season_order, patch_artist=True)
for patch, color in zip(bp['boxes'], colors_pie):
    patch.set_facecolor(color)
ax1.set_ylabel('Dengue Cases', fontsize=11, fontweight='bold')
ax1.set_title('Dengue Distribution by Season (Box Plot)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3, axis='y')

# Plot 2: Seasonal Average Bar Chart
ax2 = axes[1]
seasonal_avg = df.groupby('SEASON')['DENGUE'].mean().reindex(season_order)
bars_seasonal = ax2.bar(range(len(seasonal_avg)), seasonal_avg.values, color=colors_pie, edgecolor='black', linewidth=1.5)
ax2.set_xticks(range(len(seasonal_avg)))
ax2.set_xticklabels(seasonal_avg.index, rotation=0)
ax2.set_ylabel('Average Cases', fontsize=11, fontweight='bold')
ax2.set_title('Average Dengue Cases by Season', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')
for bar in bars_seasonal:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height)}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# Plot 3: Temperature vs Humidity Heatmap
ax3 = axes[2]
pivot_data = df.pivot_table(values='DENGUE', index='MONTH', columns='SEASON', aggfunc='mean')
pivot_data = pivot_data[season_order]  # Reorder columns
sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax3, cbar_kws={'label': 'Avg Cases'}, linewidths=1)
ax3.set_title('Average Dengue Cases (Month × Season)', fontsize=12, fontweight='bold')
ax3.set_ylabel('Month', fontsize=11, fontweight='bold')
ax3.set_xlabel('Season', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('dengue_seasonal_analysis.png', dpi=300, bbox_inches='tight')
print("✓ Seasonal analysis plot saved: dengue_seasonal_analysis.png")
plt.close()

# ============================================================================
# 7. SUMMARY REPORT
# ============================================================================

print("\n" + "="*70)
print("SUMMARY REPORT")
print("="*70)

print(f"\n📋 Dataset Overview:")
print(f"  • Total records: {len(df)}")
print(f"  • Time period: {df['YEAR'].min()} - {df['YEAR'].max()}")
print(f"  • Total dengue cases: {df['DENGUE'].sum():,.0f}")
print(f"  • Average cases per month: {df['DENGUE'].mean():.2f}")

print(f"\n🎯 High-Risk Months:")
high_risk = df.groupby('MONTH')['DENGUE'].mean().nlargest(3)
for idx, (month, cases) in enumerate(high_risk.items(), 1):
    month_name = pd.Timestamp(year=2020, month=int(month), day=1).strftime('%B')
    print(f"  {idx}. {month_name:12s}: {cases:8.2f} average cases")

print(f"\n🔴 High-Risk Seasons (by total cases):")
high_seasons = df.groupby('SEASON')['DENGUE'].sum().sort_values(ascending=False)
for idx, (season, cases) in enumerate(high_seasons.items(), 1):
    print(f"  {idx}. {season:20s}: {int(cases):,} total cases")

print(f"\n📊 Climate-Dengue Correlations:")
correlations = df[['MIN', 'MAX', 'HUMIDITY', 'RAINFALL', 'DENGUE']].corr()['DENGUE'].drop('DENGUE')
for feature, corr in correlations.sort_values(key=abs, ascending=False).items():
    direction = "↑ Positive" if corr > 0 else "↓ Negative"
    strength = "Strong" if abs(corr) > 0.5 else "Moderate" if abs(corr) > 0.3 else "Weak"
    print(f"  • {feature:12s}: {corr:7.4f} ({strength} {direction})")

print(f"\n📈 Future Outlook (Next 12 Months):")
print(f"  • Total predicted cases: {int(future_df['Predicted_Cases'].sum()):,}")
print(f"  • Average per month: {int(future_df['Predicted_Cases'].mean()):.0f}")
print(f"  • Highest risk month: {future_df.loc[future_df['Predicted_Cases'].idxmax(), ['Year', 'Month', 'Predicted_Cases']].values}")

print("\n" + "="*70)
print("✅ ANALYSIS COMPLETE!")
print("="*70)
print("\n📁 Generated Files:")
print("  • dengue_mlr_analysis.png")
print("  • dengue_feature_analysis.png")
print("  • dengue_seasonal_analysis.png")
print("\n")
