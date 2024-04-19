import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
load_dotenv()

def send_email(subject, recipient, body):
    sender_email = os.getenv('admin_email')
    sender_password = os.getenv('admin_pw')
    
    # Composing message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient

    # Attach the HTML body to the message
    msg.attach(MIMEText(body, 'html'))

    # Add the Content-Type header, telling the server to expect html
    msg.add_header('Content-Type', 'text/html')
    
    # Connecting to SMTP server
    with smtplib.SMTP(os.getenv('smtp_server'), os.getenv('smtb_port')) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)


email_bodies = {
    "password_reset": """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset Confirmation</title>
    </head>
    <body>
        <h1>Password Reset Confirmation</h1>
        <p>Your password has been successfully reset.</p>
        <p>If you did not request this change, please contact support immediately.</p>
    </body>
    </html>
    """
}


# dev only
if __name__ == "__main__":
    send_email("Subject of the Email", "wellspaul554@gmail.com", email_bodies['password_reset'])