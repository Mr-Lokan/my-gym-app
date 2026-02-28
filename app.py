import streamlit as st
import streamlit_antd_components as sac
import json
import os
import calendar
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gym Legend Pro", layout="centered")

# --- ГЛОБАЛЬНЫЕ СТИЛИ ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #0d1117; }
    .block-container { padding: 1rem !important; max-width: 450px !important; padding-bottom: 100px !important; }
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 3px; table-layout: fixed; }
    .cal-day { background: #161b22; border: 1px solid #30363d; border-radius: 6px; height: 35px; text-align: center; color: #f0f6fc; font-size: 12px; position: relative; line-height: 35px; }
    .dot { position: absolute; bottom: 3px; left: 50%; transform: translateX(-50%); width: 4px; height: 4px; background-color: #58a6ff; border-radius: 50%; }
    .ex-card { background: #1c2128; border: 1px solid #30363d; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- РАБОТА С ДАННЫМИ ---
def load_data():
    if os.path.exists("gym_data.json"):
        try:
            with open("gym_data.json", "r", encoding="utf-8") as f:
                d = json.load(f)
                d.setdefault("days", {}); d.setdefault("templates", {})
                return d
        except: pass
    return {"days": {}, "templates": {}}

def save_data(data):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- НИЖНЕЕ МЕНЮ (NAVIGATION) ---
menu = sac.bottom_nav(
    items=[
        sac.BottomNavItem(label='Тренировка', icon='calendar-event'),
        sac.BottomNavItem(label='Шаблоны', icon='clipboard-check'),
        sac.BottomNavItem(label='Стата', icon='graph-up-arrow'),
        sac.BottomNavItem(label='Профиль', icon='person-gear'),
    ],
    selected_index=0,
    key='nav_menu'
)

# --- ЛОГИКА ВКЛАДОК ---

# 1. ВКЛАДКА: ТРЕНИРОВКА
if menu == 'Тренировка':
    st.markdown("### 🏋️ Мой Календарь")
    
    # Календарь (упрощенный визуал)
    now = datetime.now()
    if 'v_m' not in st.session_state: st.session_state.v_m = now.month
    if 'v_y' not in st.session_state: st.session_state.v_y = now.year
    
    c1, c2, c3 = st.columns([1,2,1])
    if c1.button("←"): 
        st.session_state.v_m -= 1
        if st.session_state.v_m == 0: st.session_state.v_m = 12; st.session_state.v_y -= 1
        st.rerun()
    c2.write(f"**{st.session_state.v_m:02d}.{st.session_state.v_y}**")
    if c3.button("→"): 
        st.session_state.v_m += 1
        if st.session_state.v_m == 13: st.session_state.v_m = 1; st.session_state.v_y += 1
        st.rerun()

    cal = calendar.monthcalendar(st.session_state.v_y, st.session_state.v_m)
    html_grid = '<table class="cal-table"><tr><th>ПН</th><th>ВТ</th><th>СР</th><th>ЧТ</th><th>ПТ</th><th>СБ</th><th>ВС</th></tr>'
    for week in cal:
        html_grid += '<tr>'
        for day in week:
            if day == 0: html_grid += '<td class="cal-day" style="background:transparent; border:none;"></td>'
            else:
                d_key = f"{st.session_state.v_y}-{st.session_state.v_m:02d}-{day:02d}"
                dot = '<div class="dot"></div>' if d_key in st.session_state.db["days"] and st.session_state.db["days"][d_key] else ""
                html_grid += f'<td class="cal-day">{day}{dot}</td>'
        html_grid += '</tr>'
    st.markdown(html_grid + '</table>', unsafe_allow_html=True)

    days_in_m = calendar.monthrange(st.session_state.v_y, st.session_state.v_m)[1]
    sel_day = st.selectbox("День:", range(1, days_in_m + 1), index=now.day-1 if st.session_state.v_m == now.month else 0)
    target_date = f"{st.session_state.v_y}-{st.session_state.v_m:02d}-{sel_day:02d}"

    st.divider()
    
    # План упражнений
    day_data = st.session_state.db["days"].get(target_date, [])
    
    # Кнопки действий
    btn_col1, btn_col2 = st.columns(2)
    if btn_col1.button("➕ Упражнение", use_container_width=True): st.session_state.add_ex = True
    if btn_col2.button("📋 Из шаблона", use_container_width=True): st.session_state.use_tmpl = True

    if st.session_state.get("add_ex"):
        with st.form("add_ex_form"):
            name = st.text_input("Название")
            if st.form_submit_button("Добавить"):
                if target_date not in st.session_state.db["days"]: st.session_state.db["days"][target_date] = []
                st.session_state.db["days"][target_date].append({"name": name, "sets": []})
                save_data(st.session_state.db); st.session_state.add_ex = False; st.rerun()

    for i, ex in enumerate(day_data):
        with st.container(border=True):
            st.write(f"**{ex.get('name','').upper()}**")
            sets = ex.get('sets', [])
            if sets: st.caption(" | ".join([f"{s['w']}×{s['r']}" for s in sets]))
            
            c1, c2 = st.columns([4, 1])
            with c1.expander("Сет"):
                cw, cr, cb = st.columns([2, 2, 1])
                w = cw.number_input("Кг", 0.0, key=f"w_{target_date}_{i}")
                r = cr.number_input("Р", 0, key=f"r_{target_date}_{i}")
                if cb.button("➕", key=f"ok_{target_date}_{i}"):
                    ex['sets'].append({"w": str(w), "r": str(r)})
                    save_data(st.session_state.db); st.rerun()
            if c2.button("🗑️", key=f"del_{target_date}_{i}"):
                day_data.pop(i); save_data(st.session_state.db); st.rerun()

# 2. ВКЛАДКА: ШАБЛОНЫ
elif menu == 'Шаблоны':
    st.markdown("### 📋 Мои Шаблоны")
    tmpl_name = st.text_input("Название нового шаблона (напр. 'Грудь+Трицепс')")
    if st.button("Создать шаблон"):
        if tmpl_name:
            st.session_state.db["templates"][tmpl_name] = []
            save_data(st.session_state.db); st.rerun()
    
    for t_name, t_exs in st.session_state.db["templates"].items():
        with st.expander(f"Шаблон: {t_name}"):
            new_ex = st.text_input("Добавить упр. в шаблон", key=f"t_in_{t_name}")
            if st.button("Добавить", key=f"t_btn_{t_name}"):
                t_exs.append(new_ex); save_data(st.session_state.db); st.rerun()
            st.write(", ".join(t_exs))
            if st.button("Удалить шаблон", key=f"t_del_{t_name}"):
                del st.session_state.db["templates"][t_name]; save_data(st.session_state.db); st.rerun()

# 3. ВКЛАДКА: СТАТИСТИКА
elif menu == 'Стата':
    st.markdown("### 📊 Статистика")
    all_data = []
    for date, exs in st.session_state.db["days"].items():
        for ex in exs:
            for s in ex.get('sets', []):
                all_data.append({"Дата": date, "Вес": float(s['w']), "Повторы": int(s['r'])})
    
    if all_data:
        df = pd.DataFrame(all_data)
        df['Дата'] = pd.to_datetime(df['Дата'])
        st.line_chart(df.groupby('Дата')['Вес'].max())
        st.write("Максимальные веса по датам")
    else:
        st.info("Нет данных для анализа")

# 4. ВКЛАДКА: ПРОФИЛЬ
elif menu == 'Профиль':
    st.markdown("### ⚙️ Настройки")
    if st.button("🚨 ОЧИСТИТЬ ВСЕ ДАННЫЕ"):
        st.session_state.db = {"days": {}, "templates": {}}
        save_data(st.session_state.db); st.rerun()
    st.write("Версия: 3.0 Pro")
