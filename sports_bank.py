import uuid
import random
from sqlalchemy import Column, String, Integer, Text, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BANK_DATABASE_URL = "sqlite:///./sports_bank.db"
bank_engine = create_engine(BANK_DATABASE_URL, connect_args={"check_same_thread": False})
BankSession = sessionmaker(autocommit=False, autoflush=False, bind=bank_engine)
BankBase = declarative_base()

class QuestionBankItem(BankBase):
    __tablename__ = "question_bank"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sport = Column(String(50), nullable=False)        
    type = Column(String(10), nullable=False) 
    category = Column(String(50), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=True)
    correct_answer = Column(String(255), nullable=True)

BankBase.metadata.create_all(bind=bank_engine)

CRICKET_RAW = [
    ("Who scored the highest individual score in ODI cricket (264)?", ["Rohit Sharma", "Martin Guptill", "Chris Gayle", "Virender Sehwag"], "Rohit Sharma"),
    ("Who is the only player to score 100 international centuries?", ["Sachin Tendulkar", "Virat Kohli", "Ricky Ponting", "Jacques Kallis"], "Sachin Tendulkar"),
    ("Who holds the record for the highest individual score in Test cricket (400*)?", ["Brian Lara", "Matthew Hayden", "Don Bradman", "Virender Sehwag"], "Brian Lara"),
    ("Who was the winning captain of the inaugural 2007 T20 World Cup?", ["MS Dhoni", "Shoaib Malik", "Graeme Smith", "Ricky Ponting"], "MS Dhoni"),
    ("Who bowled the 'Ball of the Century' to Mike Gatting in 1993?", ["Shane Warne", "Glenn McGrath", "Wasim Akram", "Allan Donald"], "Shane Warne"),
    ("Who has taken the most wickets in international cricket history (1347)?", ["Muttiah Muralitharan", "Shane Warne", "James Anderson", "Anil Kumble"], "Muttiah Muralitharan"),
    ("Which team won the first-ever Cricket World Cup in 1975?", ["West Indies", "Australia", "England", "India"], "West Indies"),
    ("Who scored the fastest century in ODI history (31 balls)?", ["AB de Villiers", "Corey Anderson", "Shahid Afridi", "Glenn Maxwell"], "AB de Villiers"),
    ("Which Indian bowler took 10 wickets in a single Test innings against Pakistan in 1999?", ["Anil Kumble", "Kapil Dev", "Harbhajan Singh", "Zaheer Khan"], "Anil Kumble"),
    ("What is the maximum number of overs a bowler can bowl in an ODI?", ["10", "12", "8", "15"], "10"),
    ("Which cricket ground is popularly called the 'Home of Cricket'?", ["Lord's", "MCG", "Eden Gardens", "The Oval"], "Lord's"),
    ("Who holds the record for the most sixes in international cricket?", ["Rohit Sharma", "Chris Gayle", "Shahid Afridi", "Brendon McCullum"], "Rohit Sharma"),
    ("Who was the captain when India won the 1983 World Cup?", ["Kapil Dev", "Sunil Gavaskar", "Mohinder Amarnath", "Ravi Shastri"], "Kapil Dev"),
    ("Who is the fastest bowler to reach 100 ODI wickets?", ["Sandeep Lamichhane", "Rashid Khan", "Mitchell Starc", "Saqlain Mushtaq"], "Sandeep Lamichhane"),
    ("Which country won the inaugural ICC World Test Championship (2019-2021)?", ["New Zealand", "India", "Australia", "England"], "New Zealand"),
    ("Who hit 6 sixes in an over off Stuart Broad in the 2007 T20 World Cup?", ["Yuvraj Singh", "Kieron Pollard", "Herschelle Gibbs", "Chris Gayle"], "Yuvraj Singh"),
    ("Who is known as the 'God of Offside' in Indian cricket?", ["Sourav Ganguly", "VVS Laxman", "Rahul Dravid", "Sunil Gavaskar"], "Sourav Ganguly"),
    ("What was Don Bradman's final career Test batting average?", ["99.94", "100.00", "95.50", "98.20"], "99.94"),
    ("Who holds the record for the best bowling figures in an ODI (8/19)?", ["Chaminda Vaas", "Muttiah Muralitharan", "Glenn McGrath", "Anil Kumble"], "Chaminda Vaas"),
    ("Which country invented the game of cricket?", ["England", "Australia", "India", "South Africa"], "England"),
    ("Who won the IPL 2024 title?", ["Kolkata Knight Riders", "Sunrisers Hyderabad", "Rajasthan Royals", "Royal Challengers Bengaluru"], "Kolkata Knight Riders"),
    ("Which batsman has the highest batting strike rate in T20I history (min 500 balls)?", ["Suryakumar Yadav", "Andre Russell", "Glenn Maxwell", "Heinrich Klaasen"], "Suryakumar Yadav"),
    ("Who has the most runs in an individual IPL season (973 runs)?", ["Virat Kohli", "Jos Buttler", "David Warner", "Shubman Gill"], "Virat Kohli"),
    ("Which bowler holds the record for the most wickets in a single ODI World Cup edition (27)?", ["Mitchell Starc", "Glenn McGrath", "Mohammed Shami", "Muttiah Muralitharan"], "Mitchell Starc"),
    ("Who holds the record for the highest individual score in T20 international cricket (172)?", ["Aaron Finch", "Chris Gayle", "Hazratullah Zazai", "Glenn Maxwell"], "Aaron Finch"),

]

