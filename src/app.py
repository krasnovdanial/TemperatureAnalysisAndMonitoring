import asyncio
from datetime import datetime

import aiohttp
import plotly.graph_objects as go
import streamlit as st

from analysis import calculate_season_stats, check_anomaly, load_data_cached, calculate_trend
from src.weather_api import get_weather_async
from utils.utils import get_season

st.set_page_config(page_title="Weather Anomaly Detection", layout="wide")
st.title("Анализ температурных аномалий")

st.sidebar.header("1. Данные")
uploaded_file = st.sidebar.file_uploader("Загрузите CSV с данными", type=["csv"])

if uploaded_file is not None:
    df = load_data_cached(uploaded_file)

    st.sidebar.header("2. Выбор города")
    cities = df['city'].unique()
    selected_city = st.sidebar.selectbox("Выберите город", cities)

    st.sidebar.header("3. API Weather")
    if "OPENWEATHER_API_KEY" in st.secrets:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
        st.sidebar.success("API Key получен")
    else:
        api_key = st.sidebar.text_input("Введите OpenWeatherMap API Key", type="password")
        if not api_key:
            st.sidebar.warning("Введите ключ, чтобы продолжить")

    st.header(f"Анализ исторических данных: {selected_city}")

    city_data = df[df['city'] == selected_city].sort_values('date')

    stats = calculate_season_stats(df)
    city_stats = stats[stats['city'] == selected_city]

    tab1, tab2, tab3 = st.tabs(["Временной ряд", "Сезонные профили", "Текущая погода"])

    with tab1:
        st.subheader("Временной ряд температур с аномалиями")

        merged = city_data.merge(city_stats[['season', 'mean_temperature', 'std_temperature']], on='season', how='left')

        merged['lower'] = merged['mean_temperature'] - 2 * merged['std_temperature']
        merged['upper'] = merged['mean_temperature'] + 2 * merged['std_temperature']

        merged['is_anomaly'] = (merged['temperature'] < merged['lower']) | (merged['temperature'] > merged['upper'])
        anomalies = merged[merged['is_anomaly']]

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=merged['date'], y=merged['temperature'],
                                 mode='lines', name='Температура', line=dict(color='blue', width=1)))

        fig.add_trace(go.Scatter(x=anomalies['date'], y=anomalies['temperature'],
                                 mode='markers', name='Аномалии',
                                 marker=dict(color='red', size=8, symbol='x')))

        merged['rolling_mean'] = merged['temperature'].rolling(window=30).mean()
        fig.add_trace(go.Scatter(x=merged['date'], y=merged['rolling_mean'],
                                 mode='lines', name='Скользящее среднее (30д)',
                                 line=dict(color='orange', dash='dash')))

        try:
            st.plotly_chart(fig, width="stretch")
        except Exception:
            st.plotly_chart(fig, use_container_width=True)
        trend_val = calculate_trend(city_data)
        col_trend, col_none = st.columns([1, 3])
        if trend_val is not None:
            col_trend.metric("Глобальный тренд", f"{trend_val:.2f} °C/год")

        st.write("### Описательная статистика")
        st.dataframe(city_data['temperature'].describe().T)

    with tab2:
        st.subheader("Сезонные профили (Среднее ± 2 std)")

        if not city_stats.empty:
            fig_season = go.Figure()

            for index, row in city_stats.iterrows():
                fig_season.add_trace(go.Bar(
                    x=[row['season']],
                    y=[row['mean_temperature']],
                    name=row['season'],
                    error_y=dict(type='data', array=[2 * row['std_temperature']], visible=True)
                ))

            fig_season.update_layout(title="Средняя температура по сезонам (усы = ±2 стандартных отклонения)")

            try:
                st.plotly_chart(fig_season, width="stretch")
            except:
                st.plotly_chart(fig_season, use_container_width=True)

            st.dataframe(city_stats[['season', 'mean_temperature', 'std_temperature']].style.format({
                "mean_temperature": "{:.2f}",
                "std_temperature": "{:.2f}"
            }))
        else:
            st.warning("Недостаточно данных для построения профилей")

    with tab3:
        st.subheader("Мониторинг текущей погоды")

        if not api_key:
            st.info("Введите API-ключ...")
        else:
            if st.button("Проверить сейчас"):
                with st.spinner("Запрос к API..."):
                    async def fetch_data():
                        async with aiohttp.ClientSession() as session:
                            return await get_weather_async(session, selected_city, api_key)


                    try:
                        result = asyncio.run(fetch_data())

                        if result["error"] is None:
                            current_temp = result["temp"]
                            current_season = get_season(datetime.now())

                            is_normal, lower, upper = check_anomaly(selected_city, current_temp, stats, current_season)

                            col1, col2 = st.columns(2)
                            col1.metric("Текущая температура", f"{current_temp} °C")
                            col1.caption(f"Сезон: {current_season}")

                            if is_normal:
                                col2.success("Температура в норме")
                            else:
                                col2.error("Аномалия!")
                            col2.write(f"Норма: {lower:.1f} — {upper:.1f}°C")

                        elif result["error"] == 401:
                            st.error(
                                '{"cod":401, "message": "Invalid API key. Please see https://openweathermap.org/faq#error401"}')
                        else:
                            st.error(f"Ошибка API {result['error']}: {result['message']}")

                    except Exception as e:
                        st.error(f"Системная ошибка: {e}")

else:
    st.info("Пожалуйста, загрузите CSV-файл с данными, чтобы начать анализ.")
