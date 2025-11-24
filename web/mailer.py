# web/mailer.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

LAB_EMAIL = ""
LAB_PASSWORD = ""  # Gmail App Password


def send_done_mail(user_email, job_id):
    if not user_email:
        print("[EMAIL] No user email provided, skip sending mail.")
        return False

    subject = f"[scGHSOM] Job {job_id} Completed"

    body = f"""
Hello,<br><br>

<b>Your scGHSOM analysis is now complete.</b><br><br>

<b>Job ID:</b> {job_id}<br><br>

You may now visit the Results page on our website and enter your Job ID to view all outputs.<br><br>

Thank you for using our service.<br>
scGHSOM Web Server Team
"""

    msg = MIMEMultipart()
    msg["From"] = LAB_EMAIL
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(LAB_EMAIL, LAB_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"[EMAIL SENT] → {user_email}")
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


