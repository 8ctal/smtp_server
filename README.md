# Simple SMTP Test Server

This project provides two ways to test email sending functionality:
- **Local development** using Docker Compose (MailHog as SMTP server)
- **Production/Cloud deployment** using Vercel and MailerSend (cloud SMTP relay)

## Prerequisites

- Docker
- Docker Compose
- (For cloud) Vercel account
- (For cloud) MailerSend account

## Local Development (MailHog + Docker Compose)

1. Clone this repository
2. Run the following command in the project directory:
   ```bash
   docker-compose up --build
   ```

3. The web interface will be available at http://localhost:3000
4. The MailHog web interface will be available at http://localhost:8025

### Usage (Local)

1. Open your web browser and navigate to http://localhost:3000
2. Fill in the email form:
   - To: Enter any email address (for testing)
   - Subject: Enter the email subject
   - Message: Enter your email message
3. Click "Send Email" to send the message
4. To view the sent email:
   - Open http://localhost:8025 in your web browser
   - You'll see all sent emails in the MailHog interface

**Notes:**
- This is a basic setup for testing purposes only
- No authentication is required
- All emails are caught by MailHog and can be viewed in its web interface
- This setup is perfect for development and testing
- No emails will actually be delivered to real email addresses

---

## Cloud Deployment (Vercel + MailerSend)

This method allows you to deploy the app to the cloud and send real emails using [MailerSend](https://mailersend.com/).

### Prerequisites
- [Vercel account](https://vercel.com/)
- [MailerSend account](https://mailersend.com/)
- A verified MailerSend domain and SMTP credentials

### Setup & Deployment

1. **Configure Environment Variables**
   - In your Vercel project settings, add the following environment variables:
     - `MAILERSEND_SMTP_USERNAME` (from MailerSend SMTP user)
     - `MAILERSEND_SMTP_PASSWORD` (from MailerSend SMTP user)
     - `MAILERSEND_DOMAIN` (your MailerSend domain, e.g. `yourdomain.mlsender.net`)
     - `SECRET_KEY` (any random string for Flask session security)

2. **Deploy to Vercel**
   - Push your code to your Git repository (GitHub, GitLab, etc.)
   - Import the project into Vercel and deploy
   - The web interface will be available at your Vercel deployment URL

### Usage (Cloud)

1. Open your deployed Vercel app in the browser
2. Fill in the email form:
   - Recipient Email: Enter the destination email address
   - Subject: Enter the email subject
   - Message: Enter your email message
3. Click "Send Email" to send the message
4. The recipient will receive the email in their inbox (check spam if not visible)

**Notes:**
- This method uses MailerSend's SMTP relay to send real emails
- Make sure your MailerSend domain is verified and SMTP user is active
- For production, secure your environment variables and Flask secret key

---

## Troubleshooting

If you encounter any issues:

1. Make sure ports 1025, 8025, and 3000 are not in use by other applications (for local MailHog setup)
2. Check the Docker logs for any error messages:
   ```bash
   docker-compose logs
   ```
3. Ensure your firewall allows connections to these ports
4. For Vercel/MailerSend, check your environment variables and MailerSend SMTP credentials
5. Review Vercel deployment logs for errors

## Security Notice

This setup is for testing and demonstration purposes only. For production use, ensure you implement proper security measures and never expose sensitive credentials in your codebase. 