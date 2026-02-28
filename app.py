import streamlit as st
import json
import os
import calendar
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Gym Legend Pro", layout="centered")

# --- СТИЛИЗАЦИЯ ---
st.markdown("""
<style>
    [data-testid="stHeader"] { display: none; }
    .stApp { background-color: #0d1117; }
    .block-container { padding: 1rem !important; max-width: 450px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; justify-content: center; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #161b22; border-radius: 10px; padding: 10px 20px; color: white; border: 1px solid #30363d;
    }
    .cal-table { width: 100%; border-collapse: separate; border-spacing: 3px; table-layout: fixed; }
    .cal-day { background: #161b22; border: 1px solid #30363d; border-radius: 6px; height: 35px; text-align: center; color: #f0f6fc; font-size: 12px; position: relative; line-height: 35px; }
    .dot { position: absolute; bottom: 3px; left: 50%; transform: translateX(-50%); width: 4px; height: 4px; background-color: #58a6ff; border-radius: 50%; }
</style>
""", unsafe_allow_html=True)

# --- ДАННЫЕ ---
def load_data():
    if os.path.exists("gym_data.json"):
        try:
            with open("gym_data.json", "r", encoding="utf-8") as f:
                d = json.load(f)
                if "days" not in d: d["days"] = {}
                if "templates" not in d: d["templates"] = {}
                return d
        except: return {"days": {}, "templates": {}}
    return {"days": {}, "templates": {}}

