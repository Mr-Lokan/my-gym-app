import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Compact", layout="centered")

# --- КОМПАКТНЫЙ МОБИЛЬНЫЙ СТИЛЬ ---
st.markdown("""
<style>
    /* Контейнер для кнопок календаря */
    [data-testid="column"] {
        width: calc(14.28% - 4px) !important;
        flex: 1 1 calc(14.28% - 4px) !important;
        min-width: calc(14.28% - 4px) !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    
    /* Сами кнопки: делаем их маленькими квадратами */
    div.stButton > button {
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        padding: 0px !important;
        font-size: 12px !important;
        border-radius: 6px !important;
        background-color: #1e2124 !important;
        border: 1px solid #333 !important;
        line-height: 1 !important;
        display: block !important;
    }

    /* Подсветка выбранного дня */
    div.stButton > button:focus, div.stButton > button:active {
        border: 1px solid #58A6FF !important;
        background-color: #262c36 !important;
    }

    /* Точка под числом прямо в кнопке */
    .indicator {
        font-size: 18px;
        line-height: 0;
        display: block;
        margin-top: -10px;
        text-align: center;
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

# Инициализация даты
if 'active_date' not in st.session_state:
    st.session_state.active_date = datetime.now().strftime("%Y-%m-%d")

st.title("🏋️ GYM LEGEND")

# Выбор месяца (очень компактно)
c1, c2 = st.columns([3, 2])
m_idx = c1.selectbox("Месяц", range(1, 13), index=datetime.now().month-1, label_visibility="collapsed")
y_val = c2.number_input("Год", value=2026, label_visibility="collapsed")

# РЕНДЕР КАЛЕНДАРЯ
days_abbr = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
cols_h = st.columns(7)
for i, d_n in enumerate(days_abbr):
    cols_h[i].markdown(f"<p style='text-align:center; font-size:10px; color:#888; margin:0;'>{d_n}</p>", unsafe_allow_html=True)

cal = calendar.monthcalendar(y_val, m_idx)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            d_str = f"{y_val}-{m_idx:02d}-{day:02d}"
            
            # Определяем маркер тренировки
            marker = ""
            if d_str in data["days"]:
                tmpl = data["days"][d_str].get("template")
                color = data["tmpl_colors"].get(tmpl, "#58A6FF")
                # Используем спецсимвол точки с нужным цветом
                marker = f"\n\n<span class='indicator' style='color:{color};'>.</span>"
            
            # Кнопка. Название содержит число и (если есть) точку через HTML
            if cols[i].button(f"{day}", key=f"btn_{d_str}"):
                st.session_state.active_date = d_str
            
            if marker:
                cols[i].markdown(marker, unsafe_allow_html=True)

st.divider()

# РАБОТА С ВЫБРАННЫМ ДНЕМ
sel_d = st.session_state.active_date
st.subheader(f"📅 {sel_d}")

day_info = data["days"].get(sel_d, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            col_t, col_d = st.columns([5, 1])
            col_t.write(f"**{ex['name'].upper()}**")
            if col_d.button("🗑️", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
            
            for s in ex.get("sets", []):
                st.caption(f"🔹 {s['w']} кг x {s['r']}")
            
            with st.expander("Добавить подход"):
                cw, cr = st.columns(2)
                w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
                r = cr.number_input("Раз", 0, step=1, key=f"r_{i}")
                if st.button("ОК", key=f"ok_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
else:
    st.info("Нет записей.")

with st.popover("🚀 Добавить упражнение", use_container_width=True):
    n_ex = st.text_input("Название")
    if st.button("Внести"):
        if n_ex:
            if sel_d not in data["days"]: data["days"][sel_d] = {"template": None, "exercises": []}
            data["days"][sel_d]["exercises"].append({"name": n_ex.strip(), "sets": []})
            save_data(data); st.rerun()
