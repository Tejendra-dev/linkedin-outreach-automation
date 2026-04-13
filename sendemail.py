import os
import csv
import time
import smtplib
import webbrowser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER  = os.getenv("EMAIL_USER")
EMAIL_PASS  = os.getenv("EMAIL_PASS")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))

# -------------------------------
# SEND ONE EMAIL
# -------------------------------
def send_email(to_email, subject, body, resume_filename):
    try:
        msg = MIMEMultipart()
        msg["From"]    = EMAIL_USER
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach the correct resume
        resume_path = os.path.join(BASE_DIR, resume_filename)
        if os.path.exists(resume_path):
            with open(resume_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={resume_filename}"
                )
                msg.attach(part)
            print(f"  📎 Attached: {resume_filename}")
        else:
            print(f"  ⚠️ Resume not found: {resume_filename} — sending without attachment")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        print(f"  ✅ Sent to: {to_email}")
        return True

    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False

# -------------------------------
# MAIN SEND FUNCTION
# -------------------------------
def send_all_from_csv(csv_file=None):
    if csv_file is None:
        csv_file = os.path.join(BASE_DIR, "generated_emails.csv")

    if not os.path.exists(csv_file):
        print(f"❌ {csv_file} not found — run generateemail.py first")
        return

    # Read all rows
    with open(csv_file, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("❌ No rows in CSV.")
        return

    # Separate by method
    email_rows  = [r for r in rows if r.get("method") == "email"]
    link_rows   = [r for r in rows if r.get("method") == "apply_link"]
    manual_rows = [r for r in rows if r.get("method") == "manual"]

    print(f"\n📊 Summary:")
    print(f"   📧 Direct email  : {len(email_rows)}")
    print(f"   🔗 Apply link    : {len(link_rows)}")
    print(f"   ✋ Manual DM     : {len(manual_rows)}")
    print(f"   📌 Total         : {len(rows)}\n")

    # ── SECTION 1: Send direct emails ──────────────────────────
    if email_rows:
        print(f"{'='*60}")
        print(f"📧 SENDING {len(email_rows)} DIRECT EMAILS")
        print(f"{'='*60}")

        confirm = input("Send all direct emails now? (yes/no): ").strip().lower()
        if confirm == "yes":
            sent, failed = 0, 0
            for i, row in enumerate(email_rows):
                print(f"\n📤 [{i+1}/{len(email_rows)}] {row['role']} at {row['company']}")
                print(f"  To      : {row['send_to']}")
                print(f"  Subject : {row['subject']}")

                success = send_email(
                    to_email        = row["send_to"],
                    subject         = row["subject"],
                    body            = row["body"],
                    resume_filename = row.get("resume", "resume.pdf")
                )
                if success:
                    sent += 1
                else:
                    failed += 1

                time.sleep(3)  # avoid Gmail rate limit

            print(f"\n✅ Sent: {sent} | ❌ Failed: {failed}")
        else:
            print("⏩ Direct email sending skipped.")
    else:
        print("ℹ️ No direct email rows found.")

    # ── SECTION 2: Apply link rows ──────────────────────────────
    if link_rows:
        print(f"\n{'='*60}")
        print(f"🔗 APPLY LINK ROWS ({len(link_rows)} jobs)")
        print(f"{'='*60}")
        print("These jobs have application links — open them in browser?\n")

        confirm = input("Open apply links in browser? (yes/no): ").strip().lower()
        if confirm == "yes":
            for i, row in enumerate(link_rows):
                print(f"\n🌐 [{i+1}/{len(link_rows)}] {row['role']} at {row['company']}")
                print(f"  Link: {row['send_to']}")
                webbrowser.open(row["send_to"])
                time.sleep(2)
        else:
            print("⏩ Apply links skipped.")
            print("\nLinks to apply manually:")
            for row in link_rows:
                print(f"  • {row['role']} at {row['company']}: {row['send_to']}")

    # ── SECTION 3: Manual DM rows ───────────────────────────────
    if manual_rows:
        print(f"\n{'='*60}")
        print(f"✋ MANUAL DM REQUIRED ({len(manual_rows)} jobs)")
        print(f"{'='*60}")
        print("These recruiters have no email — you need to DM them on LinkedIn.\n")
        print("Here are your generated email bodies to copy-paste into LinkedIn DMs:\n")

        for i, row in enumerate(manual_rows):
            print(f"\n── [{i+1}/{len(manual_rows)}] {row['role']} at {row['company']} ──")
            print(f"Recruiter : {row['recruiter']}")
            print(f"Subject   : {row['subject']}")
            print(f"Message:\n{row['body']}")
            print("-" * 60)

        # Save manual DMs to a separate readable file
        manual_file = os.path.join(BASE_DIR, "manual_dms.txt")
        with open(manual_file, "w", encoding="utf-8") as f:
            for row in manual_rows:
                f.write(f"ROLE: {row['role']}\n")
                f.write(f"COMPANY: {row['company']}\n")
                f.write(f"RECRUITER: {row['recruiter']}\n")
                f.write(f"SUBJECT: {row['subject']}\n")
                f.write(f"MESSAGE:\n{row['body']}\n")
                f.write("\n" + "=" * 80 + "\n\n")

        print(f"\n💾 All manual DM messages saved → manual_dms.txt")
        print("👉 Open LinkedIn, find each recruiter, and send the message.")

    print(f"\n{'='*60}")
    print("✅ sendemail.py complete!")
    print(f"{'='*60}")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ EMAIL_USER or EMAIL_PASS missing in .env")
    else:
        send_all_from_csv()