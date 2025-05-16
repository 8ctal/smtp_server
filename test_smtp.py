import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_smtp_connection():
    # SMTP Configuration
    smtp_server = "smtp.mailersend.net"
    smtp_port = 587
    smtp_username = os.getenv('MAILERSEND_SMTP_USERNAME')
    smtp_password = os.getenv('MAILERSEND_SMTP_PASSWORD')
    from_email = f"noreply@{os.getenv('MAILERSEND_DOMAIN')}"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = "scientificpublic@gmail.com"  # Replace with your test email
    msg['Subject'] = "Test Email from MailerSend"
    
    body = "This is a test email to verify SMTP configuration."
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            print("Connected to SMTP server")
            
            # Login
            server.login(smtp_username, smtp_password)
            print("Successfully logged in")
            
            # Send email
            server.send_message(msg)
            print("Test email sent successfully!")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_smtp_connection() 