import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Mobile", layout="centered")

# --- ФУНКЦИИ ДАННЫХ ---
def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "days" not in data: data["days"] = {}
                if "templates" not in data: data["templates"] = {}
                if "tmpl_colors" not in data: data["tmpl_colors"] = {}
                return data
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(data):
    to_del = [d for d, v in data["days"].items() if not v.get("exercises")]
    for d in to_del: del data["days"][d]
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("🏋️ GYM LEGEND")

tab_work, tab_plan, tab_stats = st.tabs(["💪 Журнал", "📅 План", "📈 График"])

# --- ВКЛАДКА 1: ЖУРНАЛ (ИСПРАВЛЕННЫЙ МОБИЛЬНЫЙ ВИД) ---
with tab_work:
    st.subheader("📅 Выбор даты")
    
    # Вместо сетки кнопок используем календарный виджет (он идеально работает на тачскринах)
    if 'sel_date' not in st.session_state:
        st.session_state.sel_date = datetime.now().date()

    chosen_date = st.date_input("Нажми, чтобы выбрать день", st.session_state.sel_date)
    date_str = str(chosen_date)
    st.session_state.sel_date = chosen_date

    # Быстрый просмотр: Список ближайших тренировок
    with st.expander("🔍 Список всех тренировок в этом месяце"):
        if data["days"]:
            # Фильтруем дни текущего месяца
            month_prefix = chosen_date.strftime("%Y-%m")
            month_days = [d for d in data["days"] if d.startswith(month_prefix)]
            if month_days:
                for d in sorted(month_days):
                    t_name = data["days"][d].get("template", "Своя")
                    color = data["tmpl_colors"].get(t_name, "#58A6FF")
                    if st.button(f"📅 {d} | {t_name}", key=f"quick_{d}"):
                        st.session_state.sel_date = datetime.strptime(d, "%Y-%m-%d").date()
                        st.rerun()
            else:
                st.write("В этом месяце пока пусто")
        else:
            st.write("История пуста")

    st.divider()
    
    # Секция упражнений
    st.markdown(f"### 📝 Записи за {date_str}")
    day_info = data["days"].get(date_str, {"exercises": []})
    ex_list = day_info.get("exercises", [])

    if ex_list:
        for i, ex in enumerate(ex_list):
            with st.expander(f"🔹 {ex['name'].upper()}", expanded=True):
                # Удаление
                if st.button(f"🗑️ Удалить упражнение", key=f"del_{date_str}_{i}"):
                    ex_list.pop(i)
                    save_data(data)
                    st.rerun()
                
                # Подходы
                for s_idx, s in enumerate(ex.get("sets", [])):
                    st.write(f"**{s_idx+1}** | {s['w']} кг x {s['r']}")
                
                # Добавление сета
                with st.form(f"form_{date_str}_{i}", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    w = c1.number_input("Кг", min_value=0.0, step=0.5, key=f"w_{i}")
                    r = c2.number_input("Раз", min_value=0, step=1, key=f"r_{i}")
                    if st.form_submit_button("➕ Добавить подход"):
                        ex["sets"].append({"w": str(w), "r": str(r)})
                        save_data(data)
                        st.rerun()
    else:
        st.info("Нет записей на сегодня")

    # Добавление нового упражнения вручную
    with st.popover("🚀 Добавить упражнение"):
        new_name = st.text_input("Название")
        if st.button("Добавить"):
            if new_name:
                if date_str not in data["days"]: data["days"][date_str] = {"template": None, "exercises": []}
                data["days"][date_str]["exercises"].append({"name": new_name.strip(), "sets": []})
                save_data(data)
                st.rerun()

# --- ВКЛАДКА 2: ПЛАНИРОВАНИЕ ---
with tab_plan:
    # Здесь остается твой код для создания шаблонов и кнопка Очистки
    with st.expander("⚠️ Настройки"):
        if st.button("🔥 ПОЛНАЯ ОЧИСТКА КАЛЕНДАРЯ", type="primary"):
            data["days"] = {}
            save_data(data)
            st.rerun()
            
    # Добавим кнопку скачивания JSON, чтобы не терять данные
    st.divider()
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    st.download_button(
        label="📥 Скачать бэкап (gym_data.json)",
        data=json_data,
        file_name="gym_data.json",
        mime="application/json"
    )
