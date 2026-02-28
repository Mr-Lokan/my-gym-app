import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Mobile", layout="centered")

# --- УЛЬТРА-СТИЛЬ ДЛЯ МОБИЛЬНОЙ СЕТКИ ---
st.markdown("""
<style>
    .reportview-container .main .block-container { padding: 1rem; }
    
    /* Сетка, которая НИКОГДА не развалится */
    .gym-cal {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
        width: 100%;
        background: #0e1117;
        padding: 5px;
        border-radius: 10px;
    }
    
    .day-header {
        text-align: center;
        font-size: 10px;
        color: #888;
        font-weight: bold;
        padding: 5px 0;
    }

    /* Стиль ячейки дня */
    .day-cell {
        aspect-ratio: 1/1;
        background: #1e2124;
        border: 1px solid #333;
        border-radius: 6px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        position: relative;
        text-decoration: none;
        color: white;
    }

    .day-cell:active { background: #262c36; border-color: #58A6FF; }
    
    .cell-num { font-size: 14px; font-weight: 500; }
    
    .cell-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        margin-top: 2px;
    }

    /* Кнопки упражнений */
    div.stButton > button { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
                d.setdefault("days", {}); d.setdefault("templates", {}); d.setdefault("tmpl_colors", {})
                return d
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# Логика выбора даты
if 'active_date' not in st.session_state:
    st.session_state.active_date = datetime.now().date()

st.title("🏋️ Gym Legend")

# 1. Выбор месяца и года
c1, c2 = st.columns([2, 1])
curr_m = c1.selectbox("Месяц", range(1, 13), index=st.session_state.active_date.month-1)
curr_y = c2.number_input("Год", value=2026)

# 2. Отрисовка календаря (HTML Grid)
st.markdown('<div class="gym-cal">', unsafe_allow_html=True)
for day_name in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
    st.markdown(f'<div class="day-header">{day_name}</div>', unsafe_allow_html=True)

cal_obj = calendar.monthcalendar(curr_y, curr_m)
for week in cal_obj:
    for day in week:
        if day == 0:
            st.markdown('<div></div>', unsafe_allow_html=True)
        else:
            d_str = f"{curr_y}-{curr_m:02d}-{day:02d}"
            
            # Точка тренировки
            dot_color = "transparent"
            if d_str in data["days"]:
                tmpl = data["days"][d_str].get("template")
                dot_color = data["tmpl_colors"].get(tmpl, "#58A6FF")
            
            # Ячейка (число + точка)
            st.markdown(f"""
                <div class="day-cell">
                    <span class="cell-num">{day}</span>
                    <div class="cell-dot" style="background:{dot_color}"></div>
                </div>
            """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 3. Выбор даты через слайдер (самый надежный способ для мобилок в Streamlit)
days_in_m = calendar.monthrange(curr_y, curr_m)[1]
sel_day = st.select_slider(
    "Выбери день на шкале:", 
    options=range(1, days_in_m + 1), 
    value=st.session_state.active_date.day
)
target_date = f"{curr_y}-{curr_m:02d}-{sel_day:02d}"
st.session_state.active_date = datetime.strptime(target_date, "%Y-%m-%d").date()

st.divider()

# --- РАБОТА С ЗАПИСЯМИ ---
st.subheader(f"📅 Записи: {target_date}")
day_info = data["days"].get(target_date, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            ct, cd = st.columns([5, 1])
            ct.write(f"**{ex['name'].upper()}**")
            if cd.button("❌", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"💪 {s['w']} кг x {s['r']}")
            
            with st.expander("Добавить подход"):
                cw, cr = st.columns(2)
                w = cw.number_input("Вес", 0.0, step=0.5, key=f"w_{i}")
                r = cr.number_input("Раз", 0, step=1, key=f"r_{i}")
                if st.button("ОК", key=f"ok_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
else:
    st.info("На этот день тренировок нет.")

# Кнопка добавления упражнения
with st.popover("🚀 Добавить упражнение", use_container_width=True):
    name = st.text_input("Название")
    if st.button("Внести"):
        if name:
            if target_date not in data["days"]: data["days"][target_date] = {"template": None, "exercises": []}
            data["days"][target_date]["exercises"].append({"name": name.strip(), "sets": []})
            save_data(data); st.rerun()
