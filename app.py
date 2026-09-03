import streamlit as st
import calendar
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="StapuBox Admin Engine", layout="wide")

def load_css(file_name: str):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

if "batch_start_day" not in st.session_state:
    st.session_state.batch_start_day = 1
if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1
if "poll_state" not in st.session_state:
    st.session_state.poll_state = {}

start = st.session_state.batch_start_day
end = start + 6

st.sidebar.markdown("### ⚙️ Select Details")
selected_sport = st.sidebar.selectbox("Sport", ["Cricket", "Football", "Tennis", "Basketball"])
selected_month = st.sidebar.selectbox("Month", list(range(1, 13)), index=8) 
selected_year = st.sidebar.number_input("Year", min_value=2024, max_value=2030, value=2026)

st.sidebar.markdown("---")
st.sidebar.markdown("**Cycle Info:**")
st.sidebar.markdown(f"- Active Week: `Day {start} → Day {end}`")
st.sidebar.markdown("- Schedule: `10:00 AM Daily`")

if st.sidebar.button("⏩ Advance Next 7 Days", use_container_width=True):
    st.session_state.batch_start_day += 7
    st.session_state.selected_day = st.session_state.batch_start_day
    st.rerun()

WEEK_DATA = {
    str(start): [
        {"type": "MCQ", "q": "Who holds the record for highest individual ODI score (264)?", "opts": ["Rohit Sharma", "Martin Guptill", "Chris Gayle", "Virender Sehwag"], "ans": "Rohit Sharma"},
        {"type": "POLL", "q": "Who will win the ICC Champions Trophy?", "opts": ["India", "Australia", "England"]}
    ],
    str(start + 1): [
        {"type": "MCQ", "q": "Which player has won the most Ballon d'Or awards?", "opts": ["Cristiano Ronaldo", "Lionel Messi", "Johan Cruyff", "Michel Platini"], "ans": "Lionel Messi"},
        {"type": "POLL", "q": "Will Real Madrid win UCL this season?", "opts": ["Yes", "No"]}
    ],
    str(start + 2): [
        {"type": "MCQ", "q": "How many Grand Slam singles titles has Novak Djokovic won?", "opts": ["20", "22", "24", "26"], "ans": "24"},
        {"type": "POLL", "q": "Best tennis surface?", "opts": ["Grass", "Clay", "Hard Court"]}
    ],
    str(start + 3): [
        {"type": "MCQ", "q": "Which team has won 5 IPL trophies?", "opts": ["CSK & MI", "KKR & SRH", "RCB & DC", "RR & GT"], "ans": "CSK & MI"},
        {"type": "POLL", "q": "Is T20 overshadowing Test cricket?", "opts": ["Yes", "No"]}
    ],
    str(start + 4): [
        {"type": "MCQ", "q": "Who is the NBA all-time top scorer?", "opts": ["Michael Jordan", "Kareem Abdul-Jabbar", "LeBron James", "Kobe Bryant"], "ans": "LeBron James"},
        {"type": "POLL", "q": "Fastest growing sport globally?", "opts": ["Formula 1", "Basketball", "Cricket"]}
    ],
    str(start + 5): [
        {"type": "MCQ", "q": "Who won the inaugural 2007 T20 World Cup?", "opts": ["Pakistan", "India", "Australia", "West Indies"], "ans": "India"},
        {"type": "POLL", "q": "DRS for wide balls?", "opts": ["Support", "Oppose"]}
    ],
    str(start + 6): [
        {"type": "MCQ", "q": "Most wickets in Test cricket history?", "opts": ["Shane Warne", "Muttiah Muralitharan", "James Anderson", "Anil Kumble"], "ans": "Muttiah Muralitharan"},
        {"type": "POLL", "q": "Current best fast bowler?", "opts": ["Jasprit Bumrah", "Pat Cummins", "Kagiso Rabada"]}
    ]
}


st.markdown("<h2 style='margin-bottom: 2px; color: #0F172A;'>StapuBox — Content & Calendar Scheduling Engine</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #64748B; font-size: 0.88rem; margin-bottom: 12px;'>Sport: <b>{selected_sport}</b> | Active Batch: <b>Day {start} to Day {end}</b> | <span style='color:#15803D; font-weight:600;'>🔒 Scheduled 10:00 AM Daily</span></p>", unsafe_allow_html=True)

cal = calendar.Calendar(firstweekday=0)
month_days = cal.monthdayscalendar(selected_year, selected_month)

cols = st.columns(7)
for idx, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
    cols[idx].markdown(f"<div class='cal-header'>{name}</div>", unsafe_allow_html=True)