def save_data(data):
    with open("gym_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if 'db' not in st.session_state:
    st.session_state.db = load_data()

# --- ВЕРХНЕЕ МЕНЮ (ТАБЫ) ---
tab1, tab2, tab3 = st.tabs(["🏋️ План", "📋 Шаблоны", "📈 Стата"])

# ---------------------------------------------------------
# ВКЛАДКА 1: ТРЕНИРОВКА
# ---------------------------------------------------------
with tab1:
    st.write("### Календарь")
    now = datetime.now()
    if 'v_m' not in st.session_state: st.session_state.v_m = now.month
    if 'v_y' not in st.session_state: st.session_state.v_y = now.year
    
    c1, c2, c3 = st.columns([1,2,1])
    if c1.button("←", key="m_prev"): 
        st.session_state.v_m -= 1
        if st.session_state.v_m == 0: st.session_state.v_m = 12; st.session_state.v_y -= 1
        st.rerun()
    c2.markdown(f"<div style='text-align:center;'><b>{st.session_state.v_m:02d}.{st.session_state.v_y}</b></div>", unsafe_allow_html=True)
    if c3.button("→", key="m_next"): 
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
                has_ex = d_key in st.session_state.db["days"] and len(st.session_state.db["days"][d_key]) > 0
                dot = '<div class="dot"></div>' if has_ex else ""
                html_grid += f'<td class="cal-day">{day}{dot}</td>'
        html_grid += '</tr>'
    st.markdown(html_grid + '</table>', unsafe_allow_html=True)

    days_in_m = calendar.monthrange(st.session_state.v_y, st.session_state.v_m)[1]
    sel_day = st.selectbox("Выбери день месяца:", range(1, days_in_m + 1), index=now.day-1 if st.session_state.v_m == now.month else 0)
    target_date = f"{st.session_state.v_y}-{st.session_state.v_m:02d}-{sel_day:02d}"

    st.divider()
    
    # Кнопки добавления
    col_add1, col_add2 = st.columns(2)
    if col_add1.button("➕ Упражнение", use_container_width=True): st.session_state.add_new = True
    
    # Применение шаблона
    templates = list(st.session_state.db["templates"].keys())
    if templates:
        chosen_tmpl = col_add2.selectbox("Из шаблона:", ["Выбери..."] + templates, label_visibility="collapsed")
        if chosen_tmpl != "Выбери...":
            if target_date not in st.session_state.db["days"]: st.session_state.db["days"][target_date] = []
            for ex_name in st.session_state.db["templates"][chosen_tmpl]:
                st.session_state.db["days"][target_date].append({"name": ex_name, "sets": []})
            save_data(st.session_state.db)
            st.rerun()

    if st.session_state.get("add_new"):
        with st.form("new_ex_form"):
            name = st.text_input("Название")
            if st.form_submit_button("Сохранить"):
                if target_date not in st.session_state.db["days"]: st.session_state.db["days"][target_date] = []
                st.session_state.db["days"][target_date].append({"name": name, "sets": []})
                save_data(st.session_state.db); st.session_state.add_new = False; st.rerun()

    # Список упражнений
    day_data = st.session_state.db["days"].get(target_date, [])
    for i, ex in enumerate(day_data):
        with st.container(border=True):
            st.write(f"**{ex['name'].upper()}**")
            sets = ex.get('sets', [])
            if sets: st.caption(" | ".join([f"{s['w']}×{s['r']}" for s in sets]))
            
            c1, c2 = st.columns([4, 1])
            with c1.expander("Добавить сет"):
                cw, cr, cb = st.columns([2, 2, 1])
                w = cw.number_input("Кг", 0.0, key=f"w_{target_date}_{i}", label_visibility="collapsed")
                r = cr.number_input("Р", 0, key=f"r_{target_date}_{i}", label_visibility="collapsed")
                if cb.button("➕", key=f"ok_{target_date}_{i}"):
                    ex['sets'].append({"w": str(w), "r": str(r)})
                    save_data(st.session_state.db); st.rerun()
            if c2.button("🗑️", key=f"del_{target_date}_{i}"):
                day_data.pop(i); save_data(st.session_state.db); st.rerun()

# ---------------------------------------------------------
# ВКЛАДКА 2: ШАБЛОНЫ
# ---------------------------------------------------------
with tab2:
    st.write("### 📋 Мои Шаблоны")
    new_t_name = st.text_input("Название шаблона (напр. 'Ноги')")
    if st.button("Создать шаблон"):
        if new_t_name:
            st.session_state.db["templates"][new_t_name] = []
            save_data(st.session_state.db); st.rerun()

    for t_name, t_exs in st.session_state.db["templates"].items():
        with st.expander(f"⚙️ {t_name}"):
            add_t_ex = st.text_input(f"Упр. для {t_name}", key=f"input_{t_name}")
            if st.button("➕ Добавить в список", key=f"btn_{t_name}"):
                t_exs.append(add_t_ex); save_data(st.session_state.db); st.rerun()
            st.write("Состав:", ", ".join(t_exs) if t_exs else "Пусто")
            if st.button("🗑️ Удалить шаблон", key=f"del_t_{t_name}"):
                del st.session_state.db["templates"][t_name]; save_data(st.session_state.db); st.rerun()

# ---------------------------------------------------------
# ВКЛАДКА 3: АНАЛИТИКА
# ---------------------------------------------------------
with tab3:
    st.write("### 📈 Прогресс")
    all_recs = []
    for d, exs in st.session_state.db["days"].items():
        for ex in exs:
            for s in ex.get('sets', []):
                all_recs.append({"Дата": d, "Упр": ex['name'], "Вес": float(s['w'])})
    
    if all_recs:
        df = pd.DataFrame(all_recs)
        df['Дата'] = pd.to_datetime(df['Дата'])
        u_exs = df['Упр'].unique()
        sel_ex = st.selectbox("Выбери упражнение для графика:", u_exs)
        chart_data = df[df['Упр'] == sel_ex].groupby('Дата')['Вес'].max()
        st.line_chart(chart_data)
    else:
        st.info("Добавь тренировки, чтобы увидеть графики")

    if st.button("🚨 Сбросить все данные"):
        st.session_state.db = {"days": {}, "templates": {}}
        save_data(st.session_state.db); st.rerun()
