# LinkedIn Outreach Automation

> Automated job application pipeline for freshers — scrapes LinkedIn hiring posts, generates personalized AI emails, and sends them with the right resume attached.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Selenium](https://img.shields.io/badge/Selenium-4.x-green)
![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3-orange)
![Gmail](https://img.shields.io/badge/Gmail-SMTP-red)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## What it does

| Step | Script | Description |
|------|--------|-------------|
| 1 | `login3.py` | Logs into LinkedIn, scrapes hiring posts from targeted hashtags |
| 2 | `generateemail.py` | Generates personalized cold emails using Groq AI |
| 3 | `sendemail.py` | Sends emails with correct resume attached, saves LinkedIn DMs |

**20 personalized applications in under 5 minutes — daily.**

---

## How it works

LinkedIn Hashtags (#aiintern, #javadeveloper, #fullstack)
↓
Selenium scraper (login3.py)
↓
Keyword filter (role + hiring signal matching)
↓
Groq LLaMA 3 email generator (generateemail.py)
├── AI roles    → Tejendra_resume.pdf
└── Dev roles   → Tejendra_Ayyappa_Reddy_resume.pdf
↓
Gmail SMTP sender (sendemail.py)
├── Direct email → sends automatically
├── Apply link   → opens in browser
└── Manual DM    → saves to manual_dms.txt

---

## Tech Stack

- **Scraping** — Selenium (visible Chrome, cookie-based auth)
- **AI** — Groq API (LLaMA 3.1 8B Instant) for email generation
- **Email** — Python smtplib + Gmail SMTP
- **Resume parsing** — pypdf
- **Config** — python-dotenv

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Tejendra-dev/linkedin-outreach-automation
cd linkedin-outreach-automation
```

### 2. Install dependencies
```bash
pip install selenium pypdf python-dotenv groq
```

### 3. Configure `.env`
Create a `.env` file in the root folder:
```env
LINKEDIN_EMAIL=your_linkedin_email@gmail.com
LINKEDIN_PASSWORD=your_linkedin_password
GROQ_API_KEY=your_groq_api_key
EMAIL_USER=your_gmail@gmail.com
EMAIL_PASS=your_gmail_app_password
SENDER_NAME=Your Full Name
SENDER_EMAIL=your_email@gmail.com
LINKEDIN_URL=https://www.linkedin.com/in/your-profile/
GITHUB_URL=https://github.com/your-username
TARGET_POSTS=20
JOB_TITLES=AI Intern,Java Developer,Full Stack Developer
```

### 4. Run the pipeline
```bash
# Step 1: Scrape LinkedIn hiring posts
python login3.py

# Step 2: Generate personalized emails
python generateemail.py

# Step 3: Send emails / save LinkedIn DMs
python sendemail.py
```

---

## Key Features

- **Smart resume selection** — automatically picks AI resume for AI roles, Java resume for dev roles
- **Noise filtering** — rejects irrelevant posts (HR, SAP, WFH MLM, etc.)
- **Personalized greetings** — extracts recruiter first name from post
- **Rate limit handling** — automatic retry with exponential backoff
- **Dual output** — sends emails directly OR saves messages for LinkedIn DM
- **Daily pipeline** — run every morning for fresh opportunities

---

## Project Structure

---

## Results

- 20 targeted applications generated per run
- Role-specific resume automatically attached
- Personalized email per recruiter using job post context
- Filters reduce noise from ~80% irrelevant posts to 0%

---

## Built by

**Tejendra Ayyappa Reddy Syamala**
- LinkedIn: [linkedin.com/in/tejendra-ayyappa-reddy](https://www.linkedin.com/in/tejendra-ayyappa-reddy/)
- GitHub: [github.com/Tejendra-dev](https://github.com/Tejendra-dev)
- Live project: [JobPulse AI](https://jobpulse-frontend.vercel.app)

---

> Built as a real-world automation project while actively job hunting as a fresher.
> If this helped you, drop a ⭐ on the repo!