FOOTBALL_RAW = [
    ("Which country has won the most FIFA World Cup titles (5)?", ["Brazil", "Germany", "Italy", "Argentina"], "Brazil"),
    ("Who has won the most Ballon d'Or awards in history?", ["Lionel Messi", "Cristiano Ronaldo", "Johan Cruyff", "Michel Platini"], "Lionel Messi"),
    ("Which club has won the most UEFA Champions League titles (15)?", ["Real Madrid", "AC Milan", "Bayern Munich", "Liverpool"], "Real Madrid"),
    ("Who is the all-time top goalscorer in men's international football?", ["Cristiano Ronaldo", "Ali Daei", "Lionel Messi", "Pelé"], "Cristiano Ronaldo"),
    ("Which country hosted and won the first-ever FIFA World Cup in 1930?", ["Uruguay", "Argentina", "Brazil", "Italy"], "Uruguay"),
    ("Who scored the famous 'Hand of God' goal in the 1986 World Cup?", ["Diego Maradona", "Pelé", "Zico", "Gary Lineker"], "Diego Maradona"),
    ("Who is the youngest player to score in a FIFA World Cup final?", ["Pelé", "Kylian Mbappé", "Lionel Messi", "Garrincha"], "Pelé"),
    ("Which nation won the 2022 FIFA World Cup in Qatar?", ["Argentina", "France", "Croatia", "Morocco"], "Argentina"),
    ("Who holds the record for the most goals in a single calendar year (91)?", ["Lionel Messi", "Gerd Müller", "Cristiano Ronaldo", "Robert Lewandowski"], "Lionel Messi"),
    ("What is the duration of a standard regulation football match?", ["90 minutes", "80 minutes", "100 minutes", "120 minutes"], "90 minutes"),
    ("Which player scored a hat-trick in the 2022 FIFA World Cup final?", ["Kylian Mbappé", "Lionel Messi", "Ángel Di María", "Olivier Giroud"], "Kylian Mbappé"),
    ("Which club went entire 2003-04 Premier League season undefeated ('The Invincibles')?", ["Arsenal", "Manchester United", "Chelsea", "Liverpool"], "Arsenal"),
    ("Who is known as 'El Fenomeno'?", ["Ronaldo Nazário", "Cristiano Ronaldo", "Ronaldinho", "Romário"], "Ronaldo Nazário"),
    ("Which country won UEFA Euro 2024?", ["Spain", "England", "France", "Germany"], "Spain"),
    ("What is the diameter of a standard FIFA regulation football goal width?", ["7.32 meters (8 yards)", "6.5 meters", "8.0 meters", "7.0 meters"], "7.32 meters (8 yards)"),
    ("Which goalkeeper has the most clean sheets in Premier League history?", ["Petr Čech", "David de Gea", "Peter Schmeichel", "Edwin van der Sar"], "Petr Čech"),
    ("Which team has won the most Copa América titles?", ["Argentina", "Uruguay", "Brazil", "Chile"], "Argentina"),
    ("Who is the all-time top goalscorer in the UEFA Champions League?", ["Cristiano Ronaldo", "Lionel Messi", "Robert Lewandowski", "Karim Benzema"], "Cristiano Ronaldo"),
    ("What color card did referee introduce along with red card in 1970 World Cup?", ["Yellow", "Blue", "Green", "White"], "Yellow"),

]

