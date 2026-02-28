import streamlit as st
import json
import os
from datetime import datetime

# Базовая настройка
st.set_page_config(page_title="Gym App", layout="centered")

# Функция данных (максимально простая)
def get_data():
    if not os.path.exists("gym_data.json"):
        with open("gym_data.json", "w") as f: json.dump({"days": {}}, f)
    with open("gym_data.json", "r") as f: return json.load(f)

def save_data(data):
    with open("gym_data.json", "w") as f: json.dump(data, f)

# Стили для красоты, но без вреда для верстки
st.markdown("""
<style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5rem; margin-bottom: 10px; }
    .stDateInput div { width: 100%; }
    .exercise-card { background: #262730; padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

st.title("🏋️ Тренировки")

# 1. Выбор даты (Стандартное мобильное окно)
selected_date = st.date_input("Выберите день", datetime.now()).strftime("%Y-%m-%d")

# 2. Загрузка данных
data = get_data()
day_info = data["days"].get(selected_date, {"exercises": []})

# 3. Кнопка добавления упражнения
if st.button("➕ Добавить новое упражнение"):
    st.session_state.show_add = True

if st.session_state.get("show_add"):
    with st.form("add_form"):
        name = st.text_input("Название (например: Жим)")
        if st.form_submit_button("Сохранить"):
            if selected_date not in data["days"]: data["days"][selected_date] = {"exercises": []}
            data["days"][selected_date]["exercises"].append({"name": name, "sets": []})
            save_data(data)
            st.session_state.show_add = False
            st.rerun()

st.write("---")

# 4. Список упражнений (одно под другим)
if not day_info["exercises"]:
    st.write("На сегодня планов нет")
else:
    for i, ex in enumerate(day_info["exercises"]):
        st.markdown(f"""<div class="exercise-card"><b>{ex['name'].upper()}</b></div>""", unsafe_allow_html=True)
        
        # Список подходов
        for s in ex.get("sets", []):
            st.write(f"💪 {s['w']} кг x {s['r']} раз")
        
        # Кнопки управления (друг под другом для мобилки)
        with st.expander("Добавить подход / Удалить"):
            w = st.number_input("Вес (кг)", 0.0, step=0.5, key=f"w_{i}")
            r = st.number_input("Повторы", 0, step=1, key=f"r_{i}")
            if st.button("✅ Записать подход", key=f"save_{i}"):
                ex["sets"].append({"w": str(w), "r": str(r)})
                save_data(data)
                st.rerun()
            
            if st.button("🗑️ Удалить упражнение", key=f"del_{i}"):
                day_info["exercises"].pop(i)
                save_data(data)
                st.rerun()
