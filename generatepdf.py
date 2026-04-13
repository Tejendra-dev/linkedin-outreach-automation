import os
import re
import json
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# -------------------------------
# SETUP
# -------------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-1.5-flash"

# -------------------------------
# STEP 1 - Load raw text posts
# -------------------------------
def load_raw_text(file_path="raw_posts.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Split posts by separator line
    posts = [p.strip() for p in content.split("="*120) if p.strip()]
    return posts

# -------------------------------
# STEP 2 - Analyze & Structure Posts
# -------------------------------
def process_with_gemini(posts, batch_size=5):
    structured = []

    for i in range(0, len(posts), batch_size):
        batch = posts[i:i+batch_size]

        prompt = f"""
You are a smart assistant for job extraction.
Analyze these raw LinkedIn posts and extract structured info only for roles relevant to CSE background (AI/ML/Backend/Programming).

For each relevant post, return JSON with fields:
- company
- role
- skills
- emails
- phone_numbers
- links
- comments_count
- post_text
- post_date
- job_description  # summary of 3-4 lines

If a post is not relevant, skip it.

Posts:
{json.dumps(batch, ensure_ascii=False)}
"""
        try:
            response = genai.GenerativeModel(MODEL).generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            if isinstance(data, list):
                structured.extend(data)
            else:
                structured.append(data)

        except Exception as e:
            print("⚠️ Gemini parse error:", e)
            with open("gemini_failures.log", "a", encoding="utf-8") as log:
                log.write("\n\n--- Gemini Failure ---\n")
                log.write(f"Batch: {json.dumps(batch, ensure_ascii=False)}\n")
                log.write(f"Response: {getattr(response, 'text', 'No response')}\n")
                log.write("----------------------\n")
            continue

    return structured

# -------------------------------
# STEP 3 - Save structured PDF
# -------------------------------
def save_as_pdf(structured):
    file_path = "structured_ai_posts.pdf"
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    for i, post in enumerate(structured, start=1):
        elements.append(Paragraph(f"<b>Post {i}</b>", styles["Heading2"]))
        elements.append(Paragraph(post.get("post_text", ""), styles["Normal"]))
        elements.append(Spacer(1, 12))

        data = [
            ["Company", post.get("company", "")],
            ["Role", post.get("role", "")],
            ["Skills", ", ".join(post.get("skills", [])) if isinstance(post.get("skills"), list) else post.get("skills", "")],
            ["Emails", ", ".join(post.get("emails", [])) if isinstance(post.get("emails"), list) else post.get("emails", "")],
            ["Phone Numbers", ", ".join(post.get("phone_numbers", [])) if isinstance(post.get("phone_numbers"), list) else post.get("phone_numbers", "")],
            ["Links", ", ".join(post.get("links", [])) if isinstance(post.get("links"), list) else post.get("links", "")],
            ["Comments Count", str(post.get("comments_count", 0))],
            ["Post Date", post.get("post_date", "")],
            ["Job Description", post.get("job_description", "")]
        ]
        table = Table(data, colWidths=[100, 380])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("BOX", (0,0), (-1,-1), 1, colors.black),
            ("INNERGRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        table.splitByRow = True
        elements.append(table)
        elements.append(Spacer(1, 20))

    doc.build(elements)
    print("✅ Structured data saved to", file_path)
    return file_path

# -------------------------------
# STEP 4 - Send email
# -------------------------------
def send_email(file_path):
    msg = EmailMessage()
    msg["Subject"] = "Structured AI/ML LinkedIn Posts"
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = os.getenv("EMAIL_TO")
    msg.set_content("Hi,\n\nAttached is the structured AI/ML LinkedIn post data.\n\nRegards")

    with open(file_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(file_path)
    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=file_name)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        smtp.send_message(msg)

    print(f"📧 Sent email to {os.getenv('EMAIL_TO')}")

# -------------------------------
# RUN
# -------------------------------
if __name__ == "__main__":
    raw_posts = load_raw_text("raw_posts.txt")
    structured_posts = process_with_gemini(raw_posts)
    pdf_file = save_as_pdf(structured_posts)
    send_email(pdf_file)