BADMINTON_RAW = [
    ("Who is the first Indian badminton player to win an Olympic medal?", ["Saina Nehwal", "PV Sindhu", "Prakash Padukone", "Pullela Gopichand"], "Saina Nehwal"),
    ("How many feathers are used to make an official feather shuttlecock?", ["16", "14", "18", "12"], "16"),
    ("Who is the only male player to win back-to-back Olympic singles gold (2008 & 2012)?", ["Lin Dan", "Lee Chong Wei", "Chen Long", "Viktor Axelsen"], "Lin Dan"),
    ("Which country has won the Thomas Cup the most times (14 titles)?", ["Indonesia", "China", "Malaysia", "Denmark"], "Indonesia"),
    ("In which city were the modern rules of badminton developed during the 19th century?", ["Pune, India", "London, UK", "Copenhagen, Denmark", "Kuala Lumpur, Malaysia"], "Pune, India"),
    ("How many points must a player score to win a standard BWF game?", ["21", "15", "25", "11"], "21"),
    ("Who won the Men's Singles gold at Tokyo 2020 and Paris 2024 Olympics?", ["Viktor Axelsen", "Kento Momota", "Shi Yuqi", "Lee Zii Jia"], "Viktor Axelsen"),
    ("In which year did PV Sindhu win her historic World Championship Gold medal?", ["2019", "2017", "2016", "2021"], "2019"),
    ("What is the top recorded speed of a badminton smash in official competition?", ["Over 490 km/h", "320 km/h", "250 km/h", "400 km/h"], "Over 490 km/h"),
    ("Which governing body manages international badminton?", ["BWF", "ITF", "FIFA", "ICC"], "BWF"),
    ("Who was the first Indian to win the All England Open Badminton Championships (1980)?", ["Prakash Padukone", "Pullela Gopichand", "Syed Modi", "Chetan Anand"], "Prakash Padukone"),
    ("What is the women's world team championship trophy called in badminton?", ["Uber Cup", "Thomas Cup", "Sudirman Cup", "Suez Cup"], "Uber Cup"),
    ("What is the height of a standard badminton net at the center of the court?", ["1.524 meters (5 feet)", "1.65 meters", "1.40 meters", "1.80 meters"], "1.524 meters (5 feet)"),
    ("Which feather shuttlecock part hits the racket first?", ["Cork base", "Feather tip", "Ribbon seam", "Crown ring"], "Cork base"),
    ("Who won the Men's Singles Gold at the 2024 Paris Olympics?", ["Viktor Axelsen", "Kunlavut Vitidsarn", "Lakshya Sen", "Lee Zii Jia"], "Viktor Axelsen"),
    ("What is the maximum weight allowed for a tournament-grade badminton racket?", ["Between 80 and 100 grams", "150 grams", "200 grams", "50 grams"], "Between 80 and 100 grams"),
    ("What year did badminton make its official debut as a full medal sport at the Olympics?", ["1992 (Barcelona)", "1988 (Seoul)", "1996 (Atlanta)", "2000 (Sydney)"], "1992 (Barcelona)")
]

