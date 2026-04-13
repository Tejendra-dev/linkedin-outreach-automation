import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get("https://www.linkedin.com/login")

print("Please log into LinkedIn manually in the Chrome window that just opened.")
print("After you are fully logged in and can see your feed, come back here and press Enter.")
input("Press Enter after you have logged in...")

cookies = driver.get_cookies()
pickle.dump(cookies, open("linkedin_cookies.pkl", "wb"))
print("✅ Cookies saved to linkedin_cookies.pkl!")
driver.quit()