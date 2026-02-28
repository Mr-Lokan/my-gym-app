import streamlit as st
import json
import os
import calendar
from datetime import datetime

st.set_page_config(page_title="Gym Legend", layout="centered")

# --- УЛЬТРА-КОМПАКТНЫЙ СТИЛЬ (ДЛЯ ТЕЛЕГРАМА) ---
st.markdown("""
<style>
    .block-container { padding: 0.5rem !important; }
    h1 { font-size: 1.2rem !important; margin: 0 !important; padding: 0 !important; }
    
    /* СТИЛЬ ТАБЛИЦЫ КАЛЕНДАРЯ */
    .cal-table {
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        margin-top: 10px;
    }
    .cal-table th {
        font-size: 10px;
        color: #888;
        padding: 2px;
        text-align: center;
    }
    .cal-table td {
        border: 1px solid #333;
        height: 40px;
        text-align: center;
        vertical-align: middle;
        position: relative;
        background: #1e2124;
        border-radius: 4px;
        font-size: 12px;
        color: #ddd;
    }
    .has-workout::after {
        content: '';
        position: absolute;
        bottom: 4px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background-color: #58A6FF; /* Цвет точки */
    }
    .selected-day { border: 2px solid #ff4b4b !important; background: #262c36 !important; }

    /* Прячем стандартные элементы для экономии места */
    [data-testid="stHeader"] {display: none;}
    .stSelectbox label, .stNumberInput label {display: none;}
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

# Текущая дата
if 'active_date' not in st.session_state:
    st.session_state.active_date = datetime.now().date()

st.title("🏋️ Gym Legend")

# Выбор месяца (в одну строку)
col1, col2 = st.columns([3, 2])
with col1:
    m = st.selectbox("M", range(1, 13), index=st.session_state.active_date.month-1)
with col2:
    y = st.number_input("Y", value=2026)

# --- ОТРИСОВКА HTML КАЛЕНДАРЯ ---
cal = calendar.monthcalendar(y, m)
html_code = '<table class="cal-table"><tr><th>Пн</th><th>Вт</th><th>Ср</th><th>Чт</th><th>Пт</th><th>Сб</th><th>Вс</th></tr>'

for week in cal:
    html_code += '<tr>'
    for day in week:
        if day == 0:
            html_code += '<td></td>'
        else:
            d_str = f"{y}-{m:02d}-{day:02d}"
            classes = []
            if d_str in data["days"]: classes.append("has-workout")
            if d_str == str(st.session_state.active_date): classes.append("selected-day")
            
            class_str = " ".join(classes)
            html_code += f'<td class="{class_str}">{day}</td>'
    html_code += '</tr>'
html_code += '</table>'

st.markdown(html_code, unsafe_allow_html=True)

# Слайдер для выбора дня (самый стабильный метод ввода)
days_in_m = calendar.monthrange(y, m)[1]
day_sel = st.select_slider(
    "Выбери день месяца:", 
    options=range(1, days_in_m + 1), 
    value=st.session_state.active_date.day
)
st.session_state.active_date = datetime(y, m, day_sel).date()

st.divider()

# --- СПИСОК УПРАЖНЕНИЙ ---
target_d = str(st.session_state.active_date)
st.markdown(f"**📅 {target_d}**")

day_info = data["days"].get(target_d, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            cols = st.columns([4, 1])
            cols[0].write(f"**{ex['name'].upper()}**")
            if cols[1].button("🗑️", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
            
            sets_info = " | ".join([f"{s['w']}x{s['r']}" for s in ex.get("sets", [])])
            if sets_info: st.caption(sets_info)
            
            with st.expander("Добавить подход"):
                c_w, c_r, c_b = st.columns([2, 2, 1])
                w = c_w.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
                r = c_r.number_input("Р", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
                if c_b.button("➕", key=f"add_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
else:
    st.info("Пусто")

with st.popover("🚀 Новое упражнение", use_container_width=True):
    new_ex = st.text_input("Название")
    if st.button("Добавить"):
        if new_ex:
            if target_d not in data["days"]: data["days"][target_d] = {"exercises": []}
            data["days"][target_d]["exercises"].append({"name": new_ex, "sets": []})
            save_data(data); st.rerun()