for week in month_days:
    cols = st.columns(7)
    for idx, day in enumerate(week):
        if day == 0:
            cols[idx].markdown("<div class='day-box empty'></div>", unsafe_allow_html=True)
        else:
            is_active = start <= day <= end
            box_cls = "day-box active-batch" if is_active else "day-box"
            badge = "<div class='badge-red'>Active</div>" if is_active else ""
            cols[idx].markdown(f"""
                <div class="{box_cls}">
                    <span class="day-number">{day}</span>
                    {badge}
                </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
day_cols = st.columns(7)
for idx, d in enumerate(range(start, end + 1)):
    with day_cols[idx]:
        is_sel = (st.session_state.selected_day == d)
        lbl = f"● Day {d}" if is_sel else f"Day {d}"
        if st.button(lbl, key=f"sel_d_{d}", use_container_width=True):
            st.session_state.selected_day = d
            st.rerun()

current_day = st.session_state.selected_day
if current_day < start or current_day > end:
    current_day = start

items = WEEK_DATA.get(str(current_day), [])

st.markdown(f"<p style='font-size:0.85rem; color:#475569; margin: 8px 0 4px 0;'>Showing questions for: <b>Day {current_day} (September {current_day}, {selected_year})</b></p>", unsafe_allow_html=True)

for q_idx, item in enumerate(items):
    if item["type"] == "MCQ":
        st.markdown(f"""
        <div class="question-card">
            <div class="q-title"><span style="color:#64748B; font-size:0.75rem;">[MCQ]</span> {item['q']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ans_key = f"ans_{current_day}_{q_idx}"
        if ans_key not in st.session_state:
            st.session_state[ans_key] = None
            
        selected_opt = st.session_state[ans_key]
        opt_cols = st.columns(len(item["opts"]))
        
        st.markdown("<div class='mcq-btn-wrapper'>", unsafe_allow_html=True)
        for o_idx, opt in enumerate(item["opts"]):
            if selected_opt is None:
                btn_cls = "default-opt"
                label = opt
            elif opt == item["ans"]:
                btn_cls = "correct-opt"
                label = f"✓ {opt}"
            elif opt == selected_opt and selected_opt != item["ans"]:
                btn_cls = "wrong-opt"
                label = f"✗ {opt}"
            else:
                btn_cls = "default-opt"
                label = opt
                
            with opt_cols[o_idx]:
                st.markdown(f"<div class='{btn_cls}'>", unsafe_allow_html=True)
                if st.button(label, key=f"b_{current_day}_{q_idx}_{o_idx}", disabled=(selected_opt is not None)):
                    st.session_state[ans_key] = opt
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if selected_opt is not None:
            if st.button("↺ Reset Question", key=f"rst_{current_day}_{q_idx}"):
                st.session_state[ans_key] = None
                st.rerun()

    elif item["type"] == "POLL":
        poll_key = f"poll_{current_day}_{q_idx}"
        if poll_key not in st.session_state.poll_state:
            st.session_state.poll_state[poll_key] = {
                "selected": None,
                "counts": {opt: 1 for opt in item["opts"]}
            }
        
        current_poll = st.session_state.poll_state[poll_key]
        total_votes = sum(current_poll["counts"].values())
        
        st.markdown(f"""
        <div class="wa-poll-card">
            <div class="wa-poll-title">📊 {item['q']}</div>
            <div class="wa-poll-subtitle">Select one option • {total_votes} total votes</div>
        </div>
        """, unsafe_allow_html=True)
        
        for opt in item["opts"]:
            count = current_poll["counts"][opt]
            pct = int((count / total_votes) * 100) if total_votes > 0 else 0
            is_user_choice = (current_poll["selected"] == opt)
            
            fill_class = "wa-bar-fill voted" if is_user_choice else "wa-bar-fill"
            check_icon = "✓ " if is_user_choice else ""
            
            p_col1, p_col2 = st.columns([5, 1])
            with p_col1:
                st.markdown(f"""
                <div class="wa-bar-bg">
                    <div class="{fill_class}" style="width: {pct}%;"></div>
                    <div class="wa-bar-content">
                        <span><b>{check_icon}</b>{opt}</span>
                        <span style="font-size:0.75rem; color:#475569;"><b>{pct}%</b> ({count})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with p_col2:
                st.markdown("<div class='wa-vote-btn'>", unsafe_allow_html=True)
                btn_txt = "Remove" if is_user_choice else "Vote"
                if st.button(btn_txt, key=f"wa_{poll_key}_{opt}", use_container_width=True):
                    if is_user_choice:
                        current_poll["counts"][opt] -= 1
                        current_poll["selected"] = None
                    else:
                        if current_poll["selected"] is not None:
                            current_poll["counts"][current_poll["selected"]] -= 1
                        current_poll["counts"][opt] += 1
                        current_poll["selected"] = opt
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)