import streamlit as st
import streamlit_antd_components as sac
import json
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Gym Legend Pro", layout="centered")

# --- СТИЛИЗАЦИЯ ДЛЯ КРАСОТЫ ---
st.markdown("""
<style>
    .stApp { background-color: #0c0d0e; }
    [data-testid="stHeader"] { display: none; }
    .block-container { padding-top: 1rem !important; }
    
    /* Красивая карточка упражнения */
    .ex-card {
        background: #1c1c1e;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #2c2c2e;
    }
    .ex-title { color: #ffffff; font-weight: 700; font-size: 16px; margin-bottom: 5px; }
    .set-row { color: #8e8e93; font-size: 14px; }
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

# --- ВЕРХНЯЯ ПАНЕЛЬ ---
st.write("### 🏋️ GYM LEGEND")

# Красивый выбор дня недели (Ant Design)
# Генерируем даты текущей недели
start_wk = datetime.now().date() - timedelta(days=datetime.now().weekday())
days_options = []
for i in range(7):
    d = start_wk + timedelta(days=i)
    label = f"{d.strftime('%a')}\n{d.day}"
    days_options.append(sac.SegmentedItem(label=label))

selected_idx = sac.segmented(
    items=days_options,
    align='center',
    size='sm',
    color='blue',
    index=datetime.now().weekday(),
    return_index=True
)

target_date = (start_wk + timedelta(days=selected_idx)).strftime("%Y-%m-%d")

# --- СПИСОК УПРАЖНЕНИЙ ---
st.markdown(f"#### {target_date}")

day_info = data["days"].get(target_date, {"exercises": []})

# Кнопка добавления (красивая)
if sac.buttons([sac.ButtonsItem(label='Добавить упражнение', icon='plus-lg')], align='center', variant='filled'):
    st.session_state.adding = True

if st.session_state.get("adding"):
    with st.form("add_form"):
        name = st.text_input("Название")
        if st.form_submit_button("Сохранить"):
            if target_date not in data["days"]: data["days"][target_date] = {"exercises": []}
            data["days"][target_date]["exercises"].append({"name": name, "sets": []})
            save_data(data)
            st.session_state.adding = False
            st.rerun()

# Рендер карточек
for i, ex in enumerate(day_info["exercises"]):
    st.markdown(f"""
    <div class="ex-card">
        <div class="ex-title">{ex['name'].upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Подходы и управление внутри контейнера под карточкой
    cols = st.columns([4, 1])
    sets_text = " | ".join([f"{s['w']}kg x {s['r']}" for s in ex.get("sets", [])])
    cols[0].caption(sets_text if sets_text else "Нет подходов")
    
    if cols[1].button("🗑️", key=f"del_{i}"):
        day_info["exercises"].pop(i)
        save_data(data)
        st.rerun()

    with st.expander("Добавить сет"):
        c1, c2, c3 = st.columns([2, 2, 1])
        w = c1.number_input("Кг", 0.0, key=f"w_{i}", label_visibility="collapsed")
        r = c2.number_input("Р", 0, key=f"r_{i}", label_visibility="collapsed")
        if c3.button("➕", key=f"add_{i}"):
            ex["sets"].append({"w": str(w), "r": str(r)})
            save_data(data)
            st.rerun()

st.divider()
sac.buttons([sac.ButtonsItem(label='Настройки', icon='gear')], align='center', variant='link')