POLLS_RAW = [
    ("Which sport requires higher peak cardiovascular stamina?", ["Football", "Badminton", "Cricket"]),
    ("Is T20 cricket overshadowing the legacy of Test matches?", ["Yes, completely", "No, Test is still pinnacle"]),
    ("Who is the undisputed Greatest of All Time (GOAT) in football?", ["Lionel Messi", "Cristiano Ronaldo", "Pelé / Maradona"]),
    ("Should VAR and DRS decision reviews have a strict 30-second timer?", ["Yes, preserve match flow", "No, absolute accuracy matters"]),
    ("Which tournament trophy is the most prestigious in sports?", ["FIFA World Cup", "ICC Cricket World Cup", "Olympic Gold Medal"]),
    ("Best matchday experience for a fan?", ["Loud Football Stadium", "Cricket World Cup Derby", "Indoor Badminton Arena"]),
    ("Do you prefer high-scoring thrillers or tactical defensive battles?", ["High-scoring action", "Defensive masterclasses"]),
    ("Should badminton adopt rally-scoring up to 15 points instead of 21?", ["Keep 21 points", "Shift to shorter 15 points"]),
    ("Is IPL the most competitive domestic sports league in the world?", ["Yes", "No, European football leagues are tougher"]),
    ("Greatest individual sporting rivalry?", ["Messi vs Ronaldo", "Lin Dan vs Lee Chong Wei", "India vs Pakistan (Cricket)"]),
    ("Should cricket be a regular sport at every Summer Olympics?", ["Yes, mandatory", "No, international calendar is packed"]),
    ("Which format tests a cricketer's pure skill the most?", ["Test Cricket", "One Day Internationals (ODI)", "T20 Internationals"]),
    ("Best football league in the world right now?", ["English Premier League", "La Liga", "UEFA Champions League"]),
    ("Is Viktor Axelsen the greatest European badminton player in history?", ["Yes, back-to-back Olympic Gold confirms it", "Peter Gade was better"]),

]

FACTS_RAW = [
    "The fastest recorded badminton smash in an official match reached an astounding 493 km/h by Tan Boon Heong, faster than a high-speed bullet train!",
    "Modern badminton rules were developed in the mid-19th century in Pune (Poona), India, by British army officers.",
    "A standard tournament feather shuttlecock is crafted using 16 feathers taken exclusively from the left wing of a goose for aerodynamic symmetry.",
    "A regulation cricket ball's seam is hand-stitched with between 65 and 70 stitches.",
    "Cricket was played at the Summer Olympic Games once, at the 1900 Paris Games, where Great Britain won gold.",
    "Midfielders in a professional 90-minute football match run an average of 10 to 13 kilometers per game.",
    "The legendary Don Bradman required just 4 runs in his final Test innings to retire with an exact career batting average of 100.00; he was bowled for a duck.",
    "The earliest version of football, called 'Cuju', dates back to the Han Dynasty in China over 2,000 years ago.",
    "A single badminton match can see players run up to 6 kilometers across quick multidirectional lunges and jumps on a 13.4-meter court.",
    "Courtney Walsh was the first bowler in cricket history to break the milestone barrier of 500 Test wickets.",
    "The first-ever international football match took place in 1872 between Scotland and England; it ended in a 0-0 draw.",
    "Prakash Padukone trained in Denmark in the late 1970s, pioneering professional international badminton regimens for Indian athletes.",
    "The Melbourne Cricket Ground (MCG) in Australia has light towers so tall they measure approximately 85 meters (equivalent to a 24-story building)."
]

def seed_question_bank():
    db = BankSession()
    if db.query(QuestionBankItem).count() < 250:
        db.query(QuestionBankItem).delete() 
        
        items = []
        for q, opts, ans in CRICKET_RAW:
            items.append(QuestionBankItem(sport="Cricket", type="MCQ", category="Trivia", question=q, options=opts, correct_answer=ans))
        for q, opts, ans in FOOTBALL_RAW:
            items.append(QuestionBankItem(sport="Football", type="MCQ", category="Trivia", question=q, options=opts, correct_answer=ans))
        for q, opts, ans in BADMINTON_RAW:
            items.append(QuestionBankItem(sport="Badminton", type="MCQ", category="Trivia", question=q, options=opts, correct_answer=ans))
        for q, opts in POLLS_RAW:
            items.append(QuestionBankItem(sport="General", type="POLL", category="Fan Vote", question=q, options=opts, correct_answer=None))
        for fact_text in FACTS_RAW:
            items.append(QuestionBankItem(sport="General", type="FACT", category="Did You Know?", question=fact_text, options=None, correct_answer=None))
            
        db.add_all(items)
        db.commit()
        print(f"Successfully seeded {len(items)} questions into sports_bank.db (50 Cricket, 50 Football, 50 Badminton, 50 Polls, 50 Facts).")
    else:
        print("Question bank already contains 250 items.")
    db.close()

if __name__ == "__main__":
    seed_question_bank()