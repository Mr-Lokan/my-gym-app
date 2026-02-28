import streamlit as st
import json
import os
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Gym Legend", layout="centered")

# --- СТИЛИЗАЦИЯ ПОД APPLE HEALTH ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }
    .stApp { background-color: #000000; }
    
    /* Стилизация календаря */
    .stDateInput div[data-baseweb="input"] {
        background-color: #1c1c1e !important;
        border: 1px solid #2c2c2e !important;
        border-radius: 12px !important;
        color: white !important;
    }

    /* Карточка упражнения */
    .ex-card {
        background: #1c1c1e;
        border-radius: 15px;
        padding: 16px;
        margin-top: 12px;
        border: 1px solid #2c2c2e;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .ex-title { 
        color: #ffffff; 
        font-weight: 800; 
        font-size: 18px; 
        letter-spacing: -0.5px;
        margin-bottom: 8px;
        text-transform: uppercase;
    }
    .set-badge {
        background: #2c2c2e;
        color: #58A6FF;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 13px;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
    
    /* Кнопки */
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ДАННЫХ ---
DB_FILE = "gym_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {"days": {}}
    return {"days": {}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- ВЕРХНЯЯ ЧАСТЬ ---
st.markdown("<h1 style='text-align: center; color: white; font-size: 24px;'>GYM LEGEND</h1>", unsafe_allow_html=True)

# Календарь (тот самый, удобный)
d = st.date_input("Выбор даты", value=datetime.now(), label_visibility="collapsed")
target_date = d.strftime("%Y-%m-%d")

# Кнопка добавления нового упражнения
if st.button("🚀 Добавить упражнение", use_container_width=True):
    st.session_state.show_add = True

if st.session_state.get("show_add"):
    with st.form("add_ex_form"):
        name = st.text_input("Название упражнения")
        if st.form_submit_button("Добавить"):
            if target_date not in st.session_state.db["days"]:
                st.session_state.db["days"][target_date] = []
            st.session_state.db["days"][target_date].append({"name": name, "sets": []})
            save_data(st.session_state.db)
            st.session_state.show_add = False
            st.rerun()

st.markdown("<hr style='margin: 15px 0; border-color: #2c2c2e;'>", unsafe_allow_html=True)

# --- СПИСОК УПРАЖНЕНИЙ ---
day_data = st.session_state.db["days"].get(target_date, [])

if not day_data:
    st.markdown("<p style='text-align: center; color: #8e8e93;'>На этот день тренировок нет</p>", unsafe_allow_html=True)
else:
    for i, ex in enumerate(day_data):
        # Красивая карточка через HTML
        st.markdown(f"""
        <div class="ex-card">
            <div class="ex-title">{ex['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Вывод сетов в виде "баджей"
        if ex.get('sets'):
            sets_html = "".join([f'<span class="set-badge">{s["w"]}кг × {s["r"]}</span>' for s in ex['sets']])
            st.markdown(f"<div>{sets_html}</div>", unsafe_allow_html=True)
        
        # Кнопки управления
        c1, c2 = st.columns([4, 1])
        with c1.expander("📝 Добавить подход"):
            cw, cr, cb = st.columns([2, 2, 1])
            w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
            r = cr.number_input("Р", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
            if cb.button("➕", key=f"ok_{i}"):
                ex['sets'].append({"w": str(w), "r": str(r)})
                save_data(st.session_state.db)
                st.rerun()
        
        if c2.button("🗑️", key=f"del_{i}"):
            day_data.pop(i)
            save_data(st.session_state.db)
            st.rerun()
