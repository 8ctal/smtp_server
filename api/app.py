import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import traceback

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# MailerSend SMTP Configuration
SMTP_SERVER = "smtp.mailersend.net"
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('MAILERSEND_SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('MAILERSEND_SMTP_PASSWORD')
FROM_EMAIL = os.getenv('MAILERSEND_FROM_EMAIL', f"noreply@{os.getenv('MAILERSEND_DOMAIN')}")

class EmailForm(FlaskForm):
    recipient_email = StringField('Recipient Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    logger.error(traceback.format_exc())
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'details': str(error)
    }), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Resource not found',
        'details': str(error)
    }), 404

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

            flash('Email sent successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            flash(f'Error sending email: {str(e)}', 'danger')
            return redirect(url_for('index'))
    return render_template('index.html', form=form)

# Add SMTP connection test
def test_smtp_connection():
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            return True
    except Exception as e:
        logger.error(f"SMTP Connection Test Failed: {str(e)}")
        return False

@app.route('/api/send-email', methods=['POST'])
def send_email():
    try:
        # Test SMTP connection first
        if not test_smtp_connection():
            return jsonify({
                'success': False,
                'error': 'Failed to connect to SMTP server. Please check your credentials.'
            }), 500

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
            try:
                server.send_message(msg)
            except smtplib.SMTPDataError as e:
                if "Trial accounts can only send emails to the administrator's email" in str(e):
                    logger.error("MailerSend trial account restriction: Can only send to administrator email")
                    return jsonify({
                        'success': False,
                        'error': 'Your MailerSend account is in trial mode. Please upgrade your account or contact support.'
                    }), 500
                raise e

        return jsonify({
            'success': True,
            'message': 'Email sent successfully'
        }), 200

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'SMTP authentication failed. Please check your credentials.'
        }), 500
    except Exception as e:
        logger.error(f"Error in send_email route: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000) 