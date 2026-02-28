import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Mobile", layout="centered")

# --- СТИЛИ ДЛЯ ИДЕАЛЬНОЙ СЕТКИ ---
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    
    /* Сетка календаря 7 колонок */
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 8px;
        margin: 10px 0;
    }
    
    /* Шапка дней недели */
    .weekday-label {
        text-align: center;
        font-size: 0.7rem;
        color: #888;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Плитка дня */
    .day-tile {
        background: #1e2124;
        border: 1px solid #333;
        border-radius: 8px;
        aspect-ratio: 1/1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
        cursor: pointer;
    }
    
    .day-number {
        font-size: 1rem;
        font-weight: 500;
        color: white;
    }

    /* Точка внутри плитки */
    .day-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-top: 4px;
    }
    
    /* Стиль для выбранного дня */
    .selected-day {
        border: 2px solid #ff4b4b !important;
        background: #262730 !important;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
                d.setdefault("days", {})
                d.setdefault("templates", {})
                d.setdefault("tmpl_colors", {})
                return d
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- ЛОГИКА ВЫБОРА ДАТЫ ---
if 'active_date' not in st.session_state:
    st.session_state.active_date = datetime.now().date()

st.title("🏋️ Gym Legend")

# Выбор месяца
c1, c2 = st.columns([2, 1])
m = c1.selectbox("Месяц", range(1, 13), index=st.session_state.active_date.month-1)
y = c2.number_input("Год", value=2026)

# РЕНДЕР КАЛЕНДАРЯ
# 1. Заголовки Пн-Вс
st.markdown('<div class="calendar-grid">' + 
    ''.join([f'<div class="weekday-label">{d}</div>' for d in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]) + 
    '</div>', unsafe_allow_html=True)

# 2. Сами даты
cal = calendar.monthcalendar(y, m)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            d_str = f"{y}-{m:02d}-{day:02d}"
            
            # Определяем цвет точки
            dot_color = "transparent"
            if d_str in data["days"]:
                tmpl = data["days"][d_str].get("template")
                dot_color = data["tmpl_colors"].get(tmpl, "#58A6FF")
            
            # Рисуем плитку через кнопку (чтобы она нажималась)
            # Мы используем кастомную метку для кнопки
            if cols[i].button(f"{day}", key=f"btn_{d_str}", use_container_width=True):
                st.session_state.active_date = datetime.strptime(d_str, "%Y-%m-%d").date()
            
            # Рисуем индикатор прямо ПОД кнопкой (или внутри через CSS хак)
            st.markdown(f"""
                <div style="display: flex; justify-content: center; margin-top: -12px; margin-bottom: 10px;">
                    <div style="width: 6px; height: 6px; border-radius: 50%; background-color: {dot_color};"></div>
                </div>
            """, unsafe_allow_html=True)

st.divider()

# --- РАБОТА С ВЫБРАННЫМ ДНЕМ ---
target_date = str(st.session_state.active_date)
st.subheader(f"📅 План на {target_date}")

day_info = data["days"].get(target_date, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            ct, cb = st.columns([4, 1])
            ct.write(f"**{ex['name'].upper()}**")
            if cb.button("❌", key=f"del_{i}"):
                ex_list.pop(i)
                save_data(data)
                st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"💪 {s['w']} кг x {s['r']}")
            
            with st.expander("Добавить подход"):
                cw, cr = st.columns(2)
                w = cw.number_input("Кг", min_value=0.0, step=0.5, key=f"w_{i}")
                r = cr.number_input("Раз", min_value=0, step=1, key=f"r_{i}")
                if st.button("Записать", key=f"save_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data)
                    st.rerun()
else:
    st.info("Нет тренировок. Выбери дату выше или добавь упражнение:")

# Добавление упражнения
with st.popover("🚀 Добавить упражнение"):
    new_name = st.text_input("Название")
    if st.button("Внести"):
        if new_name:
            if target_date not in data["days"]: data["days"][target_date] = {"template": None, "exercises": []}
            data["days"][target_date]["exercises"].append({"name": new_name.strip(), "sets": []})
            save_data(data)
            st.rerun()
