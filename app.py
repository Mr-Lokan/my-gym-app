import streamlit as st
import json
import os
from datetime import datetime

st.set_page_config(page_title="Gym Legend", layout="centered")

# Чистый CSS без фанатизма, чтобы ничего не плыло
st.markdown("""
<style>
    [data-testid="stHeader"] {display: none;}
    .block-container {padding-top: 1rem !important;}
    .stDateInput label {display:none;}
    .stButton>button {width:100%; border-radius:10px; height:3em;}
    .ex-box {
        background-color: #1e2124;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    if os.path.exists("gym_data.json"):
        with open("gym_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {"days": {}}

def save_data(d):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("🏋️ Gym Legend")

# ВЫБОР ДАТЫ - одна кнопка, которая открывает календарь
d = st.date_input("Выбери дату", value=datetime.now())
sel_date = d.strftime("%Y-%m-%d")

st.info(f"📅 Дата: {sel_date}")

# Кнопка добавить
if st.button("➕ Добавить упражнение"):
    st.session_state.add_mode = True

if st.session_state.get("add_mode"):
    with st.form("new_ex"):
        name = st.text_input("Название")
        if st.form_submit_button("Сохранить"):
            if sel_date not in data["days"]: data["days"][sel_date] = {"exercises": []}
            data["days"][sel_date]["exercises"].append({"name": name, "sets": []})
            save_data(data)
            st.session_state.add_mode = False
            st.rerun()

# Список упражнений
day_info = data["days"].get(sel_date, {"exercises": []})

for i, ex in enumerate(day_info["exercises"]):
    with st.container():
        st.markdown(f'<div class="ex-box"><b>{ex["name"].upper()}</b></div>', unsafe_allow_html=True)
        
        # Вывод подходов в строчку
        res = " | ".join([f"{s['w']}x{s['r']}" for s in ex.get('sets', [])])
        st.caption(res if res else "Нет подходов")
        
        col1, col2 = st.columns([4, 1])
        with col1.expander("Добавить подход"):
            c_w, c_r = st.columns(2)
            w = c_w.number_input("Кг", 0.0, step=0.5, key=f"w_{i}")
            r = c_r.number_input("Повт", 0, step=1, key=f"r_{i}")
            if st.button("Записать", key=f"btn_{i}"):
                ex["sets"].append({"w": str(w), "r": str(r)})
                save_data(data)
                st.rerun()
        
        if col2.button("🗑️", key=f"del_{i}"):
            day_info["exercises"].pop(i)
            save_data(data)
            st.rerun()
