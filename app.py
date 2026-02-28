import streamlit as st
import json
import os
from datetime import datetime

# Настройка страницы
st.set_page_config(page_title="Gym Legend Ultra", layout="centered")

# --- ФОН И КАРТОЧКИ (ПОЛНЫЙ РЕДИЗАЙН) ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #050505; }
    .block-container { padding-top: 2rem !important; max-width: 400px !important; }
    
    /* Стилизация заголовка */
    .main-title {
        font-size: 32px;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        letter-spacing: -1px;
        margin-bottom: 20px;
        text-shadow: 0 0 15px rgba(88, 166, 255, 0.4);
    }

    /* Нативный календарь как стильная кнопка */
    .stDateInput div[data-baseweb="input"] {
        background-color: #161b22 !important;
        border: 2px solid #30363d !important;
        border-radius: 15px !important;
        height: 50px !important;
        color: #58a6ff !important;
        font-weight: bold !important;
    }

    /* КАРТОЧКА УПРАЖНЕНИЯ */
    .exercise-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .exercise-header {
        color: #58a6ff;
        font-size: 18px;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 10px;
        border-left: 4px solid #58a6ff;
        padding-left: 10px;
    }

    /* Подходы (Баджи) */
    .set-tag {
        background: #21262d;
        color: #f0f6fc;
        padding: 6px 12px;
        border-radius: 10px;
        font-size: 14px;
        font-family: monospace;
        margin: 3px;
        display: inline-block;
        border: 1px solid #30363d;
    }

    /* Кнопки */
    .stButton>button {
        border-radius: 15px !important;
        background-color: #21262d !important;
        color: white !important;
        border: 1px solid #30363d !important;
        transition: 0.3s;
    }
    .stButton>button:active {
        transform: scale(0.95);
        border-color: #58a6ff !important;
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

# --- ИНТЕРФЕЙС ---
st.markdown("<div class='main-title'>LEGEND BORN</div>", unsafe_allow_html=True)

# Календарь
d = st.date_input("DATE", value=datetime.now(), label_visibility="collapsed")
target_date = d.strftime("%Y-%m-%d")

# Добавление
if st.button("➕ ДОБАВИТЬ ТРЕНИРОВКУ", use_container_width=True):
    st.session_state.add_mode = True

if st.session_state.get("add_mode"):
    with st.form("new_ex"):
        name = st.text_input("Название упражнения")
        if st.form_submit_button("СОХРАНИТЬ"):
            if target_date not in st.session_state.db["days"]:
                st.session_state.db["days"][target_date] = []
            st.session_state.db["days"][target_date].append({"name": name, "sets": []})
            save_data(st.session_state.db)
            st.session_state.add_mode = False
            st.rerun()

# Рендер упражнений
day_data = st.session_state.db["days"].get(target_date, [])

if not day_data:
    st.markdown("<p style='text-align:center; color:#8b949e; margin-top:30px;'>Сегодня день отдыха 🧘</p>", unsafe_allow_html=True)
else:
    for i, ex in enumerate(day_data):
        # Отрисовка карточки
        st.markdown(f"""
        <div class="exercise-card">
            <div class="exercise-header">{ex['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Подходы
        if ex.get('sets'):
            sets_html = "".join([f'<div class="set-tag">{s["w"]}kg × {s["r"]}</div>' for s in ex['sets']])
            st.markdown(f"<div style='margin-bottom:10px;'>{sets_html}</div>", unsafe_allow_html=True)
        
        # Управление
        c1, c2 = st.columns([4, 1])
        with c1.expander("📝 ДОБАВИТЬ СЕТ"):
            col_w, col_r, col_b = st.columns([2, 2, 1])
            w = col_w.number_input("Кг", 0.0, step=0.5, key=f"w_{i}", label_visibility="collapsed")
            r = col_r.number_input("Р", 0, step=1, key=f"r_{i}", label_visibility="collapsed")
            if col_b.button("➕", key=f"ok_{i}"):
                ex['sets'].append({"w": str(w), "r": str(r)})
                save_data(st.session_state.db)
                st.rerun()
        
        if c2.button("🗑️", key=f"del_{i}"):
            day_data.pop(i)
            save_data(st.session_state.db)
            st.rerun()
