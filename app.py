import streamlit as st
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Gym Legend Mobile", layout="centered")

# --- СТИЛИ ДЛЯ МОБИЛЬНОЙ ЛЕНТЫ ---
st.markdown("""
<style>
    .block-container { padding: 1rem !important; }
    
    /* Заставляем 7 кнопок стоять в ряд без переноса */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    
    [data-testid="column"] {
        flex: 1 !important;
        min-width: 0px !important;
    }

    /* Кнопки дней: узкие и высокие */
    div.stButton > button {
        width: 100% !important;
        height: 60px !important;
        padding: 0px !important;
        border-radius: 10px !important;
        background-color: #1e2124 !important;
        border: 1px solid #333 !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Цвет активной кнопки (сегодня/выбранная) */
    div.stButton > button:focus {
        border-color: #58A6FF !important;
        background: #262c36 !important;
    }

    .day-name { font-size: 10px; color: #888; text-transform: uppercase; margin-bottom: 2px; }
    .day-num { font-size: 16px; font-weight: bold; color: white; }
    .dot { width: 4px; height: 4px; border-radius: 50%; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

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

# --- ЛОГИКА ВЫБОРА НЕДЕЛИ ---
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

st.title("🏋️ Gym Legend")

# Переключение недель
c1, c2, c3 = st.columns([1, 3, 1])
if c1.button("◀️"):
    st.session_state.start_date -= timedelta(days=7)
    st.rerun()
c2.markdown(f"<center>{st.session_state.start_date.strftime('%b %Y')}</center>", unsafe_allow_html=True)
if c3.button("▶️"):
    st.session_state.start_date += timedelta(days=7)
    st.rerun()

# --- РЕНДЕР 7 ДНЕЙ (ЛЕНТА) ---
week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
cols = st.columns(7)

for i in range(7):
    current_day = st.session_state.start_date + timedelta(days=i)
    d_str = current_day.strftime("%Y-%m-%d")
    
    # Текст внутри кнопки (Число)
    with cols[i]:
        st.markdown(f"<div class='day-name'>{week_days[i]}</div>", unsafe_allow_html=True)
        if st.button(f"{current_day.day}", key=f"btn_{d_str}"):
            st.session_state.selected_date = current_day
        
        # Точка тренировки
        if d_str in data["days"] and data["days"][d_str].get("exercises"):
            st.markdown("<div style='display:flex; justify-content:center;'><div class='dot' style='background:#58A6FF'></div></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

st.divider()

# --- СПИСОК УПРАЖНЕНИЙ ---
sel_str = st.session_state.selected_date.strftime("%Y-%m-%d")
st.subheader(f"📅 {sel_str}")

day_info = data["days"].get(sel_str, {"exercises": []})
ex_list = day_info.get("exercises", [])

if ex_list:
    for i, ex in enumerate(ex_list):
        with st.container(border=True):
            ct, cd = st.columns([4, 1])
            ct.write(f"**{ex['name'].upper()}**")
            if cd.button("🗑️", key=f"del_{i}"):
                ex_list.pop(i); save_data(data); st.rerun()
            
            # Подходы в ряд
            sets = ex.get("sets", [])
            if sets:
                st.caption(" | ".join([f"{s['w']}кг x {s['r']}" for s in sets]))
            
            with st.expander("Добавить подход"):
                cw, cr, cb = st.columns([2, 2, 1])
                w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
                r = cr.number_input("Р", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
                if cb.button("➕", key=f"ok_{i}"):
                    ex["sets"].append({"w": str(w), "r": str(r)})
                    save_data(data); st.rerun()
else:
    st.info("Нет тренировок. Нажми кнопку ниже.")

with st.popover("🚀 Добавить упражнение", use_container_width=True):
    name = st.text_input("Название (напр. Жим лежа)")
    if st.button("Внести в план"):
        if name:
            if sel_str not in data["days"]: data["days"][sel_str] = {"exercises": []}
            data["days"][sel_str]["exercises"].append({"name": name, "sets": []})
            save_data(data); st.rerun()
