import streamlit as st
import json
import os
import calendar
from datetime import datetime

st.set_page_config(page_title="Gym Legend", layout="centered")

# --- СТИЛИ (ФИНАЛЬНАЯ ВЕРСИЯ) ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #0d1117; }
    .block-container { padding: 1rem !important; max-width: 400px !important; }
    
    /* Сетка календаря */
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 3px; table-layout: fixed; }
    .cal-table th { color: #8b949e; font-size: 10px; text-align: center; padding-bottom: 5px; }
    
    .cal-day {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        height: 40px;
        text-align: center;
        color: #f0f6fc;
        font-size: 13px;
        position: relative;
    }
    .cal-day.today { border: 1px solid #58a6ff; background: #1c2128; }
    .cal-day.empty { background: transparent; border: none; }
    
    /* Точка тренировки */
    .dot {
        position: absolute;
        bottom: 3px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        background-color: #58a6ff;
        border-radius: 50%;
    }
    
    /* Упражнения */
    .ex-card {
        background: #161b22;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ДАННЫХ ---
def load_data():
    if os.path.exists("gym_data.json"):
        try:
            with open("gym_data.json", "r", encoding="utf-8") as f:
                d = json.load(f)
                if "days" not in d: d = {"days": {}}
                return d
        except: return {"days": {}}
    return {"days": {}}

def save_data(data):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# Управление просмотром
if 'view_month' not in st.session_state: st.session_state.view_month = datetime.now().month
if 'view_year' not in st.session_state: st.session_state.view_year = datetime.now().year

# --- КАЛЕНДАРЬ (ВИЗУАЛ) ---
st.write(f"### 🗓️ {calendar.month_name[st.session_state.view_month]} {st.session_state.view_year}")

# Навигация по месяцам
c_n1, c_n2, c_n3 = st.columns([1,2,1])
if c_n1.button("←", key="prev"):
    st.session_state.view_month -= 1
    if st.session_state.view_month == 0: st.session_state.view_month = 12; st.session_state.view_year -= 1
    st.rerun()
if c_n3.button("→", key="next"):
    st.session_state.view_month += 1
    if st.session_state.view_month == 13: st.session_state.view_month = 1; st.session_state.view_year += 1
    st.rerun()

# Отрисовка сетки
cal = calendar.monthcalendar(st.session_state.view_year, st.session_state.view_month)
html_grid = '<table class="cal-table"><tr><th>ПН</th><th>ВТ</th><th>СР</th><th>ЧТ</th><th>ПТ</th><th>СБ</th><th>ВС</th></tr>'

for week in cal:
    html_grid += '<tr>'
    for day in week:
        if day == 0:
            html_grid += '<td class="cal-day empty"></td>'
        else:
            d_key = f"{st.session_state.view_year}-{st.session_state.view_month:02d}-{day:02d}"
            has_data = d_key in st.session_state.db["days"] and st.session_state.db["days"][d_key]
            dot = '<div class="dot"></div>' if has_data else ""
            is_today = "today" if d_key == datetime.now().strftime("%Y-%m-%d") else ""
            html_grid += f'<td class="cal-day {is_today}">{day}{dot}</td>'
    html_grid += '</tr>'
html_grid += '</table>'

st.markdown(html_grid, unsafe_allow_html=True)

# ВЫБОР ДАТЫ (Надежный метод)
days_in_month = calendar.monthrange(st.session_state.view_year, st.session_state.view_month)[1]
selected_day = st.selectbox("Открыть день:", range(1, days_in_month + 1), index=datetime.now().day-1 if st.session_state.view_month == datetime.now().month else 0)
target_date = f"{st.session_state.view_year}-{st.session_state.view_month:02d}-{selected_day:02d}"

st.divider()

# --- ТРЕНИРОВКИ ---
st.write(f"#### 📋 План на {target_date}")

# Добавление
if st.button("➕ ДОБАВИТЬ УПРАЖНЕНИЕ", use_container_width=True):
    st.session_state.add_mode = True

if st.session_state.get("add_mode"):
    with st.form("new_ex"):
        ex_name = st.text_input("Название")
        if st.form_submit_button("Сохранить"):
            if target_date not in st.session_state.db["days"]: st.session_state.db["days"][target_date] = []
            st.session_state.db["days"][target_date].append({"name": ex_name, "sets": []})
            save_data(st.session_state.db)
            st.session_state.add_mode = False
            st.rerun()

# Список упражнений
day_data = st.session_state.db["days"].get(target_date, [])
if not day_data:
    st.info("Пусто")
else:
    for i, ex in enumerate(day_data):
        with st.container(border=True):
            st.write(f"**{ex['name'].upper()}**")
            
            # Показ сетов
            if ex.get('sets'):
                st.caption(" | ".join([f"{s['w']}×{s['r']}" for s in ex['sets']]))
            
            col_add, col_del = st.columns([4, 1])
            with col_add.expander("Добавить сет"):
                cw, cr, cb = st.columns([2, 2, 1])
                w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{target_date}_{i}")
                r = cr.number_input("Р", 0, step=1, key=f"r_{target_date}_{i}")
                if cb.button("➕", key=f"ok_{target_date}_{i}"):
                    ex['sets'].append({"w": str(w), "r": str(r)})
                    save_data(st.session_state.db)
                    st.rerun()
            
            if col_del.button("🗑️", key=f"del_{target_date}_{i}"):
                day_data.pop(i)
                save_data(st.session_state.db)
                st.rerun()
