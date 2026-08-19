"""Chronological XGBoost forecast of daily retail sales value."""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "fact_sales.csv"
OUT = ROOT / "data" / "processed"


def main():
    fact = pd.read_csv(DATA)
    dates = pd.to_datetime(fact["order_date_key"].astype(str), format="%Y%m%d")
    daily = fact.assign(order_date=dates).groupby("order_date", as_index=False)["sales"].sum()
    daily = daily.set_index("order_date").asfreq("D", fill_value=0).reset_index()

    daily["day_of_week"] = daily["order_date"].dt.dayofweek
    daily["month"] = daily["order_date"].dt.month
    daily["quarter"] = daily["order_date"].dt.quarter
    daily["trend"] = np.arange(len(daily))
    daily["lag_1"] = daily["sales"].shift(1)
    daily["lag_7"] = daily["sales"].shift(7)
    daily["lag_14"] = daily["sales"].shift(14)
    daily["rolling_7"] = daily["sales"].shift(1).rolling(7).mean()
    daily["rolling_28"] = daily["sales"].shift(1).rolling(28).mean()
    daily = daily.dropna().reset_index(drop=True)

    feature_cols = ["day_of_week", "month", "quarter", "trend", "lag_1", "lag_7", "lag_14", "rolling_7", "rolling_28"]
    test_size = min(30, max(7, len(daily) // 5))
    train = daily.iloc[:-test_size]
    test = daily.iloc[-test_size:]

    model = XGBRegressor(
        n_estimators=400, max_depth=5, learning_rate=0.05,
        subsample=0.85, colsample_bytree=0.85, objective="reg:squarederror",
        random_state=42
    )
    model.fit(train[feature_cols], train["sales"])
    pred = model.predict(test[feature_cols])

    mae = mean_absolute_error(test["sales"], pred)
    rmse = mean_squared_error(test["sales"], pred) ** 0.5

    result = test[["order_date", "sales"]].copy()
    result["predicted_sales"] = pred
    result["absolute_error"] = (result["sales"] - result["predicted_sales"]).abs()
    result.to_csv(OUT / "sales_forecast.csv", index=False)
    pd.DataFrame([{"mae": mae, "rmse": rmse, "test_rows": test_size}]).to_csv(OUT / "forecast_metrics.csv", index=False)

    print(f"Forecast complete | MAE={mae:.2f} | RMSE={rmse:.2f}")


if __name__ == "__main__":
    main()
