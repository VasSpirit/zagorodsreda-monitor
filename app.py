import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import time
import threading

# Заголовок страницы
st.set_page_config(page_title="Мониторинг голосов", layout="wide")
st.title("📊 Мониторинг голосов на Госуслугах")

# Чтение данных
@st.cache_data
def load_data():
    if os.path.exists("votes_data.csv"):
        df = pd.read_csv("votes_data.csv", encoding="utf-8")
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%d-%m-%Y %H:%M:%S")
        df["votes"] = pd.to_numeric(df["votes"].str.replace(r"\D", "", regex=True), errors="coerce").fillna(0).astype(int)
        return df
    return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("Нет данных для отображения. Сначала соберите их с помощью `main.py`.")
    st.stop()

# Кнопка автообновления
if st.button("🔁 Автообновление"):
    st.cache_data.clear()
    st.rerun()

# Боковая панель с фильтрами
with st.sidebar:
    st.header("🔍 Фильтры")
    # Выбор проектов
    selected_projects = st.multiselect("Проекты", df["title"].unique(), default=df["title"].unique())
    # Выбор диапазона дат
    date_range = st.date_input("Период", [df["timestamp"].min(), df["timestamp"].max()])

# Применение фильтров
filtered_df = df[
    (df["title"].isin(selected_projects)) &
    (df["timestamp"].dt.date >= date_range[0]) &
    (df["timestamp"].dt.date <= date_range[1])
]

# Определение последних дат периода
last_date = filtered_df["timestamp"].dt.date.max()
prev_date = last_date - pd.Timedelta(days=1)

# Выделение данных за последний день
final_day_data = filtered_df[filtered_df["timestamp"].dt.date == last_date]

# Итоги голосования за последний день
st.subheader(f"⚖️ Общий итог голосов по проектам за {last_date}")
project_votes_last_day = final_day_data.groupby('title')['votes'].last().reset_index()
project_votes_last_day.columns = ['Проект', 'Голосов за последний день']
st.table(project_votes_last_day.style.format({"Голосов за последний день": "{:,.0f}"}))

# Метрика прироста голосов
st.subheader("📌 Прирост голосов")

# Подсчет разницы голосов за вчерашний день
yesterday_votes = (
    filtered_df[(filtered_df["timestamp"].dt.date == prev_date)]
    .groupby("title")["votes"]
    .last()
    .reindex(final_day_data["title"].unique(), fill_value=0)
)

today_votes = project_votes_last_day.set_index("Проект")["Голосов за последний день"]
vote_diff_yesterday = today_votes - yesterday_votes

# Таблица прироста голосов за вчерашний день
st.write(f"Прирост голосов за **{prev_date.strftime('%d.%m.%Y')}**:")
st.table(vote_diff_yesterday.reset_index().rename(columns={0:"Прирост"}).style.format({"Прирост": "{:,.0f}"}))

# Дополнительные метрики прироста голосов
now = datetime.now()
df["hour"] = df["timestamp"].dt.floor("H")
df["day"] = df["timestamp"].dt.date
df["week"] = df["timestamp"].dt.isocalendar().week
df["month"] = df["timestamp"].dt.month

# Функция расчета прироста
def calc_delta(group_col):
    latest = df.groupby("title").last()["votes"]
    start_period = (
        df[df[group_col] == df[group_col].max()]
        .groupby("title")
        .first()["votes"]
    )
    delta = (latest - start_period).fillna(0).astype(int)
    return delta

delta_hour = calc_delta("hour")
delta_day = calc_delta("day")
delta_week = calc_delta("week")
delta_month = calc_delta("month")

# Панель с показателями прироста
cols = st.columns(4)
for i, (label, delta) in enumerate([
    ("🕐 С начала часа", delta_hour),
    ("📅 С начала дня", delta_day),
    ("📆 С начала недели", delta_week),
    ("🗓️ С начала месяца", delta_month),
]):
    total = delta.sum()
    cols[i].metric(label, f"{total:,}".replace(",", " "), delta=f"+{total}")

# Диаграмма текущего распределения голосов
st.subheader("🏆 Текущие голоса по проектам")
latest_votes = (
    filtered_df.sort_values("timestamp")
    .groupby("title")
    .last()["votes"]
    .sort_values(ascending=False)
)
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x=latest_votes.values, y=latest_votes.index, ax=ax, palette="viridis")
st.pyplot(fig)

# Таблица подробных данных
st.subheader("📋 Подробные данные")
st.dataframe(filtered_df.sort_values("timestamp", ascending=False), use_container_width=True)