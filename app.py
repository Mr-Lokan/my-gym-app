import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Настройка страницы для мобилок
st.set_page_config(page_title="Gym Legend", layout="centered")

# --- УЛЬТРА-СТИЛИ ДЛЯ МОБИЛЬНОГО КАЛЕНДАРЯ ---
st.markdown("""
<style>
    /* Прячем лишние отступы Streamlit */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    
    /* Сетка календаря */
    .cal-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
        margin-top: 10px;
    }
    
    /* Заголовки дней недели */
    .weekday {
        text-align: center;
        font-size: 10px;
        color: #888;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Стиль кнопок-дат */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        padding: 0 !important;
        font-size: 14px !important;
        line-height: 1 !important;
        border-radius: 8px !important;
        background-color: #1e2124 !important;
        border: 1px solid #333 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Цвет точки под кнопкой */
    .dot-container {
        display: flex;
        justify-content: center;
        margin-top: -8px;
        height: 8px;
    }
    .cal-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f)
                if "days" not in d: d["days"] = {}
                if "templates" not in d: d["templates"] = {}
                if "tmpl_colors" not in d: d["tmpl_colors"] = {}
                return d
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- ИНТЕРФЕЙС ---
st.title("🏋️ Gym Legend")

# Месяц и Год в одну строку для экономии места
c1, c2 = st.columns([2, 1])
m_idx = c1.selectbox("Месяц", range(1, 13), index=datetime.now().month-1)
y_val = c2.number_input("Год", value=2026)

# ДНИ НЕДЕЛИ
st.markdown('<div class="cal-container">' + 
    ''.join([f'<div class="weekday">{d}</div>' for d in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]]) + 
    '</div>', unsafe_allow_html=True)

# КАЛЕНДАРЬ
cal = calendar.monthcalendar(y_val, m_idx)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            d_str = f"{y_val}-{m_idx:02d}-{day:02d}"
            
            # Если кнопка нажата
            if cols[i].button(str(day), key=f"d_{d_str}"):
                st.session_state.sel_date = d_str
            
            # Рисуем индикатор тренировки (точку), если есть данные
            if d_str in data["days"]:
                t_name = data["days"][d_str].get("template")
                color = data["tmpl_colors"].get(t_name, "#58A6FF")
                cols[i].markdown(f'<div class="dot-container"><div class="cal-dot" style="background:{color}"></div></div>', unsafe_allow_html=True)

st.divider()

# ВЫБРАННЫЙ ДЕНЬ
sel_d = st.session_state.get("sel_date", datetime.now().strftime("%Y-%m-%d"))
st.subheader(f"📅 {sel_d}")

day_info = data["days"].get(sel_d, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            col_name, col_del = st.columns([4, 1])
            col_name.write(f"**{ex['name'].upper()}**")
            if col_del.button("❌", key=f"del_{i}"):
                ex_list.pop(i)
                save_data(data)
                st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"🔘 {s['w']} кг x {s['r']}")
            
            # Быстрое добавление подхода
            with st.expander("➕ Сет"):
                c_w, c_r = st.columns(2)
                w = c_w.number_input("Кг", min_value=0.0, step=0.5, key=f"w_{i}")
                r = c_r.number_input("Раз", min_value=0, step=1, key=f"r_{i}")
                if st.button("ОК", key=f"ok_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data)
                    st.rerun()
else:
    st.info("Пусто. Выбери дату или добавь упражнение ниже.")

# КНОПКА ДОБАВЛЕНИЯ ВНИЗУ (ФИКСИРОВАННАЯ)
new_ex_name = st.text_input("Новое упражнение...")
if st.button("🚀 Добавить в план"):
    if new_ex_name:
        if sel_d not in data["days"]: data["days"][sel_d] = {"template": None, "exercises": []}
        data["days"][sel_d]["exercises"].append({"name": new_ex_name, "sets": []})
        save_data(data)
        st.rerun()
