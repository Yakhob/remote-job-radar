import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ===============================
# DATE WINDOW
# ===============================
DAYS = 14

def normalize(dt):
    if not dt:
        return None
    if dt.tzinfo:
        return dt.replace(tzinfo=None)
    return dt

CUTOFF = normalize(datetime.utcnow() - timedelta(days=DAYS))

jobs = []
raw_count = 0

# ===============================
# HARD BLOCK LIST
# ===============================
BLOCK = [
    "platform engineer","data engineer","ml engineer","machine learning engineer",
    "research engineer","scientist","mlops","devops","site reliability","sre",
    "infrastructure","distributed systems","pretraining","pre-training",
    "senior","staff","principal","architect","lead","manager","director",
    "5+ years","6+ years","7+ years","8+ years","9+ years","10+ years","yoe"
]

# ===============================
# LOCATION FILTER
# ===============================
def valid_location(text):
    t = text.lower()

    if "us only" in t or "united states only" in t or "uk only" in t or "europe only" in t:
        return False

    india = ["india","bangalore","bengaluru","hyderabad","chennai","pune",
             "delhi","new delhi","gurgaon","gurugram","noida",
             "mumbai","ahmedabad","kochi","trivandrum",
             "thiruvananthapuram","kozhikode","calicut"]

    if "remote" in t or "worldwide" in t or "global" in t:
        return True

    return any(x in t for x in india)

# ===============================
# ROLE FILTER
# ===============================
def role_match(text):
    t = text.lower()
    if any(b in t for b in BLOCK):
        return False

    qa = [
        "qa","tester","testing","manual","test case","regression","postman",
        "api","bug","jira","selenium","cypress","playwright","sdet",
        "test engineer","qa engineer","automation tester",
        "evaluator","review","validation","trainer","annotation",
        "label","grading","rating","quality"
    ]
    automation = ["automation","workflow","zapier","make","n8n","no-code","nocode","low-code"]
    voice = ["voice","speech","asr","tts","transcription"]
    frontend = ["frontend","front end","ui developer","ui engineer","react","next.js","vue","svelte","javascript ui","web developer","web app"]
    fullstack = ["fullstack","full stack","full-stack","web engineer","product engineer","javascript","typescript","node","express","api developer"]
    creative = ["video editor","video editing","content creator","video ads","meta ads","tiktok","reels","short form","creative","ad creative","ugc","ai video","runway","pika","sora","descript","capcut","after effects","premiere","final cut"]

    return any(x in t for x in qa + automation + voice + frontend + fullstack + creative)

# ===============================
# DATE PARSERS
# ===============================
def safe_date(v):
    try:
        return normalize(datetime.fromisoformat(str(v).replace("Z","")))
    except:
        return None

def safe_unix_or_iso(v):
    try:
        return normalize(datetime.fromtimestamp(int(v)))
    except:
        try:
            return normalize(datetime.fromisoformat(str(v).replace("Z","")))
        except:
            return None

# ===============================
# FILTER PIPE
# ===============================
def process_job(text, loc, posted):
    global raw_count
    raw_count += 1

    if not posted or posted < CUTOFF:
        return False
    if not role_match(text):
        return False
    if not valid_location(loc + " " + text):
        return False
    return True

# ===============================
# REMOTIVE
# ===============================
print("Remotive...")
try:
    data = requests.get("https://remotive.com/api/remote-jobs").json()["jobs"]
except:
    data = []

for j in data:
    text = j["title"] + " " + j["description"]
    loc = j["candidate_required_location"]
    posted = safe_date(j["publication_date"])
    if not process_job(text, loc, posted): continue
    jobs.append({"Title":j["title"],"Company":j["company_name"],"Location":loc,"Posted":posted,"URL":j["url"],"Source":"Remotive"})

# ===============================
# REMOTIVE COMMUNITY
# ===============================
print("Remotive-Community...")
try:
    data = requests.get("https://remotive.com/api/community/jobs").json()["jobs"]
except:
    data = []

for j in data:
    text = j["title"] + " " + j["description"]
    loc = j.get("candidate_required_location","")
    posted = safe_date(j.get("publication_date"))
    if not process_job(text, loc, posted): continue
    jobs.append({"Title":j["title"],"Company":j["company_name"],"Location":loc,"Posted":posted,"URL":j["url"],"Source":"Remotive-Community"})

# ===============================
# FLEXA
# ===============================
print("Flexa...")
try:
    data = requests.get("https://flexa.careers/api/jobs").json()
except:
    data = []

