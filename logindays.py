import os
import time
import pickle
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

# -------------------------------
# LOAD ENVIRONMENT VARIABLES
# -------------------------------
load_dotenv()
job_titles_env = os.getenv("JOB_TITLES")
if not job_titles_env:
    raise ValueError("❌ JOB_TITLES not found in .env. Add job titles separated by commas.")
JOB_TITLES = [title.strip() for title in job_titles_env.split(",")]

TARGET_POSTS = 5         # collect exactly 5 posts
TIME_LAPSE_DAYS = 1      # last 24 hours
MAX_SCROLLS = 10         # maximum number of scrolls per job title

# -------------------------------
# LOGIN WITH COOKIES
# -------------------------------
def linkedin_login_with_cookies(driver, cookies_file="linkedin_cookies.pkl"):
    driver.get("https://www.linkedin.com/")
    cookies = pickle.load(open(cookies_file, "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    print("✅ Logged in with cookies")

# -------------------------------
# SCRAPER FUNCTION
# -------------------------------
def scrape_posts():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)

    linkedin_login_with_cookies(driver)

    all_posts_text = []
    cutoff_date = datetime.now() - timedelta(days=TIME_LAPSE_DAYS)

    for job_title in JOB_TITLES:
        print(f"\n🔎 Searching posts for: '{job_title}'")

        # Search input
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder,'Search')]"))
        )
        search_input.clear()
        search_input.send_keys(job_title)
        search_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Filter for Posts
        try:
            posts_filter = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Posts']"))
            )
            posts_filter.click()
            time.sleep(2)
        except:
            print("⚠️ Could not find Posts filter, continuing...")

        posts_text, hashes_seen = [], set()
        scrolls = 0

        # -------------------------------
        # SCROLL UNTIL TARGET POSTS OR MAX SCROLLS
        # -------------------------------
        while len(posts_text) < TARGET_POSTS and scrolls < MAX_SCROLLS:
            driver.execute_script("window.scrollBy(0, 1200);")
            time.sleep(2)
            scrolls += 1

            post_elements = driver.find_elements(
                By.XPATH,
                "//div[contains(@class,'feed-shared-update-v2') or contains(@class,'update-components-text')]"
            )

            before = len(posts_text)
            for post in post_elements:
                if len(posts_text) >= TARGET_POSTS:
                    break
                try:
                    txt = post.text.strip()
                    if not txt or hash(txt) in hashes_seen:
                        continue

                    # Extract post date
                    try:
                        timestamp_elem = post.find_element(By.TAG_NAME, "time")
                        timestamp = timestamp_elem.get_attribute("datetime")
                        post_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        if post_date < cutoff_date:
                            continue
                    except:
                        continue

                    # Extract post link
                    post_link = "N/A"
                    try:
                        anchor = post.find_element(By.XPATH, ".//a[contains(@href,'/posts/')]")
                        post_link = anchor.get_attribute("href")
                    except:
                        pass

                    # Raw text
                    raw_text = (
                        f"JOB TITLE SEARCHED:\n{job_title}\n\n"
                        f"POST LINK:\n{post_link}\n\n"
                        f"POST DATE:\n{post_date}\n\n"
                        f"POST TEXT:\n{txt}\n\n"
                    )

                    hashes_seen.add(hash(txt))
                    posts_text.append(raw_text)
                except:
                    continue

            if len(posts_text) == before:
                print(f"⬇️ Scroll {scrolls} → No new posts found yet... continuing")
            else:
                print(f"⬇️ Scroll {scrolls} → Collected {len(posts_text)} posts so far")

        if len(posts_text) < TARGET_POSTS:
            print(f"⚠️ Reached max scrolls ({MAX_SCROLLS}) but only found {len(posts_text)} posts")

        all_posts_text.extend(posts_text)

    driver.quit()

    # Save posts
    with open("raw_posts.txt", "w", encoding="utf-8") as f:
        for post in all_posts_text:
            f.write(post)
            f.write("\n" + "="*120 + "\n\n")

    print(f"\n📌 Total posts collected: {len(all_posts_text)}")
    print("💾 Saved raw posts to raw_posts.txt")
    return all_posts_text

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    scrape_posts()
