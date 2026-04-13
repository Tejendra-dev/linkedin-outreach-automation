import pickle, os
from datetime import datetime

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "linkedin_cookies.pkl")
cookies = pickle.load(open(path, "rb"))
print(f"Total cookies: {len(cookies)}\n")
for c in cookies:
    name = c.get("name", "?")
    domain = c.get("domain", "?")
    expiry = c.get("expiry", "session")
    if expiry != "session":
        try:
            exp_str = datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M")
        except:
            exp_str = str(expiry)
    else:
        exp_str = "session"
    print(f"  {name:<35} domain={domain:<30} expiry={exp_str}")