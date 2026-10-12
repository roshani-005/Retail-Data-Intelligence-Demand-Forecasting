"""Chronological daily-sales forecast benchmark: seasonal naive vs XGBoost."""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "fact_sales.csv"
OUT = ROOT / "data" / "processed"


def metric_summary(y_true, y_pred):
    """Return MAE, RMSE and MAPE over non-zero actual values."""
    actual = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    mae = float(mean_absolute_error(actual, predicted))
    rmse = float(mean_squared_error(actual, predicted) ** 0.5)
    nonzero = actual != 0
    mape = (
        float(np.mean(np.abs((actual[nonzero] - predicted[nonzero]) / actual[nonzero])) * 100)
        if nonzero.any()
        else float("nan")
    )
    return {"mae": mae, "rmse": rmse, "mape_pct": mape, "mape_rows": int(nonzero.sum())}


def pct_improvement(baseline, model):
    """Positive values mean the model's error is lower than the baseline."""
    if baseline == 0 or not np.isfinite(baseline) or not np.isfinite(model):
        return float("nan")
    return float((baseline - model) / baseline * 100)


def build_daily_series(fact):
    dates = pd.to_datetime(fact["order_date_key"].astype(str), format="%Y%m%d")
    daily = fact.assign(order_date=dates).groupby("order_date", as_index=False)["sales"].sum()
    daily = daily.set_index("order_date").asfreq("D", fill_value=0).reset_index()
    return daily


def main():
    if not DATA.exists():
        raise FileNotFoundError(
            f"Curated sales file not found: {DATA}. Run src/etl.py first and provide "
            "the public Superstore CSV at data/raw/superstore.csv."
        )

    fact = pd.read_csv(DATA)
    daily = build_daily_series(fact)

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

    feature_cols = [
        "day_of_week", "month", "quarter", "trend", "lag_1", "lag_7",
        "lag_14", "rolling_7", "rolling_28",
    ]
    test_size = min(30, max(7, len(daily) // 5))
    if len(daily) <= test_size:
        raise ValueError(
            f"Not enough daily observations ({len(daily)}) for a chronological train/test split."
        )

    train = daily.iloc[:-test_size]
    test = daily.iloc[-test_size:]

    model = XGBRegressor(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=2,
    )
    model.fit(train[feature_cols], train["sales"])
    xgb_pred = model.predict(test[feature_cols])
    naive_pred = test["lag_7"].to_numpy(dtype=float)

    baseline_metrics = metric_summary(test["sales"], naive_pred)
    model_metrics = metric_summary(test["sales"], xgb_pred)

    rows = []
    for model_name, metrics in [
        ("Seasonal naive (same weekday last week)", baseline_metrics),
        ("XGBoost", model_metrics),
    ]:
        rows.append({
            "model": model_name,
            **metrics,
            "train_rows": int(len(train)),
            "test_rows": int(len(test)),
            "feature_count": len(feature_cols),
            "daily_series_rows": int(len(daily)),
            "mae_improvement_pct": float("nan"),
            "rmse_improvement_pct": float("nan"),
            "mape_improvement_pct": float("nan"),
        })

    rows[1]["mae_improvement_pct"] = pct_improvement(baseline_metrics["mae"], model_metrics["mae"])
    rows[1]["rmse_improvement_pct"] = pct_improvement(baseline_metrics["rmse"], model_metrics["rmse"])
    rows[1]["mape_improvement_pct"] = pct_improvement(
        baseline_metrics["mape_pct"], model_metrics["mape_pct"]
    )
    pd.DataFrame(rows).to_csv(OUT / "forecast_metrics.csv", index=False)

    result = test[["order_date", "sales"]].copy()
    result["seasonal_naive_sales"] = naive_pred
    result["predicted_sales"] = xgb_pred
    result["absolute_error_xgboost"] = (result["sales"] - result["predicted_sales"]).abs()
    result["absolute_error_naive"] = (result["sales"] - result["seasonal_naive_sales"]).abs()
    result.to_csv(OUT / "sales_forecast.csv", index=False)

    print(f"Forecast complete | train_rows={len(train)} | test_rows={len(test)} | features={len(feature_cols)}")
    for row in rows:
        print(
            f"{row['model']}: MAE={row['mae']:.2f}, RMSE={row['rmse']:.2f}, "
            f"MAPE={row['mape_pct']:.2f}% (non-zero actuals n={row['mape_rows']})"
        )
    print(
        f"Improvement vs seasonal naive: MAE={rows[1]['mae_improvement_pct']:.2f}%, "
        f"RMSE={rows[1]['rmse_improvement_pct']:.2f}%"
    )


if __name__ == "__main__":
    main()
