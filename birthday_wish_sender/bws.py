import os
import asyncio
import psycopg2
import aiosmtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

load_dotenv()

SENDER_EMAIL   = "rachithooda09@gmail.com"
APP_PASSWORD   = os.getenv('MAIL_APP_PASSWORD')
SUBJECT        = "Happy Birthday from Anantya Foundation! 🎂"
CONN_STRING    = os.getenv('DATABASE_URL')
MAX_CONCURRENT = 5

sql = """
    SELECT * FROM members
    WHERE EXTRACT(MONTH FROM dob) = EXTRACT(MONTH FROM CURRENT_DATE)
      AND EXTRACT(DAY   FROM dob) = EXTRACT(DAY   FROM CURRENT_DATE);
"""


def build_birthday_email(recipient_email, member_data):
    name      = member_data.get('fullname', 'Volunteer')
    member_id = member_data.get('member_id', '')

    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Happy Birthday!</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=DM+Serif+Display&display=swap" rel="stylesheet"/>
</head>
<body style="margin:0;padding:0;background-color:#f5efe6;font-family:'DM Sans','Trebuchet MS',Arial,sans-serif;">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5efe6;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background-color:#fffdf8;border-radius:8px;overflow:hidden;box-shadow:0 4px 24px rgba(101,67,33,0.12);border:1px solid #e8d9c4;">

          <!-- Header -->
          <tr>
            <td style="background-color:#5c3a1e;padding:40px 48px 32px;text-align:center;">
              <p style="margin:0 0 8px;font-size:40px;">🎂</p>
              <p style="margin:0 0 6px;font-family:'DM Sans',Arial,sans-serif;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:#c8a97a;">Est. with Purpose</p>
              <h1 style="margin:0;font-family:'DM Serif Display','Georgia',serif;font-size:30px;font-weight:normal;color:#fff8ee;letter-spacing:1px;">Anantya Foundation</h1>
              <p style="margin:6px 0 0;font-size:12px;color:#d4a96a;letter-spacing:1px;font-style:italic;">परिवर्तन अनंतते वर्तते</p>
              <div style="margin:18px auto 0;width:60px;height:2px;background:linear-gradient(to right,#e8923a,#f5c842,#6cbf6c,#5b9bd5,#9b59b6);border-radius:2px;"></div>
            </td>
          </tr>

          <!-- Colorful accent bar -->
          <tr>
            <td style="height:5px;background:linear-gradient(to right,#e8923a 20%,#f5c842 20% 40%,#6cbf6c 40% 60%,#5b9bd5 60% 80%,#9b59b6 80%);"></td>
          </tr>

          <!-- Welcome Banner -->
          <tr>
            <td style="background-color:#fdf4e7;padding:20px 48px;text-align:center;border-bottom:1px solid #e8d9c4;">
              <p style="margin:0;font-family:'DM Sans',Arial,sans-serif;font-size:12px;letter-spacing:3px;text-transform:uppercase;color:#7a4a1e;font-weight:700;">✦ Wishing You a Wonderful Birthday ✦</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:40px 48px;">

              <p style="margin:0 0 20px;font-size:16px;line-height:1.7;color:#3a2010;">Dear <strong style="color:#5c3a1e;">{name}</strong>,</p>

              <p style="margin:0 0 24px;font-size:15px;line-height:1.8;color:#5a4030;">
                On behalf of everyone at Anantya Foundation, we wish you a very <strong style="color:#e8923a;">Happy Birthday!</strong> 🎉 Your dedication and service to the community inspire everyone around you.
              </p>

              <p style="margin:0 0 28px;font-size:15px;line-height:1.8;color:#5a4030;">
                Today, we celebrate not just your birthday, but the wonderful impact you've made as a volunteer. Your contributions mean the world to us.
              </p>

              <!-- Volunteer ID Box -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:32px;">
                <tr>
                  <td style="background-color:#fdf4e7;border:1px solid #d4a96a;border-left:5px solid #e8923a;border-radius:6px;padding:20px 24px;">
                    <p style="margin:0 0 6px;font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#7a4a1e;">Your Volunteer ID</p>
                    <p style="margin:0;font-size:26px;font-weight:bold;color:#5c3a1e;letter-spacing:2px;font-family:'Courier New',monospace;">{member_id}</p>
                    <p style="margin:8px 0 0;font-size:12px;color:#8a6a50;line-height:1.5;">Keep making a difference — we're grateful to have you with us.</p>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 32px;font-size:14px;line-height:1.8;color:#5a4030;">
                May this year bring you great joy, good health, and countless opportunities to create positive change. We look forward to your continued journey with us.
              </p>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:36px;">
                <tr>
                  <td style="text-align:center;">
                    <a href="mailto:anantyafoundation03@gmail.com" style="display:inline-block;background-color:#5c3a1e;color:#fff8ee;text-decoration:none;font-size:13px;font-weight:700;padding:12px 32px;border-radius:4px;letter-spacing:1px;">Get in Touch</a>
                  </td>
                </tr>
              </table>

              <p style="margin:0;font-size:14px;color:#3a2010;">With warm birthday wishes,</p>
              <p style="margin:4px 0 0;font-size:15px;font-weight:700;color:#5c3a1e;">Team Anantya Foundation</p>

            </td>
          </tr>

          <!-- Colorful accent bar (bottom) -->
          <tr>
            <td style="height:5px;background:linear-gradient(to right,#9b59b6 20%,#5b9bd5 20% 40%,#6cbf6c 40% 60%,#f5c842 60% 80%,#e8923a 80%);"></td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color:#5c3a1e;padding:28px 48px;text-align:center;">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:12px;">
                    <span style="font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#c8a97a;">Contact Us</span>
                  </td>
                </tr>
                <tr>
                  <td align="center">
                    <p style="margin:0 0 6px;font-size:13px;color:#e8d9c4;">
                      <a href="tel:+918076339730" style="color:#d4a96a;text-decoration:none;">+91 8076339730</a>
                    </p>
                    <p style="margin:0;font-size:13px;color:#e8d9c4;">
                      <a href="mailto:anantyafoundation03@gmail.com" style="color:#d4a96a;text-decoration:none;">anantyafoundation03@gmail.com</a>
                    </p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>

        <p style="margin:20px 0 0;font-size:11px;color:#a08060;text-align:center;">This is an official communication from Anantya Foundation.</p>
      </td>
    </tr>
  </table>

