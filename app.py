import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Compact", layout="centered")

# --- СТИЛИ ДЛЯ МИКРО-КНОПОК ---
st.markdown("""
<style>
    /* Убираем отступы контейнера */
    .block-container { padding-top: 1rem !important; }
    
    /* Делаем колонки узкими и в один ряд */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
        padding: 0 2px !important;
    }

    /* МИКРО-КНОПКИ */
    div.stButton > button {
        width: 100% !important;
        height: 35px !important; /* Жесткая высота */
        padding: 0px !important;
        font-size: 13px !important;
        border-radius: 6px !important;
        background-color: #1e2124 !important;
        border: 1px solid #333 !important;
        color: white !important;
    }

    /* Точка под числом */
    .cal-dot {
        width: 4px;
        height: 4px;
        border-radius: 50%;
        margin: -8px auto 4px auto;
        display: block;
    }
    
    .day-name {
        text-align: center;
        font-size: 10px;
        color: #888;
        margin-bottom: 2px;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f); d.setdefault("days", {}); d.setdefault("templates", {}); d.setdefault("tmpl_colors", {})
                return d
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

if 'sel_date' not in st.session_state:
    st.session_state.sel_date = datetime.now().strftime("%Y-%m-%d")

st.title("🏋️ Gym Legend")

# Компактный выбор месяца
c1, c2 = st.columns([2, 1])
m_idx = c1.selectbox("Месяц", range(1, 13), index=datetime.now().month-1, label_visibility="collapsed")
y_val = c2.number_input("Год", value=2026, label_visibility="collapsed")

# Шапка дней недели
h_cols = st.columns(7)
for i, d_n in enumerate(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]):
    h_cols[i].markdown(f"<div class='day-name'>{d_n}</div>", unsafe_allow_html=True)

# Сетка календаря
cal = calendar.monthcalendar(y_val, m_idx)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            d_str = f"{y_val}-{m_idx:02d}-{day:02d}"
            
            # Кнопка дня
            if cols[i].button(str(day), key=f"d_{d_str}"):
                st.session_state.sel_date = d_str
            
            # Точка индикатор
            if d_str in data["days"]:
                tmpl = data["days"][d_str].get("template")
                color = data["tmpl_colors"].get(tmpl, "#58A6FF")
                cols[i].markdown(f"<div class='cal-dot' style='background:{color}'></div>", unsafe_allow_html=True)

st.divider()

# РАБОТА С ЗАПИСЯМИ
curr_d = st.session_state.sel_date
st.markdown(f"### 📅 {curr_d}")

day_info = data["days"].get(curr_d, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            cols = st.columns([5, 1])
            cols[0].write(f"**{ex['name'].upper()}**")
            if cols[1].button("❌", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"🔹 {s['w']} кг x {s['r']}")
            
            with st.expander("Добавить подход"):
                cw, cr = st.columns(2)
                w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
                r = cr.number_input("Раз", 0, step=1, key=f"r_{i}")
                if st.button("Записать", key=f"s_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
else:
    st.info("Выбери дату выше")

with st.popover("🚀 Добавить упражнение", use_container_width=True):
    n_ex = st.text_input("Название")
    if st.button("Внести"):
        if n_ex:
            if curr_d not in data["days"]: data["days"][curr_d] = {"template": None, "exercises": []}
            data["days"][curr_d]["exercises"].append({"name": n_ex.strip(), "sets": []})
            save_data(data); st.rerun()
