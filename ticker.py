from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from polygon import RESTClient
import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
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
async def get_stock_data(
    ticker: str = "AAPL", 
    start: str = "2021-06-01", 
    end: str = "2025-02-06", 
    predict_days: int = 90, 
    predict_unit: str = "days"
):
    client = RESTClient(api_key=API_KEY)
    aggs = []

    try:
        # ✅ Fetch stock data
        for a in client.list_aggs(ticker, 1, "day", start, end, limit=50000):
            aggs.append({
                "date": a.timestamp,  
                "open": a.open,       
                "close": a.close,     
                "high": a.high,       
                "low": a.low          
            })

        df_data = pd.DataFrame(aggs)

        if df_data.empty:
            raise HTTPException(status_code=404, detail="No stock data found.")

        # ✅ Convert timestamp to datetime
        df_data["date"] = pd.to_datetime(df_data["date"], unit='ms')
        df_data["date_numeric"] = df_data["date"].map(datetime.toordinal)

        # ✅ Get last known stock price
        last_known_price = df_data["close"].iloc[-1]

        # ✅ Prepare X and y for Linear Regression
        X = df_data["date_numeric"].values.reshape(-1, 1)
        y = df_data["close"].values.reshape(-1, 1)

        # ✅ Train the Linear Regression model
        model = LinearRegression()
        model.fit(X, y)

        # ✅ Convert months/years to days
        if predict_unit == "months":
            predict_days *= 30
        elif predict_unit == "years":
            predict_days *= 365

        # ✅ Ensure predictions start from today
        today = datetime.today()
        future_dates = [(today + timedelta(days=i)).toordinal() for i in range(1, predict_days + 1)]
        future_dates = np.array(future_dates).reshape(-1, 1)

        # ✅ Predict future stock prices
        future_prices = model.predict(future_dates)

        # ✅ Ensure today's date has the last known stock price
        future_predictions = [{"date": today.strftime("%Y-%m-%d"), "predictedClose": float(last_known_price)}]

        # ✅ Append future predicted prices starting from tomorrow
        future_predictions += [
            {"date": (today + timedelta(days=i)).strftime("%Y-%m-%d"), "predictedClose": float(future_prices[i-1])}
            for i in range(1, predict_days + 1)
        ]

        return {
            "historicalData": aggs,
            "futurePredictions": future_predictions
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))