import streamlit as st
import calendar
from datetime import date, datetime
import os
from dotenv import load_dotenv

from models import SessionLocal, Athlete, ContentItem, CalendarBatch
from sports_bank import BankSession, QuestionBankItem, seed_question_bank

load_dotenv()
seed_question_bank()  

st.set_page_config(page_title="StapuBox Admin Engine", layout="wide")

def load_css(file_name="style.css"):
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

st.sidebar.markdown("### ⚙️ Engine Controls")
selected_sports = st.sidebar.multiselect(
    "Active Sports", 
    ["Cricket", "Football", "Badminton"], 
    default=["Cricket", "Football", "Badminton"]
)
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

def get_db():
    return SessionLocal()

def get_bank_db():
    return BankSession()

def get_birthdays_for_month(month: int):
    db = get_db()
    athletes = db.query(Athlete).filter(Athlete.birth_month == month).all()
    db.close()
    return {a.birth_day: a for a in athletes}

def get_content_for_day(target_date: date):
    db = get_db()
    items = db.query(ContentItem).filter(ContentItem.scheduled_date == target_date).all()
    db.close()
    return items

def populate_schedule_from_bank(year, month, s_day, e_day):
    db = get_db()
    bank_db = get_bank_db()
    
    cricket_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.sport == "Cricket").all()
    football_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.sport == "Football").all()
    badminton_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.sport == "Badminton").all()
    poll_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.type == "POLL").all()
    fact_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.type == "FACT").all()
    
    batch_start = date(year, month, s_day)
    batch_end = date(year, month, e_day)
    
    batch = db.query(CalendarBatch).filter(
        CalendarBatch.start_date == batch_start,
        CalendarBatch.end_date == batch_end
    ).first()
    
    if not batch:
        batch = CalendarBatch(
            sport="All",
            start_date=batch_start,
            end_date=batch_end,
            status="DRAFT"
        )
        db.add(batch)
        db.flush()

    for d in range(s_day, e_day + 1):
        c_date = date(year, month, d)
        existing = db.query(ContentItem).filter(ContentItem.scheduled_date == c_date).count()
        if existing == 0:
            idx = (d - 1) % 50
            c_item = cricket_pool[idx % len(cricket_pool)]
            f_item = football_pool[idx % len(football_pool)]
            b_item = badminton_pool[idx % len(badminton_pool)]
            p_item = poll_pool[idx % len(poll_pool)]
            fa_item = fact_pool[idx % len(fact_pool)]
            
            new_items = [
                ContentItem(batch_id=batch.id, sport="Cricket", type="MCQ", category="Records", question=c_item.question, options=c_item.options, correct_answer=c_item.correct_answer, scheduled_date=c_date),
                ContentItem(batch_id=batch.id, sport="Football", type="MCQ", category="Trivia", question=f_item.question, options=f_item.options, correct_answer=f_item.correct_answer, scheduled_date=c_date),
                ContentItem(batch_id=batch.id, sport="Badminton", type="MCQ", category="Tournaments", question=b_item.question, options=b_item.options, correct_answer=b_item.correct_answer, scheduled_date=c_date),
                ContentItem(batch_id=batch.id, sport="General", type="POLL", category="Fan Vote", question=p_item.question, options=p_item.options, correct_answer=None, scheduled_date=c_date),
                ContentItem(batch_id=batch.id, sport="General", type="FACT", category="Did You Know?", question=fa_item.question, options=None, correct_answer=None, scheduled_date=c_date)
            ]
            db.add_all(new_items)
            
    db.commit()
    db.close()
    bank_db.close()

populate_schedule_from_bank(selected_year, selected_month, start, end)

db = get_db()
batch_items = db.query(ContentItem).filter(
    ContentItem.scheduled_date >= date(selected_year, selected_month, start),
    ContentItem.scheduled_date <= date(selected_year, selected_month, end)
).all()
is_all_scheduled = all(item.status == "SCHEDULED" for item in batch_items) if batch_items else False
db.close()

st.markdown("<h2 style='margin-bottom: 2px; color: #0F172A;'>StapuBox — Content & Calendar Scheduling</h2>", unsafe_allow_html=True)
status_color = "#15803D" if is_all_scheduled else "#D97706"
status_text = "🔒 Scheduled (10:00 AM Daily)" if is_all_scheduled else "📝 Draft Mode (Pending Approval)"
st.markdown(
    f"<p style='color: #64748B; font-size: 0.88rem; margin-bottom: 12px;'>"
    f"Sports: <b>{', '.join(selected_sports)}</b> | Active Batch: <b>Day {start} to Day {end}</b> | "
    f"<span style='color:{status_color}; font-weight:600;'>{status_text}</span> | ",
    unsafe_allow_html=True
)

birthday_dict = get_birthdays_for_month(selected_month)

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
            has_bday = day in birthday_dict
            box_cls = "day-box active-batch" if is_active else "day-box"
            
            badge_html = ""
            if has_bday:
                badge_html += f"<div class='badge-bday'>🎂 {birthday_dict[day].name.split()[0]}</div>"
            elif is_active:
                badge_html += "<div class='badge-red'>Active</div>"
                
            cols[idx].markdown(f"""
                <div class="{box_cls}">
                    <span class="day-number">{day}</span>
                    {badge_html}
                </div>
            """, unsafe_allow_html=True)

