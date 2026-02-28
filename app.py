import streamlit as st
import json
import os
import calendar
from datetime import datetime

# Настройка
st.set_page_config(page_title="Gym Legend", layout="centered")

# --- СТИЛИ ДЛЯ ЖЕСТКОЙ СЕТКИ КАЛЕНДАРЯ ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #0d1117; }
    .block-container { padding-top: 1rem !important; max-width: 400px !important; }
    
    /* Таблица календаря */
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .cal-table th { color: #8b949e; font-size: 11px; text-align: center; font-weight: 400; padding-bottom: 8px; }
    
    .cal-day {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        height: 45px;
        text-align: center;
        vertical-align: middle;
        cursor: pointer;
        position: relative;
        color: #f0f6fc;
        font-size: 14px;
        transition: 0.2s;
    }
    .cal-day:active { background: #1f6feb; }
    .cal-day.selected { border: 2px solid #58a6ff; background: #1c2128; }
    .cal-day.empty { background: transparent; border: none; }
    
    /* Точка тренировки */
    .dot {
        position: absolute;
        bottom: 5px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        background-color: #58a6ff;
        border-radius: 50%;
        box-shadow: 0 0 5px #58a6ff;
    }

    /* Заголовок месяца */
    .month-header {
        text-align: center;
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ДАННЫХ ---
def load_data():
    if os.path.exists("gym_data.json"):
        try:
            with open("gym_data.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"days": {}}
    return {"days": {}}

def save_data(data):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# Инициализация выбранной даты
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()
if 'view_month' not in st.session_state:
    st.session_state.view_month = datetime.now().month
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year

# --- ОТРИСОВКА КАЛЕНДАРЯ ---
st.markdown(f"<div class='month-header'><span>{calendar.month_name[st.session_state.view_month]} {st.session_state.view_year}</span></div>", unsafe_allow_html=True)

# Кнопки переключения месяца (в ряд)
col_m1, col_m2, col_m3 = st.columns([1,2,1])
if col_m1.button("←", key="prev"):
    st.session_state.view_month -= 1
    if st.session_state.view_month == 0:
        st.session_state.view_month = 12
        st.session_state.view_year -= 1
    st.rerun()
if col_m3.button("→", key="next"):
    st.session_state.view_month += 1
    if st.session_state.view_month == 13:
        st.session_state.view_month = 1
        st.session_state.view_year += 1
    st.rerun()

# Генерируем HTML таблицу
cal = calendar.monthcalendar(st.session_state.view_year, st.session_state.view_month)
html_cal = '<table class="cal-table"><tr><th>ПН</th><th>ВТ</th><th>СР</th><th>ЧТ</th><th>ПТ</th><th>СБ</th><th>ВС</th></tr>'

for week in cal:
    html_cal += '<tr>'
    for day in week:
        if day == 0:
            html_cal += '<td class="cal-day empty"></td>'
        else:
            d_str = f"{st.session_state.view_year}-{st.session_state.view_month:02d}-{day:02d}"
            
            # Проверяем наличие тренировки
            has_workout = d_str in st.session_state.db["days"] and len(st.session_state.db["days"][d_str]) > 0
            dot_html = '<div class="dot"></div>' if has_workout else ''
            
            # Проверяем, выбран ли этот день
            is_selected = "selected" if d_str == st.session_state.selected_date.strftime("%Y-%m-%d") else ""
            
            # Мы используем st.button внутри ячейки для кликабельности, но это сложно. 
            # Проще оставить выбор через слайдер или числовой ввод под календарем для стабильности.
            html_cal += f'<td class="cal-day {is_selected}">{day}{dot_html}</td>'
    html_cal += '</tr>'
html_cal += '</table>'

st.markdown(html_cal, unsafe_allow_html=True)

# Выбор дня (чтобы календарь «ожил»)
day_to_select = st.number_input("Выбери число для записи:", 1, 31, value=st.session_state.selected_date.day)
st.session_state.selected_date = datetime(st.session_state.view_year, st.session_state.view_month, day_to_select).date()

st.divider()

# --- СПИСОК УПРАЖНЕНИЙ ---
target_str = st.session_state.selected_date.strftime("%Y-%m-%d")
st.subheader(f"📅 {target_str}")

if st.button("➕ ДОБАВИТЬ УПРАЖНЕНИЕ", use_container_width=True):
    st.session_state.show_add = True

if st.session_state.get("show_add"):
    with st.form("new_ex"):
        name = st.text_input("Название")
        if st.form_submit_button("OK"):
            if target_str not in st.session_state.db["days"]: st.session_state.db["days"][target_str] = []
            st.session_state.db["days"][target_str].append({"name": name, "sets": []})
            save_data(st.session_state.db)
            st.session_state.show_add = False
            st.rerun()

day_data = st.session_state.db["days"].get(target_str, [])
for i, ex in enumerate(day_data):
    with st.container(border=True):
        st.write(f"**{ex['name'].upper()}**")
        sets_preview = " | ".join([f"{s['w']}x{s['r']}" for s in ex.get('sets', [])])
        st.caption(sets_preview if sets_preview else "Нет подходов")
        
        c1, c2 = st.columns([4, 1])
        with c1.expander("Добавить сет"):
            cw, cr, cb = st.columns([2, 2, 1])
            w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
            r = cr.number_input("Р", 0, step=1, key=f"r_{i}")
            if cb.button("➕", key=f"btn_{i}"):
                ex['sets'].append({"w": str(w), "r": str(r)})
                save_data(st.session_state.db)
                st.rerun()
        if c2.button("🗑️", key=f"del_{i}"):
            day_data.pop(i)
            save_data(st.session_state.db)
            st.rerun()
