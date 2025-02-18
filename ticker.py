from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from polygon import RESTClient
import numpy as np
import pandas as pd
import os
from datetime import datetime
from sklearn.linear_model import LinearRegression

app = FastAPI()

# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "LrOxo7sdeDLQPp9wQx6xDnk7u97bnppt"  # Replace with your actual API Key

@app.get("/stock")
async def get_stock_data(ticker: str = "AAPL", start: str = "2021-06-01", end: str = "2025-02-06", predict_days: int = 90, predict_unit: str = "days"):
    client = RESTClient(api_key=API_KEY)
    aggs = []
    predictDays = predict_days

    try:
        # Fetch stock data
        for a in client.list_aggs(ticker, 1, "day", start, end, limit=50000):
            aggs.append({
                "date": a.timestamp,  # Date
                "open": a.open,        # Open price
                "close": a.close,      # Close price
                "high": a.high,        # High price
                "low": a.low           # Low price
            })

        df_data = pd.DataFrame(aggs)
        
        # Convert timestamp to numerical format
        df_data["date"] = pd.to_datetime(df_data["date"], unit='ms')
        df_data["date_numeric"] = df_data["date"].map(datetime.toordinal)

        # Prepare X and y
        X = df_data["date_numeric"].values.reshape(-1, 1)
        y = df_data["close"].values.reshape(-1, 1)

        # Train a linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Convert months/years to days
        if predict_unit == "months":
            predictDays = predict_days * 30
        elif predict_unit == "years":
            predictDays = predict_days * 365
        else:
            predictDays = predict_days

        # Predict future stock prices
        last_date = df_data["date"].max()
        future_dates = [(last_date + pd.Timedelta(days=i)).toordinal() for i in range(1, predictDays + 1)]
        future_prices = model.predict(np.array(future_dates).reshape(-1, 1))

        # Convert back to readable dates
        future_predictions = [{"date": (last_date + pd.Timedelta(days=i)).strftime("%Y-%m-%d"), "predictedClose": float(future_prices[i-1])} for i in range(1, predictDays + 1)]

        return {
            "historicalData": aggs,
            "futurePredictions": future_predictions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
