from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import socket
import json
import requests
from functools import wraps
import time
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for CSRF protection

class EmailForm(FlaskForm):
    from_email = StringField('From', validators=[DataRequired(), Email()])
    to_email = StringField('To', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

@contextmanager
def smtp_connection():
    """Context manager for SMTP connection with optimized timeout"""
    smtp_host = os.getenv('SMTP_HOST', 'mailhog')
    smtp_port = int(os.getenv('SMTP_PORT', '1026' if smtp_host != 'mailhog' else '1025'))
    
    # Set a shorter timeout for the connection
    socket.setdefaulttimeout(2)  # 2 seconds timeout
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=2)
        server.set_debuglevel(0)  # Disable debug output
        yield server
    finally:
        try:
            server.quit()
        except:
            pass

def send_email_async(from_email, to_email, subject, message):
    """Send email with optimized connection handling"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        logger.info(f"Attempting to send email from {from_email} to {to_email}")
        
        with smtp_connection() as server:
            # Send the message
            server.send_message(msg)
            logger.info("Email sent successfully")
            return True, "Email sent successfully"
            
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        return False, f"SMTP Error: {str(e)}"
    except socket.timeout:
        logger.error("Connection timed out")
        return False, "Connection timed out. Please try again."
    except ConnectionRefusedError:
        logger.error("Connection refused")
        return False, "Could not connect to SMTP server. Please check if the server is running."
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return False, str(e)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            # Start the email sending process
            success, message = send_email_async(
                form.from_email.data,
                form.to_email.data,
                form.subject.data,
                form.message.data
            )
            
            if success:
                flash('Email sent successfully!', 'success')
            else:
                flash(f'Error sending email: {message}', 'error')
            
            return redirect(url_for('index'))
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            flash(f'Error sending email: {str(e)}', 'error')
    
    return render_template('index.html', form=form)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000) 