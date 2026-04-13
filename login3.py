import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

load_dotenv()

LINKEDIN_EMAIL    = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
TARGET_POSTS      = int(os.getenv("TARGET_POSTS", 30))

if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
    raise ValueError("❌ Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env")

# ── Only tech/dev/AI roles relevant to your profile ──────────────────────────
ROLE_KEYWORDS = [
    "ai intern", "ai developer", "ai engineer",
    "web developer", "web development",
    "full stack", "fullstack",
    "frontend developer", "front end developer",
    "backend developer", "back end developer",
    "java developer", "java intern",
    "software engineer intern", "software developer intern",
    "ml intern", "machine learning intern",
    "python developer", "python intern",
    "react developer", "react intern",
    "node developer", "node.js",
    "entry level developer", "entry level engineer",
    "junior developer", "junior engineer",
    "fresher developer", "fresher engineer",
    "data science intern", "data analyst intern",
    "prompt engineer", "ai trainer",
    "internship", "intern"
]

# ── Must also contain a hiring signal ────────────────────────────────────────
HIRING_SIGNALS = [
    "hiring", "we're hiring", "we are hiring", "looking for",
    "open position", "join our team", "apply", "opportunity",
    "dm me", "send your resume", "send resume", "reach out"
]

# ── Reject posts with these — not relevant to your skills ────────────────────
REJECT_KEYWORDS = [
    "hr recruiter", "hr intern", "human resource",
    "sap consultant", "sap module",
    "civil engineer", "mechanical engineer",
    "news anchor", "journalist", "content writer",
    "social media executive", "digital marketing",
    "work from home opportunity", "eagle club",
    "mlm", "network marketing", "direct selling",
    "sales executive", "business development",
    "accountant", "finance", "chartered accountant",
    "teach", "teacher", "tutor", "faculty",
    "hindi mandatory", "hindi language",
    "chat process", "bpo", "customer support"
]

# ── Targeted hashtag URLs ─────────────────────────────────────────────────────
HASHTAG_URLS = [
    ("https://www.linkedin.com/feed/hashtag/aiintern/",              "#aiintern"),
    ("https://www.linkedin.com/feed/hashtag/aideveloper/",           "#aideveloper"),
    ("https://www.linkedin.com/feed/hashtag/aiengineer/",            "#aiengineer"),
    ("https://www.linkedin.com/feed/hashtag/webdeveloper/",          "#webdeveloper"),
    ("https://www.linkedin.com/feed/hashtag/fullstackdeveloper/",    "#fullstackdeveloper"),
    ("https://www.linkedin.com/feed/hashtag/frontenddeveloper/",     "#frontenddeveloper"),
    ("https://www.linkedin.com/feed/hashtag/javadeveloper/",         "#javadeveloper"),
    ("https://www.linkedin.com/feed/hashtag/reactdeveloper/",        "#reactdeveloper"),
    ("https://www.linkedin.com/feed/hashtag/pythonintern/",          "#pythonintern"),
    ("https://www.linkedin.com/feed/hashtag/softwareengineerintern/","#softwareengineerintern"),
    ("https://www.linkedin.com/feed/hashtag/mlintern/",              "#mlintern"),
    ("https://www.linkedin.com/feed/hashtag/freshersjobs/",          "#freshersjobs"),
    ("https://www.linkedin.com/feed/hashtag/entrylevel/",            "#entrylevel"),
]

# -------------------------------
# RELEVANCE FILTER
# -------------------------------
def is_relevant_post(text):
    t = text.lower()

    # Reject irrelevant roles first
    if any(kw in t for kw in REJECT_KEYWORDS):
        return False

    # Must have a hiring signal
    has_signal = any(kw in t for kw in HIRING_SIGNALS)
    if not has_signal:
        return False

    # Must mention a relevant role
    has_role = any(kw in t for kw in ROLE_KEYWORDS)
    if not has_role:
        return False

    return True

# -------------------------------
# CHROME DRIVER
# -------------------------------
def create_driver():
    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(30)
    return driver

# -------------------------------
# LOGIN
# -------------------------------
def login(driver):
    print("🔐 Logging into LinkedIn...")
    try:
        driver.get("https://www.linkedin.com/login")
    except TimeoutException:
        pass

    # Wait longer for page to fully render
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        time.sleep(2)
    except TimeoutException:
        print(f"  ❌ Login page did not load. Title: {driver.title} | URL: {driver.current_url}")
        return False

    try:
        email_field = driver.find_element(By.ID, "username")
        email_field.clear()
        time.sleep(1)
        email_field.send_keys(LINKEDIN_EMAIL)
        print("  ✅ Email entered")
    except Exception as e:
        print(f"  ❌ Email field error: {e}")
        return False

    try:
        pass_field = driver.find_element(By.ID, "password")
        pass_field.clear()
        time.sleep(1)
        pass_field.send_keys(LINKEDIN_PASSWORD)
        print("  ✅ Password entered")
    except Exception as e:
        print(f"  ❌ Password field error: {e}")
        return False

    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        btn.click()
        print("  ✅ Login button clicked")
    except Exception as e:
        print(f"  ❌ Submit button error: {e}")
        return False

    time.sleep(8)
    print(f"  🌐 URL: {driver.current_url}")
    print(f"  📄 Title: {driver.title}")

    if "feed" in driver.current_url or "mynetwork" in driver.current_url:
        print("✅ Logged in successfully!")
        return True
    elif "checkpoint" in driver.current_url or "challenge" in driver.current_url:
        print("\n⚠️ LinkedIn verification required!")
        input("👉 Complete verification in Chrome window, then press Enter: ")
        time.sleep(3)
        if "feed" in driver.current_url:
            print("✅ Logged in after verification!")
            return True

    print(f"❌ Login failed — URL: {driver.current_url}")
    return False
