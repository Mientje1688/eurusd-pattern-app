import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
from datetime import datetime

# --- Streamlit Sidebar Config ---
st.set_page_config(page_title="EUR/USD Pattern Analyzer", layout="wide")
st.title("📊 EUR/USD Pattern Analyzer")

# --- Parameters ---
PAIR = 'EURUSD'
DATA_PATH = './data'

# --- Sidebar Controls ---
available_years = list(range(2010, 2025))
year_range = st.sidebar.slider('Selecteer aantal jaren terug', 5, 15, 5)
selected_years = sorted(available_years[-year_range:])

st.sidebar.markdown(f"**Gekozen jaren:** {selected_years}")
pattern_to_detect = st.sidebar.selectbox("Kies candlestick patroon", ["Bullish Engulfing"])

# --- Functie om CSV's in te laden ---
def load_yearly_data(year):
    filepath = os.path.join(DATA_PATH, f'{PAIR}_{year}.csv')
    df = pd.read_csv(filepath)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = year
    df['DayOfYear'] = df['Date'].dt.dayofyear
    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Year', 'DayOfYear']]

# --- Data combineren ---
dataframes = []
for y in selected_years:
    try:
        dataframes.append(load_yearly_data(y))
    except FileNotFoundError:
        st.warning(f"Geen data gevonden voor jaar {y}")

df_all = pd.concat(dataframes, ignore_index=True)

# --- Plot Overlay ---
def plot_overlay(df):
    fig, ax = plt.subplots(figsize=(14, 6))
    for year in df['Year'].unique():
        yearly_df = df[df['Year'] == year]
        ax.plot(yearly_df['DayOfYear'], yearly_df['Close'], label=str(year))
    ax.set_title(f'{PAIR} - Jaarlijkse koersvergelijking')
    ax.set_xlabel('Dag van het jaar')
    ax.set_ylabel('Sluitingsprijs')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

# --- Candlestick patroon: Bullish Engulfing ---
def find_bullish_engulfing(df):
    df['Prev_Open'] = df['Open'].shift(1)
    df['Prev_Close'] = df['Close'].shift(1)
    conditions = (
        (df['Prev_Close'] < df['Prev_Open']) &
        (df['Close'] > df['Open']) &
        (df['Open'] < df['Prev_Close']) &
        (df['Close'] > df['Prev_Open'])
    )
    engulfing = df[conditions]
    return engulfing[['Date', 'Open', 'Close', 'Prev_Open', 'Prev_Close', 'Year']]

# --- Output ---
st.subheader("📈 Overlay Chart")
plot_overlay(df_all)

st.subheader("🕯️ Herkende Patronen")
if pattern_to_detect == "Bullish Engulfing":
    patterns = find_bullish_engulfing(df_all)
    st.write(f"Aantal bullish engulfing patronen: {len(patterns)}")
    st.dataframe(patterns.head(20))
