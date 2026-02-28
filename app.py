import streamlit as st
import streamlit_antd_components as sac
import json
import os
from datetime import datetime, timedelta

# Настройки страницы
st.set_page_config(page_title="Gym Legend Pro", layout="centered")

# --- СТИЛЬ «APPLE DARK MODE» ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem !important; max-width: 450px !important; }
    .stApp { background-color: #000000; }
    
    /* Карточка упражнения */
    .ex-card {
        background: #1c1c1e;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
        border: 1px solid #2c2c2e;
    }
    .ex-title { color: #ffffff; font-weight: 700; font-size: 16px; margin-bottom: 5px; text-transform: uppercase; }
    
    /* Убираем лишние отступы у стандартных виджетов */
    .stNumberInput label { display: none; }
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
st.markdown("<h2 style='color:white; text-align:center;'>🏋️ GYM LEGEND</h2>", unsafe_allow_html=True)

# 1. ВЫБОР ДНЯ (Красивая панель Ant Design)
# Берем текущую неделю
today = datetime.now().date()
start_week = today - timedelta(days=today.weekday())
days_items = []

for i in range(7):
    d = start_week + timedelta(days=i)
    # Формируем подпись: Пн, Вт и т.д.
    wd = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"][i]
    days_items.append(sac.SegmentedItem(label=str(d.day), caption=wd))

# Этот компонент идеально держит 7 колонок в ряд
sel_idx = sac.segmented(
    items=days_items,
    index=today.weekday(),
    align='center',
    size='sm',
    color='blue',
    return_index=True
)

target_date = (start_week + timedelta(days=sel_idx)).strftime("%Y-%m-%d")

# 2. КНОПКА ДОБАВЛЕНИЯ
st.write("")
if sac.buttons([sac.ButtonsItem(label='Добавить упражнение', icon='plus-lg')], align='center', variant='filled', color='blue'):
    st.session_state.show_add = True

if st.session_state.get("show_add"):
    with st.form("add_form"):
        name = st.text_input("Название (например: Жим)")
        if st.form_submit_button("Сохранить"):
            if target_date not in st.session_state.db["days"]:
                st.session_state.db["days"][target_date] = []
            st.session_state.db["days"][target_date].append({"name": name, "sets": []})
            save_data(st.session_state.db)
            st.session_state.show_add = False
            st.rerun()

st.markdown(f"<div style='color:#8e8e93; font-size:11px; margin-top:10px;'>ДАТА: {target_date}</div>", unsafe_allow_html=True)

# 3. РЕНДЕР ТРЕНИРОВОК
day_data = st.session_state.db["days"].get(target_date, [])

if not day_data:
    st.caption("На этот день ничего не запланировано.")
else:
    for i, ex in enumerate(day_data):
        # Сама карточка
        st.markdown(f"""
        <div class="ex-card">
            <div class="ex-title">{ex['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Подходы и кнопки управления (в колонках, но очень аккуратно)
        c1, c2 = st.columns([5, 1])
        
        # Красивый вывод подходов
        sets_list = [f"{s['w']}×{s['r']}" for s in ex.get('sets', [])]
        c1.markdown(f"<span style='color:#58A6FF; font-size:14px;'>{' | '.join(sets_list) if sets_list else 'Нет подходов'}</span>", unsafe_allow_html=True)
        
        if c2.button("🗑️", key=f"del_{i}"):
            day_data.pop(i)
            save_data(st.session_state.db)
            st.rerun()
            
        with st.expander("Добавить подход"):
            cw, cr, cb = st.columns([2, 2, 1])
            w = cw.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
            r = cr.number_input("Р", 0, step=1, key=f"r_{i}")
            if cb.button("➕", key=f"ok_{i}"):
                ex['sets'].append({"w": str(w), "r": str(r)})
                save_data(st.session_state.db)
                st.rerun()
