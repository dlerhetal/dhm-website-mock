import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config


def send_reset_email(to_email, reset_url):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'D&H Meats — Password Reset'
    msg['From'] = config.MAIL_FROM
    msg['To'] = to_email

    text = f"""You requested a password reset for your D&H Meats account.

Click the link below to set a new password (expires in 1 hour):
{reset_url}

If you didn't request this, ignore this email.

— D&H Meats
(319) 270-4800
"""

    html = f"""<html><body style="font-family: Arial, sans-serif; color: #333;">
<h2 style="color: #000;">Password Reset</h2>
<p>You requested a password reset for your D&H Meats account.</p>
<p><a href="{reset_url}" style="display: inline-block; background: #FFCD00; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">Reset Password</a></p>
<p style="color: #666; font-size: 14px;">This link expires in 1 hour. If you didn't request this, ignore this email.</p>
<hr style="border: none; border-top: 1px solid #eee;">
<p style="color: #999; font-size: 12px;">D&H Meats &bull; 325 1st ST, Palo, Iowa 52324 &bull; (319) 270-4800</p>
</body></html>"""

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    if not config.MAIL_PASSWORD:
        print(f"[MAIL] Reset link for {to_email}: {reset_url}")
        return True

    try:
        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
            server.starttls()
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[MAIL ERROR] {e}")
        return False
