import os
import sys
from pathlib import Path

import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
import streamlit as st

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.utils import get_season


@st.cache_data
def load_data_cached(uploaded_file):
    return load_weather_data(uploaded_file)


def load_weather_data(filepath: Path):
    df = pd.read_csv(filepath)

    if 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp'])
    elif 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    df['season'] = df['date'].apply(get_season)
    return df


def calculate_season_stats(df: pd.DataFrame):
    stats = df.groupby(['city', 'season'])['temperature'].agg(['mean', 'std']).reset_index()
    stats.rename(columns={'mean': 'mean_temperature', 'std': 'std_temperature'}, inplace=True)
    return stats


def check_anomaly(city: str, current_temp: float, profiles: pd.DataFrame, current_season: str):
    row = profiles[(profiles['city'] == city) & (profiles['season'] == current_season)]

    if row.empty:
        return False, 0.0, 0.0

    mean = row.iloc[0]['mean_temperature']
    std = row.iloc[0]['std_temperature']

    lower = mean - 2 * std
    upper = mean + 2 * std

    is_normal = (lower <= current_temp <= upper)

    return is_normal, lower, upper


def calculate_trend(df_city: pd.DataFrame):
    temp_df = df_city.dropna(subset=['temperature'])
    if temp_df.empty:
        return 0.0

    temp_df = temp_df.copy()

    if 'timestamp' in temp_df.columns:
        if not pd.api.types.is_datetime64_any_dtype(temp_df['timestamp']):
            temp_df['timestamp'] = pd.to_datetime(temp_df['timestamp'])

        temp_df['date_ordinal'] = temp_df['timestamp'].map(pd.Timestamp.toordinal)
    else:
        if 'date' in temp_df.columns:
            temp_df['date_ordinal'] = pd.to_datetime(temp_df['date']).map(pd.Timestamp.toordinal)
        else:
            return 0.0

    X = temp_df[['date_ordinal']]
    y = temp_df['temperature']

    model = LinearRegression()
    model.fit(X, y)

    return model.coef_[0] * 365


def analyze_city_data(df_city: pd.DataFrame):
    df = df_city.copy()

    if 'date' in df.columns:
        df = df.sort_values('date')

    df['rolling_mean'] = df['temperature'].rolling(window=30, min_periods=1).mean()
    df['rolling_std'] = df['temperature'].rolling(window=30, min_periods=1).std()

    df['lower_bound'] = df['rolling_mean'] - 2 * df['rolling_std']
    df['upper_bound'] = df['rolling_mean'] + 2 * df['rolling_std']

    df['is_anomaly'] = (df['temperature'] < df['lower_bound']) | \
                       (df['temperature'] > df['upper_bound'])

    df['trend_long'] = df['temperature'].rolling(window=365, min_periods=180, center=True).mean()

    return df


def temperature_trend_plot(city_name: str, full_data: pd.DataFrame):
    full_data = full_data.copy()
    name = city_name.title()
    city_data = full_data[full_data['city'] == name]

    if city_data.empty:
        print(f"Город {name} не найден в данных.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(city_data['date'], city_data['temperature'], label='Температура', alpha=0.3)
    plt.plot(city_data['date'], city_data['rolling_mean'], label='Скользящее среднее (30 дней)', color='orange')
    plt.plot(city_data['date'], city_data['trend_long'], label='Годовой тренд', color='green', linewidth=2)

    anomalies = city_data[city_data['is_anomaly']]
    plt.scatter(anomalies['date'], anomalies['temperature'], color='red', s=10, label='Аномалии')

    plt.legend()
    plt.grid(True)
    plt.title(f"График изменения температуры в г. {name}")
    plt.show()
