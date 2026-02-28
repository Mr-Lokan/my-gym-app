import streamlit as st
import streamlit_antd_components as sac
import json
import os
from datetime import datetime, timedelta

# Настройки для мобилок
st.set_page_config(page_title="Gym Pro", layout="centered")

# --- СТИЛЬ «APPLE HEALTH» ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }
    .stApp { background-color: #000000; }
    
    /* Карточки упражнений */
    .ex-card {
        background: #1c1c1e;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        border: 1px solid #2c2c2e;
    }
    .ex-name { color: #ffffff; font-weight: 600; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# --- РАБОТА С ДАННЫМИ ---
def load_data():
    if os.path.exists("gym_data.json"):
        with open("gym_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"days": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

# --- ИНТЕРФЕЙС ---
st.markdown("<h3 style='color:white; margin-bottom:20px;'>🏋️ Мои тренировки</h3>", unsafe_allow_html=True)

# 1. СТИЛЬНЫЙ ВЫБОР ДНЯ (Segmented Control)
# Создаем список из 7 дней (текущая неделя)
today = datetime.now().date()
start_week = today - timedelta(days=today.weekday())
days_list = []
for i in range(7):
    d = start_week + timedelta(days=i)
    days_list.append(sac.SegmentedItem(label=d.strftime('%d'), caption=d.strftime('%a')))

sel_idx = sac.segmented(
    items=days_list,
    index=today.weekday(),
    align='center',
    size='sm',
    color='indigo',
    return_index=True
)

target_date = (start_week + timedelta(days=sel_idx)).strftime("%Y-%m-%d")

# 2. КНОПКА ДОБАВЛЕНИЯ
if sac.buttons([sac.ButtonsItem(label='Добавить упражнение', icon='plus-circle-fill')], 
               align='center', variant='link', color='indigo'):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("add_ex"):
        name = st.text_input("Название (например, Приседания)")
        if st.form_submit_button("Сохранить"):
            if target_date not in data["days"]: data["days"][target_date] = {"exercises": []}
            data["days"][target_date]["exercises"].append({"name": name, "sets": []})
            save_data(data)
            st.session_state.show_form = False
            st.rerun()

st.markdown(f"<p style='color:#8e8e93; font-size:12px;'>ПЛАН НА {target_date}</p>", unsafe_allow_html=True)

# 3. СПИСОК УПРАЖНЕНИЙ
day_info = data["days"].get(target_date, {"exercises": []})

if not day_info["exercises"]:
    st.caption("Пока пусто. Добавь первое упражнение!")
else:
    for i, ex in enumerate(day_info["exercises"]):
        # Рисуем карточку
        st.markdown(f"<div class='ex-card'><div class='ex-name'>{ex['name'].upper()}</div></div>", unsafe_allow_html=True)
        
        # Управление сетами
        cols = st.columns([4, 1])
        sets_preview = " | ".join([f"{s['w']}x{s['r']}" for s in ex.get('sets', [])])
        cols[0].caption(sets_preview if sets_preview else "Нет подходов")
        
        if cols[1].button("🗑️", key=f"del_{i}"):
            day_info["exercises"].pop(i)
            save_data(data)
            st.rerun()
            
        with st.expander("Записать подход"):
            c1, c2, c3 = st.columns([2, 2, 1])
            w = c1.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
            r = c2.number_input("П", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
            if c3.button("✅", key=f"save_{i}"):
                ex["sets"].append({"w": str(w), "r": str(r)})
                save_data(data)
                st.rerun()
