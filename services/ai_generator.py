import os
import json
from datetime import date , timedelta
from dotenv import load_dotenv
from groq import Groq
from schemas import GeneratedItem, WeekendBatchGeneration
from models import ContentItem, CalenderBatch
from database import SessionLocal
from services.deduplicator import is_duplicate

load_dotenv()

client = Groq(api_key= os.getenv("GROQ_API_KEY"))

def generate_week_content(
    year: int,
    month: int,
    start_day: int,
    end_day: int,
    sport: str = "Cricket"
) -> CalenderBatch:

    db = SessionLocal()

    try:
        date_list = [date(year,month,d).isoformat() for d in range(start_day , end_day+1 )]

        prompt = f"""
        You are the sports content generation engine for StapuBox.
        Sport: {sport}
        Target Dates: {date_list}

        Generate sports content for each of the dates listed:
        For EACH single date, provide exactly:
        - 1 Multiple Choice Questions (MCQ) with 4 options and 1 correct_answer.
        - 1 Fan/Opinion Polls (POLL) with 2 or 3 options and correct_answer set to null.

        Output must strictly be valid JSON matching this schema:
        {{
          "days": [
            {{
              "date_str": "YYYY-MM-DD",
              "day_number": <int>,
              "items": [
                {{
                  "type": "MCQ" or "POLL",
                  "sport": "{sport}",
                  "category": "Trivia or Recent or Records",
                  "question": "question text",
                  "options": ["Option A", "Option B", "Option C", "Option D"],
                  "correct_answer": "Option A" (or null if POLL)
                }}
              ]
            }}
          ]
        }}
        """

        response = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages = [
                {"role":"system","content":"You are a professional sports trivia and poll creator. Return JSON only."},
                {"role":"user","content":prompt}
            ],

            response_format= {"type":"json_object"},
            temperature= 0.7,
        )

        raw_json = json.loads(response.choices[0].message.content)
        validated_batch = WeekendBatchGeneration(**raw_json)

        batch_record = CalenderBatch(
            year = year,
            month = month,
            start_day = start_day,
            end_day = end_day,
            status = "Draft"
        )

        db.add(batch_record)
        db.flush()

        for day in validated_batch.days:
            scheduled_date = datetime.fromisoformat(day.date_str)
            for item in day.items:
                if is_duplicate_question(item.question, db):
                    continue 
                content_item = ContentItem(
                    batch_id=batch_record.id,
                    sport=item.sport,
                    category=item.category,
                    type=item.type,
                    question=item.question,
                    options=item.options,
                    correct_answer=item.correct_answer,
                    scheduled_date=scheduled_date,
                    status="DRAFT"
                )
                db.add(content_item)

        db.commit()
        db.refresh(batch_record)
        return batch_record
    finally:
        db.close()

