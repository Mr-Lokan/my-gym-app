import streamlit as st
import json
import os
from datetime import datetime, timedelta
import streamlit.components.v1 as components

st.set_page_config(page_title="Gym Legend", layout="centered")

# --- ЗАГРУЗКА ДАННЫХ ---
def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                d = json.load(f); d.setdefault("days", {}); return d
        except: pass
    return {"days": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- ЛОГИКА ВЫБОРА ДАТЫ ---
if 'sel_date' not in st.session_state:
    st.session_state.sel_date = datetime.now().strftime("%Y-%m-%d")

# --- HTML/JS КОМПОНЕНТ КАЛЕНДАРЯ ---
def scroll_calendar():
    # Генерируем дни на 2 недели вперед и назад
    start = datetime.now() - timedelta(days=14)
    days_html = ""
    for i in range(30):
        d = start + timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")
        is_today = "today" if d.date() == datetime.now().date() else ""
        is_sel = "selected" if d_str == st.session_state.sel_date else ""
        has_work = "dot" if d_str in data["days"] and data["days"][d_str].get("exercises") else ""
        
        days_html += f"""
        <div class="day-card {is_sel} {is_today}" onclick="selectDate('{d_str}')">
            <span class="wd">{d.strftime('%a')}</span>
            <span class="num">{d.day}</span>
            <div class="{has_work}"></div>
        </div>
        """

    html_content = f"""
    <style>
        .scroll-wrapper {{
            display: flex;
            overflow-x: auto;
            padding: 10px 5px;
            gap: 10px;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }}
        .scroll-wrapper::-webkit-scrollbar {{ display: none; }}
        .day-card {{
            flex: 0 0 50px;
            height: 70px;
            background: #1e2124;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            border: 1px solid #333;
            color: #888;
            cursor: pointer;
        }}
        .day-card.selected {{ border: 2px solid #58A6FF; color: white; background: #262c36; }}
        .day-card.today {{ color: #58A6FF; border-bottom: 2px solid #58A6FF; }}
        .wd {{ font-size: 10px; text-transform: uppercase; }}
        .num {{ font-size: 18px; font-weight: bold; }}
        .dot {{ width: 5px; height: 5px; background: #58A6FF; border-radius: 50%; margin-top: 4px; }}
    </style>
    
    <div class="scroll-wrapper">
        {days_html}
    </div>

    <script>
        function selectDate(date) {{
            window.parent.postMessage({{type: 'streamlit:setComponentValue', value: date}}, '*');
        }}
    </script>
    """
    return components.html(html_content, height=100)

# --- ИНТЕРФЕЙС ---
st.write("### 🏋️ Gym Legend")

# Вызов календаря и получение выбранной даты
res = scroll_calendar()
if res:
    st.session_state.sel_date = res
    st.rerun()

curr_date = st.session_state.sel_date
st.markdown(f"#### 📅 {curr_date}")

# --- СПИСОК УПРАЖНЕНИЙ ---
day_info = data["days"].get(curr_date, {"exercises": []})

with st.popover("🚀 Добавить упражнение", use_container_width=True):
    name = st.text_input("Название")
    if st.button("Добавить"):
        if name:
            if curr_date not in data["days"]: data["days"][curr_date] = {"exercises": []}
            data["days"][curr_date]["exercises"].append({"name": name, "sets": []})
            save_data(data); st.rerun()

if not day_info["exercises"]:
    st.info("Нет записей")
else:
    for i, ex in enumerate(day_info["exercises"]):
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.write(f"**{ex['name'].upper()}**")
            if c2.button("🗑️", key=f"del_{i}"):
                day_info["exercises"].pop(i); save_data(data); st.rerun()
            
            # Компактный вывод подходов
            if ex.get("sets"):
                st.caption(" | ".join([f"{s['w']}×{s['r']}" for s in ex['sets']]))
            
            with st.expander("Добавить сет"):
                col_w, col_r, col_b = st.columns([2, 2, 1])
                w = col_w.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
                r = col_r.number_input("П", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
                if col_b.button("➕", key=f"ok_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
