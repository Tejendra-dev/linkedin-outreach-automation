import os
import re
import csv
import time
from pypdf import PdfReader
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LINKEDIN_URL = os.getenv("LINKEDIN_URL", "")
GITHUB_URL   = os.getenv("GITHUB_URL", "")
SENDER_NAME  = os.getenv("SENDER_NAME", "Tejendra Ayyappa Reddy")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "tejendrasyamala23@gmail.com")

if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY missing in .env")

client = Groq(api_key=GROQ_API_KEY)
MODEL  = "llama-3.1-8b-instant"

# -------------------------------
# RESUME SELECTION BY ROLE
# -------------------------------
AI_ROLE_KEYWORDS = [
    "ai intern", "ai developer", "ai engineer", "artificial intelligence",
    "prompt engineer", "ml intern", "machine learning", "deep learning",
    "data science intern", "ai trainer", "nlp", "llm", "aiengineer",
    "aideveloper", "aiintern", "mlintern", "generative ai", "gen ai"
]

def pick_resume(role_text):
    t = role_text.lower()
    base = os.path.dirname(os.path.abspath(__file__))
    if any(kw in t for kw in AI_ROLE_KEYWORDS):
        name = "Tejendra_resume.pdf"
    else:
        name = "Tejendra Ayyappa Reddy_resume.pdf"
    path = os.path.join(base, name)
    if not os.path.exists(path):
        print(f"  ⚠️ Resume not found: {name}")
        path = os.path.join(base, "resume.pdf")
        name = "resume.pdf"
    return path, name

# -------------------------------
# TEXT CLEANER
# -------------------------------
def clean_text(text):
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    junk_prefixes = [
        "more ", "apply for the ", "join us for a ",
        "view job preferences", "we are hiring ",
        "we are looking for a highly skilled ",
        "we are looking for ", "looking for a ",
        "is looking for an ", "is looking for a ",
        "divine hindu is looking for an ",
        "passionate ", "n experienced ", "n ",
    ]
    for prefix in junk_prefixes:
        if text.lower().startswith(prefix):
            text = text[len(prefix):]
    text = text.strip()
    if text:
        text = text[0].upper() + text[1:]
    return text

# -------------------------------
# STEP 1 — Extract resume text
# -------------------------------
def extract_resume_text(resume_pdf):
    if not os.path.exists(resume_pdf):
        raise FileNotFoundError(f"❌ Resume not found: {resume_pdf}")
    reader = PdfReader(resume_pdf)
    text = ""
    for page in reader.pages:
        t = page.extract_text()
        if t:
            text += t + "\n"
    return text.strip()

