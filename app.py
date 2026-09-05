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

if "last_viewed_month" not in st.session_state:
    st.session_state.last_viewed_month = 9 
if "batch_start_day" not in st.session_state:
    st.session_state.batch_start_day = 1
if "selected_day" not in st.session_state:
    st.session_state.selected_day = 1
if "poll_state" not in st.session_state:
    st.session_state.poll_state = {}

st.sidebar.markdown("### ⚙️ Engine Controls")
selected_sports = st.sidebar.multiselect(
    "Active Sports", 
    ["Cricket", "Football", "Badminton"], 
    default=["Cricket", "Football", "Badminton"]
)

selected_month = st.sidebar.selectbox(
    "Month", 
    list(range(1, 13)), 
    index=st.session_state.last_viewed_month - 1
)
selected_year = st.sidebar.number_input("Year", min_value=2024, max_value=2030, value=2026)

if selected_month != st.session_state.last_viewed_month:
    st.session_state.last_viewed_month = selected_month
    st.session_state.batch_start_day = 1
    st.session_state.selected_day = 1
    st.rerun()

_, max_days = calendar.monthrange(selected_year, selected_month)

if st.session_state.batch_start_day > max_days:
    st.session_state.batch_start_day = 1

start = st.session_state.batch_start_day
end = min(start + 6, max_days)

st.sidebar.markdown("---")
st.sidebar.markdown("**Cycle Info:**")
st.sidebar.markdown(f"- Active Week: `Day {start} → Day {end}`")
st.sidebar.markdown("- Schedule: `10:00 AM Daily`")

if st.sidebar.button("⏩ Advance Next 7 Days", use_container_width=True):
    next_start = st.session_state.batch_start_day + 7
    if next_start > max_days:
        st.session_state.batch_start_day = 1
        st.session_state.selected_day = 1
    else:
        st.session_state.batch_start_day = next_start
        st.session_state.selected_day = next_start
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
    
    _, max_month_days = calendar.monthrange(year, month)
    s_day = min(s_day, max_month_days)
    e_day = min(e_day, max_month_days)
    
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

    cricket_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.sport == "Cricket").all()
    football_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.sport == "Football").all()
    badminton_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.sport == "Badminton").all()
    poll_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.type == "POLL").all()
    fact_pool = bank_db.query(QuestionBankItem).filter(QuestionBankItem.type == "FACT").all()

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

st.markdown("<h2 style='margin-bottom: 2px; color: #0F172A;'>StapuBox — Content & Calendar Scheduling Engine</h2>", unsafe_allow_html=True)
status_color = "#15803D" if is_all_scheduled else "#D97706"
status_text = "🔒 Scheduled (10:00 AM Daily)" if is_all_scheduled else "📝 Draft Mode (Pending Approval)"
st.markdown(
    f"<p style='color: #64748B; font-size: 0.88rem; margin-bottom: 8px;'>"
    f"Sports: <b>{', '.join(selected_sports)}</b> | Active Batch: <b>Day {start} to Day {end}</b> | "
    f"<span style='color:{status_color}; font-weight:600;'>{status_text}</span> | "
    f"<span style='color:#0284C7;'>Bank: <b>50 Items Loaded / Sport</b></span></p>", 
    unsafe_allow_html=True
)

month_name = calendar.month_name[selected_month]
st.markdown(f"<div class='cal-month-title'>📅 {month_name} {selected_year}</div>", unsafe_allow_html=True)

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
            
            if has_bday:
                box_cls = "day-box birthday-day"
                badge_html = f"<div class='badge-bday'><span class='cake-icon'>🎂</span> {birthday_dict[day].name.split()[0]}</div>"
            elif is_active:
                box_cls = "day-box active-batch"
                badge_html = "<div class='badge-green'>Active</div>"
            else:
                box_cls = "day-box"
                badge_html = ""
                
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
day_cols = st.columns(len(range(start, end + 1)))
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

FB_EMOJIS = ["👍", "❤️", "🔥", "👏", "😮"]

for q_idx, item in enumerate(day_items):

    if item.type == "MCQ" and item.sport in selected_sports:
        st.markdown(f"""
        <div class="question-card">
            <div class="q-title"><span style="color:#0284C7; font-size:0.75rem;">[{item.sport.upper()}]</span> {item.question}</div>
        </div>
        """, unsafe_allow_html=True)
        
        inp_col, btn_col = st.columns([4, 1])
        user_input_key = f"input_{current_day}_{item.id}"
        verified_key = f"verif_{current_day}_{item.id}"
        
        with inp_col:
            user_val = st.text_input(
                "Your Answer:", 
                key=user_input_key, 
                placeholder="Type your answer here...", 
                label_visibility="collapsed"
            )
            
        with btn_col:
            check_clicked = st.button("Submit", key=f"btn_check_{current_day}_{item.id}", use_container_width=True)
            
        if check_clicked and user_val.strip():
            st.session_state[verified_key] = user_val.strip()
            
        if verified_key in st.session_state:
            typed = st.session_state[verified_key].strip().lower()
            actual = str(item.correct_answer).strip().lower()
            
            if typed == actual or typed in actual or actual in typed:
                st.markdown("<div class='feedback-right'>🎉 You are right!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='feedback-wrong'>❌ You are wrong! Correct answer: <b>{item.correct_answer}</b></div>", unsafe_allow_html=True)
                
            if st.button("↺ Try Again", key=f"rst_{current_day}_{item.id}"):
                del st.session_state[verified_key]
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
        
        with st.container():
            st.markdown("<div class='fb-poll-marker'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="fb-poll-header">📊 {item.question}</div>
            <div class="fb-poll-sub">Facebook Community Poll • {total_votes} votes</div>
            """, unsafe_allow_html=True)
            
            for idx, opt in enumerate(item.options):
                emoji = FB_EMOJIS[idx % len(FB_EMOJIS)]
                count = current_poll["counts"][opt]
                pct = int((count / total_votes) * 100) if total_votes > 0 else 0
                is_user_choice = (current_poll["selected"] == opt)
                
                fill_class = "fb-bar-fill voted" if is_user_choice else "fb-bar-fill"
                check_mark = "✓ " if is_user_choice else ""
                
                p_col1, p_col2 = st.columns([3.6, 1.4])
                with p_col1:
                    st.markdown(f"""
                    <div class="fb-bar-container">
                        <div class="{fill_class}" style="width: {pct}%;"></div>
                        <div class="fb-bar-content">
                            <span><span style="font-size:0.95rem; margin-right:4px;">{emoji}</span><b>{check_mark}</b>{opt}</span>
                            <span style="font-size:0.68rem; color:#475569;"><b>{pct}%</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with p_col2:
                    btn_txt = "Undo" if is_user_choice else f"Vote {emoji}"
                    if st.button(btn_txt, key=f"fb_{poll_key}_{opt}", use_container_width=True):
                        if is_user_choice:
                            current_poll["counts"][opt] -= 1
                            current_poll["selected"] = None
                        else:
                            if current_poll["selected"] is not None:
                                current_poll["counts"][current_poll["selected"]] -= 1
                            current_poll["counts"][opt] += 1
                            current_poll["selected"] = opt
                        st.rerun()

    elif item.type == "FACT":
        st.markdown(f"""
        <div class="fact-card">
            <div style="font-size:0.75rem; font-weight:700; color:#0369A1; margin-bottom:2px;">💡 DID YOU KNOW? (DAILY SPORTS FACT)</div>
            <div style="font-size:0.86rem; color:#0C4A6E; font-weight:500;">{item.question}</div>
        </div>
        """, unsafe_allow_html=True)