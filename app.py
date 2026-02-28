import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime, timedelta
import calendar

st.set_page_config(page_title="Gym Legend Elite", layout="centered")

def load_data():
    path = "gym_data.json"
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "days" not in data: data["days"] = {}
                if "templates" not in data: data["templates"] = {}
                if "tmpl_colors" not in data: data["tmpl_colors"] = {}
                # Лечим старые ошибки данных (AttributeError Fix)
                for date in list(data["days"].keys()):
                    if isinstance(data["days"][date], list):
                        data["days"][date] = {"template": None, "exercises": data["days"][date]}
                return data
        except: pass
    return {"days": {}, "templates": {}, "tmpl_colors": {}}

def save_data(data):
    # Очистка пустых записей перед сохранением
    to_del = [d for d, v in data["days"].items() if not v.get("exercises")]
    for d in to_del: del data["days"][d]
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

data = load_data()

st.title("🏋️ GYM LEGEND ELITE")

tab_work, tab_plan, tab_stats = st.tabs(["💪 Тренировка", "📅 Планирование", "📈 Прогресс"])

# --- ВКЛАДКА 1: ТРЕНИРОВКА ---
with tab_work:
    st.subheader("📅 Календарь")
    
    col_m, col_y = st.columns(2)
    c_m = col_m.selectbox("Месяц", range(1, 13), index=datetime.now().month-1)
    c_y = col_y.number_input("Год", value=datetime.now().year)
    
    # Чтобы календарь не разваливался на мобильных, используем контейнеры
    days_abbr = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    cols_header = st.columns(7)
    for i, name in enumerate(days_abbr):
        cols_header[i].write(f"**{name}**")
    
    cal = calendar.monthcalendar(int(c_y), int(c_m))
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day != 0:
                d_str = f"{c_y}-{c_m:02d}-{day:02d}"
                
                # Ищем цвет шаблона
                marker = ""
                if d_str in data["days"]:
                    t_name = data["days"][d_str].get("template")
                    c = data["tmpl_colors"].get(t_name, "#58A6FF")
                    # Визуальный маркер (точка)
                    marker = f"<div style='color:{c}; font-size:24px; margin-top:-10px; text-align:center;'>•</div>"
                
                if cols[i].button(str(day), key=f"d_{d_str}", use_container_width=True):
                    st.session_state.sel_date = d_str
                
                if marker:
                    cols[i].markdown(marker, unsafe_allow_html=True)

    st.divider()
    
    # Работа с выбранной датой
    curr_date = st.session_state.get('sel_date', str(datetime.now().date()))
    st.info(f"Выбрано: **{curr_date}**")
    
    day_info = data["days"].get(curr_date, {"exercises": []})
    ex_list = day_info.get("exercises", [])

    if ex_list:
        for i, ex in enumerate(ex_list):
            with st.expander(f"🔹 {ex['name'].upper()}", expanded=True):
                if st.button(f"🗑️ Удалить", key=f"del_{curr_date}_{i}"):
                    ex_list.pop(i)
                    save_data(data)
                    st.rerun()
                
                for s in ex.get("sets", []):
                    st.write(f"✅ {s['w']} кг x {s['r']}")
                
                with st.form(f"f_{curr_date}_{i}", clear_on_submit=True):
                    c1, c2 = st.columns(2)
                    w = c1.number_input("Вес", min_value=0.0, step=0.5, key=f"w_{i}")
                    r = c2.number_input("Повт", min_value=0, step=1, key=f"r_{i}")
                    if st.form_submit_button("➕ Сет"):
                        ex["sets"].append({"w": str(w), "r": str(r)})
                        save_data(data)
                        st.rerun()
    else:
        st.write("На этот день нет записей.")

# --- ВКЛАДКА 2: ПЛАНИРОВАНИЕ ---
with tab_plan:
    st.header("⚙️ Настройки")
    
    with st.expander("⚠️ ОЧИСТКА КАЛЕНДАРЯ"):
        if st.button("🔥 УДАЛИТЬ ВСЕ ТРЕНИРОВКИ", type="primary"):
            data["days"] = {}
            save_data(data)
            st.rerun()

    st.divider()
    
    with st.expander("➕ Создать шаблон"):
        name = st.text_input("Название (напр. Спина)")
        color = st.color_picker("Цвет", "#FF00FF")
        exs = st.text_area("Упражнения (через Enter)")
        if st.button("Сохранить шаблон"):
            if name and exs:
                data["templates"][name] = [x.strip() for x in exs.split('\n') if x.strip()]
                data["tmpl_colors"][name] = color
                save_data(data)
                st.rerun()

    if data["templates"]:
        st.subheader("🗓️ Расставить по дням")
        target = st.selectbox("Шаблон", list(data["templates"].keys()))
        
        # Исправленная логика выбора дней недели
        st.write("Дни недели:")
        day_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        sel_w_days = []
        cols = st.columns(7)
        for i, col in enumerate(cols):
            if col.checkbox(day_names[i], key=f"wd_{i}"):
                sel_w_days.append(i)
        
        # ВАЖНО: Выбор начальной и конечной даты
        col_s, col_e = st.columns(2)
        start_dt = col_s.date_input("С какого числа", datetime.now())
        end_dt = col_e.date_input("По какое число", datetime.now() + timedelta(days=31))
        
        if st.button("⚡ Заполнить Пн и Пт (или другие)", type="primary"):
            if not sel_w_days:
                st.error("Выберите дни недели!")
            else:
                # Цикл теперь идет СТРОГО от выбранной даты старта до конца
                curr = datetime.combine(start_dt, datetime.min.time())
                limit = datetime.combine(end_dt, datetime.min.time())
                count = 0
                while curr <= limit:
                    if curr.weekday() in sel_w_days:
                        ds = curr.strftime("%Y-%m-%d")
                        data["days"][ds] = {
                            "template": target,
                            "exercises": [{"name": n, "sets": []} for n in data["templates"][target]]
                        }
                        count += 1
                    curr += timedelta(days=1)
                save_data(data)
                st.success(f"Добавлено {count} тренировок! (Проверьте 30-е число)")
                st.rerun()

# --- ВКЛАДКА 3: ПРОГРЕСС ---
with tab_stats:
    st.header("📈 Прогресс")
    # Аналитика остается без изменений