# -------------------------------
# STEP 2 — Parse raw_posts.txt
# -------------------------------
def parse_raw_posts(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ {filepath} not found — run login3.py first")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_blocks = content.split("=" * 100)
    posts = []

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue

        source_match = re.search(r"SOURCE:\s*(.+)", block)
        source = source_match.group(1).strip() if source_match else "unknown"

        post_match = re.search(r"POST TEXT:\s*([\s\S]+?)(?=EMAILS:|$)", block)
        post_text = post_match.group(1).strip() if post_match else ""

        if not post_text or len(post_text) < 80:
            continue

        email_match = re.search(r"EMAILS:\s*([\s\S]+?)(?=PHONES:|$)", block)
        email_raw = email_match.group(1).strip() if email_match else ""
        emails = [
            e.strip() for e in email_raw.split("\n")
            if e.strip() and e.strip() != "None found" and "@" in e
        ]

        link_match = re.search(r"LINKS:\s*([\s\S]+?)$", block)
        link_raw = link_match.group(1).strip() if link_match else ""
        links = [
            l.strip() for l in link_raw.split("\n")
            if l.strip() and l.strip() != "None" and l.strip().startswith("http")
        ]

        recruiter_name = extract_recruiter(post_text)
        role           = extract_role(post_text)
        company        = extract_company(post_text)

        posts.append({
            "source":         source,
            "post_text":      post_text,
            "emails":         emails,
            "links":          links,
            "recruiter_name": recruiter_name,
            "role":           role,
            "company":        company,
        })

    print(f"✅ Parsed {len(posts)} posts from {filepath}")
    return posts

# -------------------------------
# HELPERS
# -------------------------------
BAD_NAME_WORDS = {
    "visit", "tag", "react", "frontend", "backend", "hiring", "manager",
    "follow", "connect", "view", "more", "apply", "assistant", "talent",
    "hr", "dear", "hello", "hey", "the", "a", "an", "we", "our", "your"
}

def extract_recruiter(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return "Hiring Manager"
    first = lines[0]
    parts = first.split()
    if (2 <= len(parts) <= 4 and
        all(p[0].isupper() for p in parts if p) and
        not any(char.isdigit() for char in first) and
        len(first) < 40 and
        parts[0].lower() not in BAD_NAME_WORDS):
        return first
    return "Hiring Manager"

def extract_role(text):
    text_clean = re.sub(r'\n+', ' ', text)
    patterns = [
        r"(?:hiring|we.re hiring|we are hiring)\s+(?:a|an)?\s*([A-Za-z\s\/\-]+?(?:intern|developer|engineer|analyst|trainer))",
        r"looking for\s+(?:a|an)?\s*([A-Za-z\s\/\-]+?(?:intern|developer|engineer|analyst|trainer))",
        r"(?:role|position)[:\s]+([A-Za-z\s\/\-]+?(?:intern|developer|engineer|analyst|trainer))",
        r"([A-Za-z\s]*(?:AI|Web|Full[\s\-]?Stack|Frontend|Front[\s\-]End|Backend|Back[\s\-]End|Java|Python|React|ML|Data|Software)[A-Za-z\s]*(?:Intern|Developer|Engineer|Analyst|Trainer))",
    ]
    for pattern in patterns:
        m = re.search(pattern, text_clean, re.IGNORECASE)
        if m:
            role = m.group(1).strip()
            role = re.sub(r'\s+', ' ', role)
            if 3 < len(role) < 50:
                return clean_text(role)
    return "Software Development Intern"

def extract_company(text):
    patterns = [
        r"\bat\s+([A-Z][A-Za-z0-9\s&\.\-]+?)(?:\s*[\|\n,\.]|$)",
        r"\bjoin\s+([A-Z][A-Za-z0-9\s&\.\-]+?)(?:\s*[\|\n,\.]|$)",
        r"[Cc]ompany[:\s]+([A-Z][A-Za-z0-9\s&\.\-]+?)(?:\s*[\|\n,\.]|$)",
        r"🏢\s*([A-Z][A-Za-z0-9\s&\.\-]+?)(?:\s*[\|\n,\.]|$)",
    ]
    bad_company_words = {
        "the", "a", "an", "us", "our", "team", "you", "we", "me",
        "linkedin", "india", "remote", "bangalore", "hyderabad",
        "mumbai", "delhi", "chennai", "pune"
    }
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for company in matches:
            company = company.strip()
            company = re.sub(r'\s+', ' ', company)
            first_word = company.split()[0].lower() if company.split() else ""
            if (2 < len(company) < 50 and
                first_word not in bad_company_words and
                not company[0].islower()):
                return company
    return "the company"

# -------------------------------
# STEP 3 — Generate email with Groq
# -------------------------------
def generate_email(post, resume_text):
    role      = post["role"]
    company   = post["company"]
    job_desc  = post["post_text"][:2000]
    recruiter = post["recruiter_name"]

    first_name = recruiter.split()[0] if recruiter != "Hiring Manager" else ""
    if (not first_name or
        first_name.lower() in BAD_NAME_WORDS or
        len(first_name) > 20 or
        first_name.isupper()):
        first_name = ""
    else:
        first_name = first_name.title()
    greeting = f"Hi {first_name}," if first_name else "Hi there,"

    company_str = company if company.lower() != "the company" else "your company"

    prompt = f"""You are helping {SENDER_NAME} write a cold outreach email for a job application.

CANDIDATE RESUME:
{resume_text}

JOB POST:
{job_desc}

ROLE: {role}
COMPANY: {company_str}

Write a professional cold email following these rules:
1. Start with: {greeting}
2. One sentence: mention the specific role ({role}) at {company_str} and why you are a fit
3. Two sentences: highlight the most relevant skill and ONE specific project from the resume that matches this exact role
4. One sentence: express interest in a quick call or discussion
5. End exactly with:
Best regards,
{SENDER_NAME}
{SENDER_EMAIL}
6. Total: under 150 words
7. Tone: confident, direct, not desperate
8. Do NOT say "I am writing to express my interest"
9. Do NOT mention resume or attachments
10. Do NOT add a subject line
11. Plain text only — no bullet points, no markdown

Output ONLY the email body.
"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            body = response.choices[0].message.content.strip()
            if LINKEDIN_URL:
                body += f"\n🔗 LinkedIn: {LINKEDIN_URL}"
            if GITHUB_URL:
                body += f"\n💻 GitHub: {GITHUB_URL}"
            return body
        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "429" in err or "quota" in err:
                wait = 30 * (attempt + 1)
                print(f"  ⚠️ Rate limit — waiting {wait}s (attempt {attempt+1}/3)")
                time.sleep(wait)
            else:
                print(f"  ❌ Groq error: {e}")
                break

    return "⚠️ Could not generate email."

# -------------------------------
# STEP 4 — Generate subject
# -------------------------------
def generate_subject(role, company):
    role = clean_text(role)
    if company and company.lower() != "the company":
        company = clean_text(company)
        return f"Application – {role} at {company} | {SENDER_NAME}"
    return f"Application – {role} | {SENDER_NAME}"

# -------------------------------
# STEP 5 — Main runner
# -------------------------------
def generate_emails(posts_file=None, output_csv=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if posts_file is None:
        posts_file = os.path.join(base_dir, "raw_posts.txt")
    if output_csv is None:
        output_csv = os.path.join(base_dir, "generated_emails.csv")

    posts = parse_raw_posts(posts_file)

    if not posts:
        print("❌ No posts found. Run login3.py first.")
        return

    results = []

    for i, post in enumerate(posts):
        role    = post["role"]
        company = post["company"]
        print(f"\n📝 [{i+1}/{len(posts)}] {role} at {company}")

        resume_path, resume_name = pick_resume(role + " " + post["post_text"][:300])
        resume_text = extract_resume_text(resume_path)
        print(f"  📄 Resume: {resume_name}")

        body    = generate_email(post, resume_text)
        subject = generate_subject(role, company)

        if post["emails"]:
            send_to = post["emails"][0]
            method  = "email"
        elif post["links"]:
            send_to = post["links"][0]
            method  = "apply_link"
        else:
            send_to = "No contact — DM recruiter on LinkedIn manually"
            method  = "manual"

        results.append({
            "company":      company,
            "role":         clean_text(role),
            "recruiter":    post["recruiter_name"],
            "subject":      subject,
            "body":         body,
            "send_to":      send_to,
            "method":       method,
            "resume":       resume_name,
            "source":       post["source"],
            "post_snippet": post["post_text"][:200].replace("\n", " "),
        })

        print(f"  📧 Send to : {send_to} [{method}]")
        print(f"  Subject   : {subject}")
        print(f"  Preview   : {body[:120]}...")
        time.sleep(6)

    if not results:
        print("❌ No emails generated.")
        return

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    has_email = sum(1 for r in results if r["method"] == "email")
    has_link  = sum(1 for r in results if r["method"] == "apply_link")
    manual    = sum(1 for r in results if r["method"] == "manual")

    print(f"\n{'='*60}")
    print(f"✅ Generated {len(results)} emails")
    print(f"   📧 Direct email : {has_email}")
    print(f"   🔗 Apply link   : {has_link}")
    print(f"   ✋ Manual DM    : {manual}")
    print(f"📂 Saved → {output_csv}")
    print("⚠️  Review the CSV before running sendemail.py")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    generate_emails()