# -------------------------------
# PARSE BODY TEXT INTO POST BLOCKS
# -------------------------------
def parse_blocks(body_text, hashes_seen):
    new_blocks = []
    raw_blocks = re.split(
        r'\n(?=[A-Z][^\n]{2,60}\n[^\n]{0,100}(?:•|\d+[smhdw]|Follow|Connect|\d+st|\d+nd|\d+rd))',
        body_text
    )
    for block in raw_blocks:
        block = block.strip()
        if len(block) < 100:
            continue
        h = hash(block[:300])
        if h in hashes_seen:
            continue
        hashes_seen.add(h)
        new_blocks.append(block)
    return new_blocks

# -------------------------------
# SCRAPE ONE URL
# -------------------------------
def scrape_url(driver, url, label, target, all_hashes):
    print(f"\n📄 Scraping: {label}")

    try:
        driver.get(url)
        time.sleep(5)
    except TimeoutException:
        print("  ⚠️ Timed out — skipping")
        return []

    if "login" in driver.current_url.lower():
        print("  ❌ Redirected to login — skipping")
        return []

    print(f"  📄 Title: {driver.title}")

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
        )
    except TimeoutException:
        pass
    time.sleep(3)

    posts_text = []
    scrolls = 0
    no_new_count = 0
    last_offset = -1
    rejected = 0

    while len(posts_text) < target and no_new_count < 5:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(3)
        scrolls += 1

        offset = driver.execute_script("return window.pageYOffset")
        if offset == last_offset and scrolls > 2:
            print("  🛑 End of feed")
            break
        last_offset = offset

        try:
            body_text = driver.find_element(By.TAG_NAME, "body").text
        except:
            no_new_count += 1
            continue

        before = len(posts_text)
        all_blocks = parse_blocks(body_text, all_hashes)

        for block in all_blocks:
            # Apply relevance filter
            if not is_relevant_post(block):
                rejected += 1
                continue

            emails = re.findall(r'\b[\w.\-+]+@[\w.\-]+\.\w{2,}\b', block)
            phones = re.findall(r'\+?\d[\d\-\s]{7,}\d', block)
            links  = re.findall(r'https?://\S+', block)

            entry = (
                f"SOURCE:\n{label}\n\n"
                f"POST TEXT:\n{block}\n\n"
                f"EMAILS:\n" + ("\n".join(emails) if emails else "None found") + "\n\n"
                f"PHONES:\n" + ("\n".join(phones) if phones else "None") + "\n\n"
                f"LINKS:\n" + ("\n".join(links) if links else "None") + "\n"
            )
            posts_text.append(entry)
            status = f"📧 {emails[0]}" if emails else "📝 post"
            print(f"  ✅ #{len(posts_text)} — {status}")

            if len(posts_text) >= target:
                break

        if len(posts_text) == before:
            no_new_count += 1
            print(f"  ⏳ No relevant posts this scroll ({no_new_count}/5)")
        else:
            no_new_count = 0

        print(f"  ⬇️ Scroll {scrolls} → {len(posts_text)} kept | {rejected} rejected")

    return posts_text

# -------------------------------
# MAIN
# -------------------------------
def scrape_posts():
    print("🚀 Starting LinkedIn scraper...\n")
    driver = create_driver()

    if not login(driver):
        driver.quit()
        raise SystemExit("❌ Login failed.")

    all_posts = []
    all_hashes = set()
    posts_per_url = max(3, TARGET_POSTS // len(HASHTAG_URLS))

    for url, label in HASHTAG_URLS:
        if len(all_posts) >= TARGET_POSTS:
            break
        remaining = TARGET_POSTS - len(all_posts)
        batch = scrape_url(driver, url, label, min(posts_per_url, remaining), all_hashes)
        all_posts.extend(batch)
        print(f"  → Batch: {len(batch)} | Total: {len(all_posts)}/{TARGET_POSTS}")
        time.sleep(3)

    driver.quit()

    with open("raw_posts.txt", "w", encoding="utf-8") as f:
        for post in all_posts:
            f.write(post)
            f.write("\n" + "=" * 120 + "\n\n")

    print(f"\n📌 Total relevant posts: {len(all_posts)}")
    print("💾 Saved → raw_posts.txt")
    return all_posts

if __name__ == "__main__":
    scrape_posts()