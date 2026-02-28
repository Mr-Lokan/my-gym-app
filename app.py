import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Elite", layout="centered")

# --- УЛЬТРА-СТИЛЬНЫЙ CSS ---
st.markdown("""
<style>
    .cal-wrapper {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
        background: #161b22;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #30363d;
    }
    .wd-label {
        text-align: center;
        font-size: 10px;
        color: #8b949e;
        font-weight: 600;
        padding-bottom: 5px;
    }
    .day-box {
        aspect-ratio: 1/1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #21262d;
        border-radius: 8px;
        border: 1px solid #30363d;
        position: relative;
    }
    .day-num { font-size: 14px; font-weight: bold; color: #c9d1d9; }
    .day-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-top: 4px;
    }
    .selected-marker {
        border: 2px solid #58a6ff !important;
        background: #262c36 !important;
    }
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

# --- ЛОГИКА ---
if 'sel_date' not in st.session_state:
    st.session_state.sel_date = datetime.now().strftime("%Y-%m-%d")

st.title("🏋️ GYM LEGEND")

# Выбор месяца (компактно)
c1, c2 = st.columns([2, 1])
m_idx = c1.selectbox("Месяц", range(1, 13), index=datetime.now().month-1)
y_val = c2.number_input("Год", value=2026)

# РЕНДЕР КАЛЕНДАРЯ ЧЕРЕЗ HTML
st.markdown('<div class="cal-wrapper">', unsafe_allow_html=True)
# Заголовки
for wd in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
    st.markdown(f'<div class="wd-label">{wd}</div>', unsafe_allow_html=True)

cal_obj = calendar.monthcalendar(y_val, m_idx)
for week in cal_obj:
    for day in week:
        if day == 0:
            st.markdown('<div></div>', unsafe_allow_html=True) # Пустая ячейка
        else:
            d_str = f"{y_val}-{m_idx:02d}-{day:02d}"
            
            # Ищем цвет тренировки
            dot_color = "transparent"
            if d_str in data["days"]:
                t_name = data["days"][d_str].get("template")
                dot_color = data["tmpl_colors"].get(t_name, "#58A6FF")
            
            # Выделение выбранного дня
            is_sel = "selected-marker" if d_str == st.session_state.sel_date else ""
            
            # Рисуем ячейку
            st.markdown(f"""
                <div class="day-box {is_sel}">
                    <div class="day-num">{day}</div>
                    <div class="day-dot" style="background: {dot_color}"></div>
                </div>
            """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Чтобы "нажимать" на даты на мобилке, добавим аккуратный слайдер под календарем
days_in_month = calendar.monthrange(y_val, m_idx)[1]
day_sel = st.select_slider("Переключить дату:", options=range(1, days_in_month + 1), value=int(st.session_state.sel_date.split('-')[-1]))
st.session_state.sel_date = f"{y_val}-{m_idx:02d}-{day_sel:02d}"

st.divider()

# --- РАБОТА С УПРАЖНЕНИЯМИ ---
curr_d = st.session_state.sel_date
st.subheader(f"📅 Дата: {curr_d}")

day_info = data["days"].get(curr_d, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            cols = st.columns([4, 1])
            cols[0].write(f"**{ex['name'].upper()}**")
            if cols[1].button("❌", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"💪 {s['w']} кг x {s['r']}")
            
            with st.popover("Добавить сет"):
                cw, cr = st.columns(2)
                w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
                r = cr.number_input("Раз", 0, step=1, key=f"r_{i}")
                if st.button("ОК", key=f"s_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
else:
    st.info("Нет записей. Выбери дату ползунком выше.")

with st.popover("🚀 Добавить упражнение", use_container_width=True):
    new_ex = st.text_input("Название")
    if st.button("Внести"):
        if new_ex:
            if curr_d not in data["days"]: data["days"][curr_d] = {"template": None, "exercises": []}
            data["days"][curr_d]["exercises"].append({"name": new_ex.strip(), "sets": []})
            save_data(data); st.rerun()
