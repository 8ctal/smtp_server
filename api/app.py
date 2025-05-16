import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# MailerSend SMTP Configuration
SMTP_SERVER = "smtp.mailersend.net"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('MAILERSEND_SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('MAILERSEND_SMTP_PASSWORD')
FROM_EMAIL = f"noreply@{os.getenv('MAILERSEND_DOMAIN')}"

class EmailForm(FlaskForm):
    recipient_email = StringField('Recipient Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = FROM_EMAIL
            msg['To'] = form.recipient_email.data
            msg['Subject'] = form.subject.data
            msg.attach(MIMEText(form.message.data, 'plain'))

            # Send email using MailerSend SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(msg)

            return jsonify({
                'status': 'success',
                'message': 'Email sent successfully'
            })
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
            
    return render_template('index.html', form=form)

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