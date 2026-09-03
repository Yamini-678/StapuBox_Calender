import re
from difflib import SequenceMatcher
from sqlalchemy import Session
from models import ContentItem

def normalize_text(text : str) -> str:
    text = text.lower().strip()
    return re.sub(r"[^\w\s]", "", text)


def is_duplicate(new_question:str, db:Session, similarity_threshold:float=0.82) -> bool:
    norm_new = normalize_text(new_question)
    
    existing_items = db.query(ContentItem.question).all()

    for(item_q,) in existing_items:
        norm_existing = normalize_text(item_q)
        
        if norm_new == norm_existing:
            return True

        similarity = SequenceMatcher(None, norm_new, norm_existing).ratio()
        if similarity >= similarity_threshold:
            return True

    return False
    