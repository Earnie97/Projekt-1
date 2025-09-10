import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta

# --- Page Configuration ---
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# --- Title and Description ---
st.title("📈 Interactive Stock Analysis Dashboard")
st.markdown("""
This dashboard allows you to analyze the stock price of a selected company.
You can view the closing price, moving averages, and Bollinger Bands.
*   **Data Source:** Yahoo Finance (`yfinance`)
*   **Libraries:** Streamlit, Pandas, Plotly, yfinance
""")

# --- Sidebar for User Input ---
st.sidebar.header('User Input Parameters')

today = date.today()
default_start = today - timedelta(days=365 * 2) # Default to 2 years ago

ticker_symbol = st.sidebar.text_input("Enter Stock Ticker Symbol", "AAPL").upper()
start_date = st.sidebar.date_input("Start Date", default_start)
end_date = st.sidebar.date_input("End Date", today)

# --- Data Loading and Caching ---
@st.cache_data
def load_data(ticker, start, end):
    """
    Loads historical stock data from Yahoo Finance.
    Uses Streamlit's caching to avoid re-downloading data on every interaction.
    """
    try:
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            return None
        data.reset_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Error loading data for {ticker}: {e}")
        return None

# --- Analysis Functions ---
def calculate_moving_averages(data, short_window=20, long_window=50):
    """Calculates short and long window Simple Moving Averages (SMA)."""
    data[f'SMA_{short_window}'] = data['Close'].rolling(window=short_window).mean()
    data[f'SMA_{long_window}'] = data['Close'].rolling(window=long_window).mean()
    return data

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    """Calculates Bollinger Bands."""
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()
    data['Bollinger_High'] = rolling_mean + (rolling_std * num_std_dev)
    data['Bollinger_Low'] = rolling_mean - (rolling_std * num_std_dev)
    return data

# --- Main Application Logic ---
data = load_data(ticker_symbol, start_date, end_date)

if data is not None:
    # --- Data Transformation ---
    # Ensure the 'Date' column is in datetime format for Plotly
    data['Date'] = pd.to_datetime(data['Date'])
    # Perform analysis
    data = calculate_moving_averages(data)
    data = calculate_bollinger_bands(data)

    st.header(f"Analysis for {ticker_symbol}")

    # --- Closing Price and Moving Averages Chart ---
    st.subheader("Closing Price & Moving Averages")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Close Price', line=dict(color='royalblue')))
    fig_price.add_trace(go.Scatter(x=data['Date'], y=data['SMA_20'], mode='lines', name='SMA 20', line=dict(color='orange', dash='dash')))
    fig_price.add_trace(go.Scatter(x=data['Date'], y=data['SMA_50'], mode='lines', name='SMA 50', line=dict(color='green', dash='dash')))
    fig_price.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        legend_title='Legend',
        template='plotly_white'
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # --- Bollinger Bands Chart ---
    st.subheader("Bollinger Bands")
    fig_bb = go.Figure()
    fig_bb.add_trace(go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Close Price', line=dict(color='royalblue')))
    fig_bb.add_trace(go.Scatter(x=data['Date'], y=data['Bollinger_High'], mode='lines', name='Upper Band', line=dict(color='rgba(255,0,0,0.5)')))
    fig_bb.add_trace(go.Scatter(x=data['Date'], y=data['Bollinger_Low'], mode='lines', name='Lower Band', line=dict(color='rgba(0,128,0,0.5)'), fill='tonexty', fillcolor='rgba(0,128,0,0.1)'))
    fig_bb.update_layout(
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        legend_title='Legend',
        template='plotly_white'
    )
    st.plotly_chart(fig_bb, use_container_width=True)

    # --- Display Raw Data ---
    if st.checkbox("Show Raw Data Table"):
        st.subheader("Historical Data")
        st.dataframe(data.tail(100))
else:
    st.warning("Could not load data. Please check the ticker symbol and date range.")
