import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import redis
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Redis configuration
redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

# MailerSend SMTP Configuration
SMTP_SERVER = "smtp.mailersend.net"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('MAILERSEND_SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('MAILERSEND_SMTP_PASSWORD')
FROM_EMAIL = f"noreply@{os.getenv('MAILERSEND_DOMAIN')}"

class EmailForm(FlaskForm):
    sender_email = StringField('Sender Email', validators=[DataRequired(), Email()])
    recipient_email = StringField('Recipient Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

def process_email_queue():
    """Process emails from the queue"""
    while True:
        try:
            # Get email data from queue
            email_data = redis_client.blpop('email_queue', timeout=1)
            if not email_data:
                continue

            _, data = email_data
            email_info = json.loads(data)
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = email_info['recipient_email']
            msg['Subject'] = email_info['subject']
            msg.attach(MIMEText(email_info['message'], 'plain'))

            # Send email using MailerSend SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            # Update status in Redis
            email_info['status'] = 'sent'
            email_info['sent_at'] = datetime.now().isoformat()
            redis_client.hset('email_status', email_info['id'], json.dumps(email_info))
            logger.info(f"Email sent successfully to {email_info['recipient_email']}")

        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            if email_info:
                email_info['status'] = 'failed'
                email_info['error'] = str(e)
                redis_client.hset('email_status', email_info['id'], json.dumps(email_info))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            # Generate unique ID for the email
            email_id = datetime.now().strftime('%Y%m%d%H%M%S')
            
            # Prepare email data
            email_data = {
                'id': email_id,
                'sender_email': form.sender_email.data,
                'recipient_email': form.recipient_email.data,
                'subject': form.subject.data,
                'message': form.message.data,
                'status': 'queued',
                'created_at': datetime.now().isoformat()
            }
            
            # Add to queue
            redis_client.rpush('email_queue', json.dumps(email_data))
            redis_client.hset('email_status', email_id, json.dumps(email_data))
            
            return jsonify({
                'status': 'success',
                'message': 'Email queued for sending',
                'email_id': email_id
            })
            
        except Exception as e:
            logger.error(f"Error queueing email: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
            
    return render_template('index.html', form=form)

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        data = request.json
        to_email = data.get('to_email')
        subject = data.get('subject', 'New Message')
        message = data.get('message')

        if not all([to_email, message]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Create message
        msg = MIMEMultipart()
        msg['From'] = FROM_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach message body
        msg.attach(MIMEText(message, 'plain'))

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)

        return jsonify({
            'success': True,
            'message': 'Email sent successfully'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000) 