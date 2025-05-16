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
import time
from contextlib import contextmanager
from threading import Thread
from queue import Queue
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for CSRF protection

# Email queue and status tracking
email_queue = Queue()
email_status = {}

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

def process_email_queue():
    """Background worker to process email queue"""
    while True:
        try:
            email_data = email_queue.get()
            if email_data is None:
                break
                
            email_id, from_email, to_email, subject, message = email_data
            
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = from_email
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))

                logger.info(f"Processing email {email_id} from {from_email} to {to_email}")
                
                with smtp_connection() as server:
                    # Send the message
                    server.send_message(msg)
                    logger.info(f"Email {email_id} sent successfully")
                    email_status[email_id] = {"status": "success", "message": "Email sent successfully"}
                    
            except Exception as e:
                logger.error(f"Error processing email {email_id}: {str(e)}")
                email_status[email_id] = {"status": "error", "message": str(e)}
                
            finally:
                email_queue.task_done()
                
        except Exception as e:
            logger.error(f"Queue processing error: {str(e)}")
            time.sleep(1)  # Prevent tight loop on errors

# Start the email processing worker
email_worker = Thread(target=process_email_queue, daemon=True)
email_worker.start()

def queue_email(from_email, to_email, subject, message):
    """Queue an email for processing and return immediately"""
    email_id = str(uuid.uuid4())
    email_data = (email_id, from_email, to_email, subject, message)
    email_queue.put(email_data)
    email_status[email_id] = {"status": "queued", "message": "Email queued for processing"}
    return email_id

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            # Queue the email and get its ID
            email_id = queue_email(
                form.from_email.data,
                form.to_email.data,
                form.subject.data,
                form.message.data
            )
            
            flash('Email queued for sending! Check status at /status/' + email_id, 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            logger.error(f"General error: {str(e)}")
            flash(f'Error queueing email: {str(e)}', 'error')
    
    return render_template('index.html', form=form)

@app.route('/status/<email_id>', methods=['GET'])
def check_status(email_id):
    """Check the status of a queued email"""
    if email_id not in email_status:
        return jsonify({"error": "Email ID not found"}), 404
    return jsonify(email_status[email_id])

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000) 