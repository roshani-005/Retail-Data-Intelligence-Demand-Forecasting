from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"
OUTPUTS.mkdir(parents=True, exist_ok=True)

sales = pd.read_csv(PROCESSED / "fact_sales.csv", parse_dates=["order_date"])
daily = (
    sales.groupby(["order_date", "product_id"], as_index=False)["quantity"]
    .sum()
    .rename(columns={"quantity": "demand"})
)

# Build a complete daily grid per product so lags have consistent meaning.
all_dates = pd.date_range(daily.order_date.min(), daily.order_date.max(), freq="D")
products = daily.product_id.unique()
grid = pd.MultiIndex.from_product([all_dates, products], names=["order_date", "product_id"]).to_frame(index=False)
daily = grid.merge(daily, on=["order_date", "product_id"], how="left")
daily["demand"] = daily["demand"].fillna(0)

daily = daily.sort_values(["product_id", "order_date"]).reset_index(drop=True)
daily["day_of_week"] = daily.order_date.dt.dayofweek
daily["month"] = daily.order_date.dt.month
daily["trend"] = (daily.order_date - daily.order_date.min()).dt.days
for lag in [1, 7, 14]:
    daily[f"lag_{lag}"] = daily.groupby("product_id")["demand"].shift(lag)
daily["rolling_7"] = daily.groupby("product_id")["demand"].transform(lambda s: s.shift(1).rolling(7).mean())
daily = daily.dropna().copy()

features = ["product_id", "day_of_week", "month", "trend", "lag_1", "lag_7", "lag_14", "rolling_7"]
cutoff = daily.order_date.max() - pd.Timedelta(days=30)
train = daily[daily.order_date < cutoff]
test = daily[daily.order_date >= cutoff]

model = XGBRegressor(
    n_estimators=350,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42,
)
model.fit(train[features], train["demand"])
pred = np.clip(model.predict(test[features]), 0, None)

mae = mean_absolute_error(test["demand"], pred)
rmse = np.sqrt(mean_squared_error(test["demand"], pred))
results = test[["order_date", "product_id", "demand"]].copy()
results["predicted_demand"] = pred
results["absolute_error"] = np.abs(results["demand"] - results["predicted_demand"])
results.to_csv(OUTPUTS / "demand_forecast.csv", index=False)
pd.DataFrame({"metric": ["MAE", "RMSE"], "value": [mae, rmse]}).to_csv(OUTPUTS / "forecast_metrics.csv", index=False)

# A simple business recommendation dataset for BI consumption.
product_summary = results.groupby("product_id", as_index=False).agg(
    actual_demand=("demand", "sum"),
    forecast_demand=("predicted_demand", "sum"),
)
product_summary["forecast_gap"] = product_summary["forecast_demand"] - product_summary["actual_demand"]
product_summary["recommendation"] = np.select(
    [product_summary.forecast_gap > 5, product_summary.forecast_gap < -5],
    ["Review replenishment capacity", "Review stock and demand drivers"],
    default="Monitor demand",
)
product_summary.to_csv(OUTPUTS / "business_recommendations.csv", index=False)
print(f"XGBoost complete | MAE={mae:.2f} | RMSE={rmse:.2f}")