for j in data:
    if not j.get("remote"): continue
    text = j.get("title","") + " " + j.get("description","")
    posted = safe_date(j.get("created_at"))
    if not process_job(text,"Remote",posted): continue
    jobs.append({"Title":j.get("title"),"Company":j.get("company",{}).get("name",""),"Location":"Remote","Posted":posted,"URL":j.get("url"),"Source":"Flexa"})

# ===============================
# TESTDEVJOBS
# ===============================
print("TestDevJobs...")
try:
    data = requests.get("https://testdevjobs.com/jobs.json").json()
except:
    data = []

for j in data:
    text = j.get("title","") + " " + j.get("description","")
    posted = safe_date(j.get("date"))
    if not process_job(text,"Remote",posted): continue
    jobs.append({"Title":j["title"],"Company":j["company"],"Location":"Remote","Posted":posted,"URL":j["url"],"Source":"TestDevJobs"})

# ===============================
# CHATGPT-JOBS
# ===============================
print("ChatGPT-Jobs...")
try:
    data = requests.get("https://www.chatgpt-jobs.com/api/jobs").json()
except:
    data = []

for j in data:
    text = j.get("title","") + " " + j.get("description","")
    posted = safe_date(j.get("date"))
    if not process_job(text,"Remote",posted): continue
    jobs.append({"Title":j["title"],"Company":j["company"],"Location":"Remote","Posted":posted,"URL":j["url"],"Source":"ChatGPT-Jobs"})

# ===============================
# REMOTEOK
# ===============================
print("RemoteOK...")
try:
    data = requests.get("https://remoteok.com/api").json()[1:]
except:
    data = []

for j in data:
    text = f"{j.get('position','')} {j.get('description','')} {' '.join(j.get('tags',[]))}"
    loc = j.get("location","")
    posted = safe_unix_or_iso(j.get("date"))
    if not process_job(text,loc,posted): continue
    jobs.append({"Title":j.get("position"),"Company":j.get("company"),"Location":loc,"Posted":posted,"URL":"https://remoteok.com"+j.get("url",""),"Source":"RemoteOK"})

# ===============================
# WORKING NOMADS
# ===============================
print("WorkingNomads...")
try:
    data = requests.get("https://www.workingnomads.com/jobsapi").json()["jobs"]
except:
    data = []

for j in data:
    text = j.get("title","") + " " + j.get("description","")
    loc = j.get("location","")
    posted = safe_date(j.get("publication_date"))
    if not process_job(text,loc,posted): continue
    jobs.append({"Title":j["title"],"Company":j["company_name"],"Location":loc,"Posted":posted,"URL":j["url"],"Source":"WorkingNomads"})

# ===============================
# WEWORKREMOTELY (QA)
# ===============================
print("WeWorkRemotely...")
try:
    soup = BeautifulSoup(requests.get("https://weworkremotely.com/categories/remote-qa-testing-jobs").text,"lxml")
except:
    soup = None

if soup:
    for job in soup.select("section.jobs li"):
        try:
            title = job.select_one("span.title").get_text(strip=True)
            company = job.select_one("span.company").get_text(strip=True)
            loc = job.select_one("span.region").get_text(strip=True) if job.select_one("span.region") else "Remote"
            url = "https://weworkremotely.com" + job.select_one("a")["href"]
            posted = normalize(datetime.utcnow())

            if not process_job(title,loc,posted): continue
            jobs.append({"Title":title,"Company":company,"Location":loc,"Posted":posted,"URL":url,"Source":"WeWorkRemotely"})
        except:
            continue

# ===============================
# JOBSPRESSO
# ===============================
print("Jobspresso...")
for page in range(1,6):
    try:
        soup = BeautifulSoup(requests.get(f"https://jobspresso.co/remote-jobs/page/{page}/").text,"lxml")
    except:
        continue

    for c in soup.select("article.job_listing"):
        title = c.select_one("h3")
        company = c.select_one(".job_listing-company")
        loc = c.select_one(".job_listing-location")
        link = c.select_one("a")

        if not title or not link: continue

        title = title.text.strip()
        company = company.text.strip() if company else ""
        loc = loc.text.strip() if loc else "Remote"
        posted = normalize(datetime.utcnow())

        if not process_job(title,loc,posted): continue
        jobs.append({"Title":title,"Company":company,"Location":loc,"Posted":posted,"URL":link["href"],"Source":"Jobspresso"})

# ===============================
# OUTPUT
# ===============================
df = pd.DataFrame(jobs).drop_duplicates()
df = df.sort_values("Posted", ascending=False)
df["Posted"] = df["Posted"].dt.strftime("%Y-%m-%d")
df.to_excel("daily_jobs.xlsx", index=False)

print("\nTOTAL SCANNED:", raw_count)
print("TOTAL MATCHED:", len(jobs))
print("Saved to daily_jobs.xlsx")
