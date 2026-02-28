import streamlit as st
import json
import os
import calendar
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="Gym Legend", layout="centered")

# --- СТИЛИ И СКРИПТ ДЛЯ КЛИКАБЕЛЬНОСТИ ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #0d1117; }
    .block-container { padding-top: 1rem !important; max-width: 400px !important; }
    
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 4px; table-layout: fixed; }
    .cal-table th { color: #8b949e; font-size: 11px; text-align: center; font-weight: 400; padding-bottom: 8px; }
    
    .cal-day {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        height: 45px;
        text-align: center;
        color: #f0f6fc;
        font-size: 14px;
        cursor: pointer;
        position: relative;
        transition: 0.2s;
    }
    .cal-day:hover { border-color: #58a6ff; }
    .cal-day.selected { border: 2px solid #58a6ff; background: #1c2128; box-shadow: 0 0 10px rgba(88,166,255,0.2); }
    .cal-day.empty { background: transparent; border: none; cursor: default; }
    
    .dot {
        position: absolute;
        bottom: 4px;
        left: 50%;
        transform: translateX(-50%);
        width: 4px;
        height: 4px;
        background-color: #58a6ff;
        border-radius: 50%;
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

# Инициализация состояния
if 'view_month' not in st.session_state: st.session_state.view_month = datetime.now().month
if 'view_year' not in st.session_state: st.session_state.view_year = datetime.now().year
if 'sel_date_str' not in st.session_state: st.session_state.sel_date_str = datetime.now().strftime("%Y-%m-%d")

# --- КОМПОНЕНТ КАЛЕНДАРЯ ---
def draw_calendar():
    curr_month = st.session_state.view_month
    curr_year = st.session_state.view_year
    cal = calendar.monthcalendar(curr_year, curr_month)
    month_name = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"][curr_month-1]
    
    rows_html = ""
    for week in cal:
        rows_html += "<tr>"
        for day in week:
            if day == 0:
                rows_html += '<td class="cal-day empty"></td>'
            else:
                d_str = f"{curr_year}-{curr_month:02d}-{day:02d}"
                is_sel = "selected" if d_str == st.session_state.sel_date_str else ""
                has_work = '<div class="dot"></div>' if d_str in st.session_state.db["days"] and st.session_state.db["days"][d_str] else ""
                rows_html += f'<td class="cal-day {is_sel}" onclick="selectDate(\'{d_str}\')">{day}{has_work}</td>'
        rows_html += "</tr>"

    html_code = f"""
    <div style="color:white; text-align:center; font-family:sans-serif; margin-bottom:10px;">
        <b style="font-size:18px;">{month_name} {curr_year}</b>
    </div>
    <table class="cal-table">
        <tr><th>ПН</th><th>ВТ</th><th>СР</th><th>ЧТ</th><th>ПТ</th><th>СБ</th><th>ВС</th></tr>
        {rows_html}
    </table>
    <script>
        function selectDate(date) {{
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: date}}, '*');
        }}
    </script>
    """
    # Компонент возвращает выбранную дату при клике
    return components.html(html_code, height=310)

# Отрисовка
col_nav1, col_nav2, col_nav3 = st.columns([1,2,1])
if col_nav1.button("←"):
    st.session_state.view_month -= 1
    if st.session_state.view_month == 0: st.session_state.view_month = 12; st.session_state.view_year -= 1
    st.rerun()
if col_nav3.button("→"):
    st.session_state.view_month += 1
    if st.session_state.view_month == 13: st.session_state.view_month = 1; st.session_state.view_year += 1
    st.rerun()

new_date = draw_calendar()
if new_date and new_date != st.session_state.sel_date_str:
    st.session_state.sel_date_str = new_date
    st.rerun()

# --- СПИСОК УПРАЖНЕНИЙ ---
st.markdown(f"### 📋 План: {st.session_state.sel_date_str}")

if st.button("➕ ДОБАВИТЬ УПРАЖНЕНИЕ", use_container_width=True):
    st.session_state.add_mode = True

if st.session_state.get("add_mode"):
    with st.form("add_ex"):
        name = st.text_input("Название")
        if st.form_submit_button("OK"):
            d_key = st.session_state.sel_date_str
            if d_key not in st.session_state.db["days"]: st.session_state.db["days"][d_key] = []
            st.session_state.db["days"][d_key].append({"name": name, "sets": []})
            save_data(st.session_state.db)
            st.session_state.add_mode = False
            st.rerun()

day_data = st.session_state.db["days"].get(st.session_state.sel_date_str, [])
if not day_data:
    st.caption("На этот день ничего нет")
else:
    for i, ex in enumerate(day_data):
        with st.container(border=True):
            st.write(f"**{ex['name'].upper()}**")
            # Сеты
            if ex.get('sets'):
                st.write(" | ".join([f"{s['w']}×{s['r']}" for s in ex['sets']]))
            
            c1, c2 = st.columns([4, 1])
            with c1.expander("Добавить подход"):
                cw, cr, cb = st.columns([2, 2, 1])
                w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
                r = cr.number_input("Р", 0, step=1, key=f"r_{i}")
                if cb.button("✅", key=f"ok_{i}"):
                    ex['sets'].append({"w": str(w), "r": str(r)})
                    save_data(st.session_state.db)
                    st.rerun()
            if c2.button("🗑️", key=f"del_{i}"):
                day_data.pop(i)
                save_data(st.session_state.db)
                st.rerun()