</body>
</html>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From']    = f"Anantya Foundation <{SENDER_EMAIL}>"
    msg['To']      = recipient_email
    msg.attach(MIMEText(html_body, 'html'))
    return msg


async def send_birthday_email(member, semaphore):
    name  = member.get('fullname', 'Unknown')
    email = member.get('email')

    if not email:
        print(f"[WARN] No email for {name}, skipping.")
        return

    msg = build_birthday_email(email, member)

    async with semaphore:
        try:
            await aiosmtplib.send(
                msg,
                hostname="smtp.gmail.com",
                port=465,
                username=SENDER_EMAIL,
                password=APP_PASSWORD,
                use_tls=True,
            )
            print(f"[SUCCESS] Birthday email sent to {name} ({email})")
        except Exception as e:
            print(f"[ERROR] Failed to send to {email}: {e}")


async def main():
    print("[INFO] Checking for today's birthdays...")
    try:
        with psycopg2.connect(CONN_STRING) as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                records  = cur.fetchall()
                colnames = [desc[0] for desc in cur.description]

            if not records:
                print("[INFO] No birthdays today.")
                return

            print(f"[INFO] Found {len(records)} birthday(s) today.")
            members = [dict(zip(colnames, row)) for row in records]

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = [send_birthday_email(m, semaphore) for m in members]
    await asyncio.gather(*tasks)
    print("[INFO] Done.")


if __name__ == "__main__":
    while True:
        asyncio.run(main())
        print("Done birthdays for today! putting to sleep!")
        time.sleep(43200)  # run once every 12 hours