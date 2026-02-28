import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Настройка страницы для фиксации интерфейса
st.set_page_config(page_title="Gym Legend", layout="centered", initial_sidebar_state="collapsed")

# --- СТИЛИ ДЛЯ ИСКЛЮЧЕНИЯ ЛИШНЕГО СКРОЛЛА ---
st.markdown("""
<style>
    /* Убираем верхний отступ Streamlit */
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }
    
    /* Делаем заголовок меньше */
    h1 { font-size: 1.5rem !important; margin-bottom: 0.5rem !important; }

    /* Принудительный ряд для колонок (Flexbox) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    
    [data-testid="column"] {
        width: 14% !important;
        flex: 1 1 0% !important;
        min-width: 0px !important;
    }

    /* Кнопки-микро: уменьшаем высоту, чтобы не листать */
    div.stButton > button {
        width: 100% !important;
        height: 28px !important;
        padding: 0px !important;
        font-size: 10px !important;
        border-radius: 4px !important;
        background-color: #1e2124 !important;
        border: 1px solid #333 !important;
    }

    /* Точка под числом еще ближе */
    .cal-dot {
        width: 3px;
        height: 3px;
        border-radius: 50%;
        margin: -5px auto 2px auto;
        display: block;
    }

    /* Убираем лишние отступы у виджетов */
    .stSelectbox, .stNumberInput { margin-bottom: -10px !important; }
    
    /* Стили для карточек упражнений */
    [data-testid="stExpander"] { border-radius: 8px !important; }
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

# Компактная строка выбора месяца/года
c_m, c_y = st.columns([3, 2])
m_idx = c_m.selectbox("M", range(1, 13), index=datetime.now().month-1, label_visibility="collapsed")
y_val = c_y.number_input("Y", value=2026, label_visibility="collapsed")

# Шапка дней (мини)
h_cols = st.columns(7)
for i, d_n in enumerate(["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]):
    h_cols[i].markdown(f"<p style='text-align:center; font-size:8px; color:#666; margin:0;'>{d_n}</p>", unsafe_allow_html=True)

# Сетка календаря
cal = calendar.monthcalendar(y_val, m_idx)
for week in cal:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            d_str = f"{y_val}-{m_idx:02d}-{day:02d}"
            # Кнопка
            if cols[i].button(str(day), key=f"d_{d_str}"):
                st.session_state.sel_date = d_str
            # Индикатор
            if d_str in data["days"]:
                tmpl = data["days"][d_str].get("template")
                color = data["tmpl_colors"].get(tmpl, "#58A6FF")
                cols[i].markdown(f"<div class='cal-dot' style='background:{color}'></div>", unsafe_allow_html=True)

st.divider()

# СЕКЦИЯ ТРЕНИРОВКИ (ОЧЕНЬ КОМПАКТНО)
curr_d = st.session_state.sel_date
st.markdown(f"**📝 {curr_d}**")

day_info = data["days"].get(curr_d, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.expander(f"🔹 {ex['name'].upper()}", expanded=True):
            # Краткий список сетов в одну строку
            sets_str = " | ".join([f"{s['w']}x{s['r']}" for s in ex.get("sets", [])])
            if sets_str: st.caption(sets_str)
            
            # Ввод нового сета (маленький)
            cw, cr, cb = st.columns([2, 2, 1])
            w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
            r = cr.number_input("Р", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
            if cb.button("➕", key=f"add_{i}"):
                ex["sets"].append({"w": str(w), "r": str(r)})
                save_data(data); st.rerun()
            
            if st.button(f"Удалить упражнение", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
else:
    st.caption("Выбери дату выше")

# Кнопка добавления в самом низу
with st.popover("🚀 Добавить упражнение", use_container_width=True):
    n_ex = st.text_input("Название")
    if st.button("OK"):
        if n_ex:
            if curr_d not in data["days"]: data["days"][curr_d] = {"template": None, "exercises": []}
            data["days"][curr_d]["exercises"].append({"name": n_ex.strip(), "sets": []})
            save_data(data); st.rerun()
