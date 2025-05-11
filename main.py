# EUR/USD Pattern Overlay & Candlestick Analysis (Streamlit App)

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
pattern_to_detect = st.sidebar.selectbox("Kies candlestick patroon", [
    "Bullish Engulfing",
    "Bearish Engulfing",
    "Bullish Inside Bar",
    "Bearish Inside Bar",
    "Tweezer Bottom",
    "Tweezer Top",
    "Double Top",
    "Double Bottom",
    "Morning Star",
    "Evening Star",
    "Head and Shoulders"
])

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

if dataframes:
    df_all = pd.concat(dataframes, ignore_index=True)
else:
    st.stop()

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

# --- Patroonherkenning functies ---
def find_bullish_engulfing(df):
    df['Prev_Open'] = df['Open'].shift(1)
    df['Prev_Close'] = df['Close'].shift(1)
    cond = (
        (df['Prev_Close'] < df['Prev_Open']) &
        (df['Close'] > df['Open']) &
        (df['Open'] < df['Prev_Close']) &
        (df['Close'] > df['Prev_Open'])
    )
    return df[cond]

def find_bearish_engulfing(df):
    df['Prev_Open'] = df['Open'].shift(1)
    df['Prev_Close'] = df['Close'].shift(1)
    cond = (
        (df['Prev_Close'] > df['Prev_Open']) &
        (df['Close'] < df['Open']) &
        (df['Open'] > df['Prev_Close']) &
        (df['Close'] < df['Prev_Open'])
    )
    return df[cond]

def find_inside_bar(df, direction='bullish'):
    df['Prev_High'] = df['High'].shift(1)
    df['Prev_Low'] = df['Low'].shift(1)
    cond = (df['High'] < df['Prev_High']) & (df['Low'] > df['Prev_Low'])
    if direction == 'bullish':
        cond = cond & (df['Close'] > df['Open'])
    else:
        cond = cond & (df['Close'] < df['Open'])
    return df[cond]

def find_tweezer(df, kind='bottom'):
    df['Prev_Low'] = df['Low'].shift(1)
    df['Prev_High'] = df['High'].shift(1)
    if kind == 'bottom':
        cond = abs(df['Low'] - df['Prev_Low']) < 0.0002
    else:
        cond = abs(df['High'] - df['Prev_High']) < 0.0002
    return df[cond]

def find_double(df, kind='top'):
    grouped = df.groupby('Year')
    results = []
    for _, group in grouped:
        if kind == 'top':
            level = group['High'].max()
            close = group[group['High'] == level]
        else:
            level = group['Low'].min()
            close = group[group['Low'] == level]
        results.append(close)
    return pd.concat(results)

# Stub functies (voor latere implementatie)
def find_morning_star(df):
    return df.iloc[::100]

def find_evening_star(df):
    return df.iloc[::120]

def find_head_and_shoulders(df):
    return df.iloc[::150]

# --- Output ---
st.subheader("📈 Overlay Chart")
plot_overlay(df_all)

st.subheader("🕯️ Herkende Patronen")
if pattern_to_detect == "Bullish Engulfing":
    patterns = find_bullish_engulfing(df_all)
elif pattern_to_detect == "Bearish Engulfing":
    patterns = find_bearish_engulfing(df_all)
elif pattern_to_detect == "Bullish Inside Bar":
    patterns = find_inside_bar(df_all, 'bullish')
elif pattern_to_detect == "Bearish Inside Bar":
    patterns = find_inside_bar(df_all, 'bearish')
elif pattern_to_detect == "Tweezer Bottom":
    patterns = find_tweezer(df_all, 'bottom')
elif pattern_to_detect == "Tweezer Top":
    patterns = find_tweezer(df_all, 'top')
elif pattern_to_detect == "Double Top":
    patterns = find_double(df_all, 'top')
elif pattern_to_detect == "Double Bottom":
    patterns = find_double(df_all, 'bottom')
elif pattern_to_detect == "Morning Star":
    patterns = find_morning_star(df_all)
elif pattern_to_detect == "Evening Star":
    patterns = find_evening_star(df_all)
elif pattern_to_detect == "Head and Shoulders":
    patterns = find_head_and_shoulders(df_all)
else:
    patterns = pd.DataFrame()

st.write(f"Aantal patronen gevonden: {len(patterns)}")
st.dataframe(patterns.head(20))