st.write("")
col_ap1, col_ap2 = st.columns([1, 1])
with col_ap2:
    if st.button("✅ Approve Whole Week (Lock 10:00 AM Daily)", use_container_width=True):
        db = get_db()
        items_to_lock = db.query(ContentItem).filter(
            ContentItem.scheduled_date >= date(selected_year, selected_month, start),
            ContentItem.scheduled_date <= date(selected_year, selected_month, end)
        ).all()
        for it in items_to_lock:
            it.status = "SCHEDULED"
        db.commit()
        db.close()
        st.success("Whole week successfully locked and scheduled for 10:00 AM daily!")
        st.rerun()

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
day_cols = st.columns(7)
for idx, d in enumerate(range(start, end + 1)):
    with day_cols[idx]:
        is_sel = (st.session_state.selected_day == d)
        bday_icon = "🎂 " if d in birthday_dict else ""
        lbl = f"● {bday_icon}Day {d}" if is_sel else f"{bday_icon}Day {d}"
        if st.button(lbl, key=f"sel_d_{d}", use_container_width=True):
            st.session_state.selected_day = d
            st.rerun()

current_day = st.session_state.selected_day
if current_day < start or current_day > end:
    current_day = start

if current_day in birthday_dict:
    ath = birthday_dict[current_day]
    age = selected_year - ath.birth_year
    st.markdown(f"""
    <div class="birthday-card">
        <div style="font-size: 1.05rem; font-weight: 700; color: #9A3412;">🎉 Celebrity Birthday: {ath.name} ({ath.sport})</div>
        <div style="font-size: 0.82rem; color: #C2410C; margin-top: 2px;">
            Turns <b>{age} years old</b> on this date ({calendar.month_name[selected_month]} {current_day}, {selected_year}).
        </div>
        <div style="font-size: 0.82rem; color: #7C2D12; margin-top: 4px;">
            <b>Notable Records:</b> {ath.notable_records}<br>
            <b>Trivia:</b> {ath.trivia_fact}
        </div>
    </div>
    """, unsafe_allow_html=True)

cur_date = date(selected_year, selected_month, current_day)
day_items = get_content_for_day(cur_date)

st.markdown(f"<p style='font-size:0.85rem; color:#475569; margin: 8px 0 4px 0;'>Showing questions for: <b>Day {current_day} ({calendar.month_name[selected_month]} {current_day}, {selected_year})</b></p>", unsafe_allow_html=True)

for q_idx, item in enumerate(day_items):

    if item.type == "MCQ" and item.sport in selected_sports:
        st.markdown(f"""
        <div class="question-card">
            <div class="q-title"><span style="color:#0284C7; font-size:0.75rem;">[{item.sport.upper()} MCQ]</span> {item.question}</div>
        </div>
        """, unsafe_allow_html=True)
        
        ans_key = f"ans_{current_day}_{item.id}"
        if ans_key not in st.session_state:
            st.session_state[ans_key] = None
            
        selected_opt = st.session_state[ans_key]
        opt_cols = st.columns(len(item.options))
        
        st.markdown("<div class='mcq-btn-wrapper'>", unsafe_allow_html=True)
        for o_idx, opt in enumerate(item.options):
            if selected_opt is None:
                btn_cls = "default-opt"
                label = opt
            elif opt == item.correct_answer:
                btn_cls = "correct-opt"
                label = f"✓ {opt}"
            elif opt == selected_opt and selected_opt != item.correct_answer:
                btn_cls = "wrong-opt"
                label = f"✗ {opt}"
            else:
                btn_cls = "default-opt"
                label = opt
                
            with opt_cols[o_idx]:
                st.markdown(f"<div class='{btn_cls}'>", unsafe_allow_html=True)
                if st.button(label, key=f"b_{current_day}_{item.id}_{o_idx}", disabled=(selected_opt is not None)):
                    st.session_state[ans_key] = opt
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        if selected_opt is not None:
            if st.button("↺ Reset Question", key=f"rst_{current_day}_{item.id}"):
                st.session_state[ans_key] = None
                st.rerun()

    elif item.type == "POLL":
        poll_key = f"poll_{current_day}_{item.id}"
        if poll_key not in st.session_state.poll_state:
            st.session_state.poll_state[poll_key] = {
                "selected": None,
                "counts": {opt: 1 for opt in item.options}
            }
        
        current_poll = st.session_state.poll_state[poll_key]
        total_votes = sum(current_poll["counts"].values())
        
        st.markdown(f"""
        <div class="wa-poll-card">
            <div class="wa-poll-title">📊 {item.question}</div>
            <div class="wa-poll-subtitle">Select one option • {total_votes} total votes</div>
        </div>
        """, unsafe_allow_html=True)
        
        for opt in item.options:
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

    elif item.type == "FACT":
        st.markdown(f"""
        <div class="fact-card">
            <div style="font-size:0.75rem; font-weight:700; color:#0369A1; margin-bottom:2px;">💡 DID YOU KNOW? (DAILY SPORTS FACT)</div>
            <div style="font-size:0.86rem; color:#0C4A6E; font-weight:500;">{item.question}</div>
        </div>
        """, unsafe_allow_html=True)