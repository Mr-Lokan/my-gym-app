import streamlit as st
import json
import os
from datetime import datetime, timedelta

# Конфигурация для мобилок
st.set_page_config(page_title="Gym", layout="centered")

# --- CSS ДЛЯ ТОТАЛЬНОГО СЖАТИЯ ---
st.markdown("""
<style>
    /* Убираем все внешние отступы Streamlit */
    .block-container { padding: 0.5rem !important; max-width: 100% !important; }
    [data-testid="stHeader"] {display: none;}
    
    /* Схлопываем вертикальные расстояния */
    div[data-testid="stVerticalBlock"] > div { margin-top: -10px !important; }
    
    /* Флекс-ряд для 7 кнопок (жестко) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
    }
    [data-testid="column"] { flex: 1 !important; min-width: 0px !important; }

    /* КНОПКИ ДАТ (миниатюрные) */
    div.stButton > button {
        width: 100% !important;
        height: 45px !important;
        padding: 0px !important;
        font-size: 11px !important;
        border-radius: 6px !important;
        background-color: #1e2124 !important;
        line-height: 1.2 !important;
    }
    
    /* Упражнения: делаем компактнее */
    .stExpander { border: 1px solid #333 !important; margin-bottom: 5px !important; }
    .stMarkdown p { font-size: 14px !important; margin-bottom: 2px !important; }
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

# Инициализация дат
if 'start_date' not in st.session_state:
    st.session_state.start_date = datetime.now().date() - timedelta(days=datetime.now().weekday())
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()

# ВЕРХНЯЯ ПАНЕЛЬ (без Title)
st.write("### 🏋️ Gym Legend")
c1, c2, c3 = st.columns([1, 4, 1])
if c1.button("‹"): st.session_state.start_date -= timedelta(days=7); st.rerun()
c2.markdown(f"<center><b>{st.session_state.start_date.strftime('%B')}</b></center>", unsafe_allow_html=True)
if c3.button("›"): st.session_state.start_date += timedelta(days=7); st.rerun()

# ЛЕНТА 7 ДНЕЙ
week_days = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
cols = st.columns(7)
for i in range(7):
    day = st.session_state.start_date + timedelta(days=i)
    d_str = day.strftime("%Y-%m-%d")
    is_sel = "border: 1px solid #58A6FF;" if day == st.session_state.selected_date else ""
    
    with cols[i]:
        # В кнопке пишем День недели + Число
        if st.button(f"{week_days[i]}\n{day.day}", key=f"d_{d_str}"):
            st.session_state.selected_date = day
            st.rerun()
        # Точка если есть тренировка
        if d_str in data["days"] and data["days"][d_str].get("exercises"):
            st.markdown("<div style='height:3px; width:3px; background:#58A6FF; border-radius:50%; margin:-8px auto 5px auto;'></div>", unsafe_allow_html=True)

st.divider()

# СПИСОК УПРАЖНЕНИЙ
sel_str = st.session_state.selected_date.strftime("%Y-%m-%d")
day_info = data["days"].get(sel_str, {"exercises": []})

# Добавление (сразу сверху, чтобы было под рукой)
with st.popover("➕ Добавить", use_container_width=True):
    name = st.text_input("Название")
    if st.button("OK"):
        if name:
            if sel_str not in data["days"]: data["days"][sel_str] = {"exercises": []}
            data["days"][sel_str]["exercises"].append({"name": name, "sets": []})
            save_data(data); st.rerun()

# Список карточек
for i, ex in enumerate(day_info["exercises"]):
    with st.expander(f"**{ex['name'].upper()}**", expanded=False):
        # Список подходов
        for s_idx, s in enumerate(ex.get("sets", [])):
            st.write(f"{s_idx+1}. {s['w']} кг — {s['r']} повт.")
        
        # Форма ввода
        cw, cr, cb = st.columns([3, 3, 2])
        w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
        r = cr.number_input("Р", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
        if cb.button("➕", key=f"add_{i}"):
            ex["sets"].append({"w": str(w), "r": str(r)})
            save_data(data); st.rerun()
        
        if st.button("🗑️ Удалить", key=f"del_{i}"):
            day_info["exercises"].pop(i); save_data(data); st.rerun()

if not day_info["exercises"]:
    st.caption("На этот день ничего не запланировано")
