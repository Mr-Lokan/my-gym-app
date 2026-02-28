import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Настройка страницы
st.set_page_config(page_title="Gym Legend Elite", layout="centered")

# --- СТИЛИЗАЦИЯ (CSS) ---
st.markdown("""
<style>
    /* Плитка календаря */
    .cal-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        text-align: center;
        margin-bottom: 20px;
    }
    .cal-day-header {
        font-weight: bold;
        color: #888;
        font-size: 0.8rem;
        padding-bottom: 5px;
    }
    .cal-day {
        background: #1e2124;
        border-radius: 8px;
        padding: 10px 0;
        min-height: 45px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border: 1px solid #333;
    }
    .cal-day.active {
        border: 2px solid #58A6FF;
        background: #232a35;
    }
    .dot {
        height: 6px;
        width: 6px;
        border-radius: 50%;
        display: inline-block;
        margin-top: 4px;
    }
    /* Кнопки как в приложении */
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- ФУНКЦИИ ДАННЫХ ---
def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "days" not in data: data["days"] = {}
                if "templates" not in data: data["templates"] = {}
                if "tmpl_colors" not in data: data["tmpl_colors"] = {}
                return data
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(data):
    to_del = [d for d, v in data["days"].items() if not v.get("exercises")]
    for d in to_del: del data["days"][d]
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
st.title("🏋️ GYM LEGEND")

# Инициализация даты
if 'sel_date' not in st.session_state:
    st.session_state.sel_date = datetime.now().strftime("%Y-%m-%d")

# ВЫБОР МЕСЯЦА
col_m, col_y = st.columns([2, 1])
now = datetime.now()
month = col_m.selectbox("Месяц", range(1, 13), index=now.month-1, format_func=lambda x: calendar.month_name[x])
year = col_y.number_input("Год", value=now.year)

# РЕНДЕР КАЛЕНДАРЯ
st.markdown('<div class="cal-grid">', unsafe_allow_html=True)
for day_name in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
    st.markdown(f'<div class="cal-day-header">{day_name}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

cal = calendar.monthcalendar(year, month)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            d_str = f"{year}-{month:02d}-{day:02d}"
            is_active = d_str == st.session_state.sel_date
            
            # Логика цвета
            dot_html = ""
            if d_str in data["days"]:
                tmpl = data["days"][d_str].get("template")
                c = data["tmpl_colors"].get(tmpl, "#58A6FF")
                dot_html = f'<span class="dot" style="background-color: {c}; shadow: 0 0 5px {c};"></span>'
            
            # Кнопка дня
            btn_label = f"{day}"
            if cols[i].button(btn_label, key=f"d_{d_str}", use_container_width=True):
                st.session_state.sel_date = d_str
                st.rerun()
            
            # Точка под кнопкой
            if dot_html:
                cols[i].markdown(f'<div style="text-align:center; margin-top:-15px;">{dot_html}</div>', unsafe_allow_html=True)

st.divider()

# --- СПИСОК УПРАЖНЕНИЙ ---
date_str = st.session_state.sel_date
st.subheader(f"📅 План: {date_str}")

day_info = data["days"].get(date_str, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            col_t, col_btn = st.columns([4, 1])
            col_t.markdown(f"**{ex['name'].upper()}**")
            if col_btn.button("🗑️", key=f"del_{i}"):
                ex_list.pop(i)
                save_data(data)
                st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"✅ {s['w']} кг x {s['r']}")
            
            # Форма сета
            with st.expander("Добавить подход"):
                c1, c2 = st.columns(2)
                w = c1.number_input("Кг", min_value=0.0, step=0.5, key=f"w_{i}")
                r = c2.number_input("Раз", min_value=0, step=1, key=f"r_{i}")
                if st.button("Сохранить сет", key=f"save_s_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data)
                    st.rerun()
else:
    st.info("На этот день нет записей. Выберите дату в календаре выше или добавьте упражнение.")

# Кнопка добавления внизу
if st.button("➕ Добавить новое упражнение"):
    st.session_state.adding = True

if st.session_state.get("adding"):
    with st.form("new_ex"):
        name = st.text_input("Название упражнения")
        if st.form_submit_button("Добавить"):
            if date_str not in data["days"]: data["days"][date_str] = {"template": None, "exercises": []}
            data["days"][date_str]["exercises"].append({"name": name, "sets": []})
            save_data(data)
            st.session_state.adding = False
            st.rerun()
