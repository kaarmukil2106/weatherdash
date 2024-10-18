import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime, timedelta

# Title
st.title("Stock Price Prediction")

# Select stock
ticker = st.text_input("Enter the stock ticker (e.g., AAPL, TSLA, MSFT):", "AAPL")

# Date range
start_date = st.date_input("Select start date:", datetime(2015, 1, 1))
end_date = st.date_input("Select end date:", datetime.now())

# Fetch stock data
data = yf.download(ticker, start=start_date, end=end_date)

# Show data
st.write("### Stock Data", data.head())

# Plot stock price
st.write("### Historical Stock Prices")
fig, ax = plt.subplots()
ax.plot(data.index, data['Close'])
ax.set_title(f"{ticker} Stock Prices")
ax.set_xlabel("Date")
ax.set_ylabel("Price (USD)")
st.pyplot(fig)

# Simple Linear Regression Model for Prediction
if st.button("Predict Next 7 Days"):
    # Use closing price as feature
    data['Date'] = pd.to_datetime(data.index)
    data['Days'] = (data['Date'] - data['Date'].min()).dt.days

    X = data['Days'].values.reshape(-1, 1)
    y = data['Close'].values

    model = LinearRegression()
    model.fit(X, y)

    # Predict next 7 days
    future_days = np.arange(data['Days'].max() + 1, data['Days'].max() + 8).reshape(-1, 1)
    future_predictions = model.predict(future_days)

    future_dates = pd.date_range(start=data.index[-1] + timedelta(days=1), periods=7).to_list()

    # Plot predictions
    st.write("### Predicted Stock Prices for Next 7 Days")
    fig, ax = plt.subplots()
    ax.plot(data.index, data['Close'], label="Historical Prices")
    ax.plot(future_dates, future_predictions, label="Predicted Prices", color='red')
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.set_title(f"Predicted Prices for {ticker}")
    ax.legend()
    st.pyplot(fig)