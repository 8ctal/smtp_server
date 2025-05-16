# Simple SMTP Test Server

This is a simple SMTP server setup with a web interface for testing email sending functionality. It uses Docker Compose to set up both the SMTP server (MailHog) and a web interface.

## Prerequisites

- Docker
- Docker Compose

## Setup and Running

1. Clone this repository
2. Run the following command in the project directory:
   ```bash
   docker-compose up --build
   ```

3. The web interface will be available at http://localhost:3000
4. The MailHog web interface will be available at http://localhost:8025

## Usage

1. Open your web browser and navigate to http://localhost:3000
2. Fill in the email form:
   - To: Enter any email address (for testing)
   - Subject: Enter the email subject
   - Message: Enter your email message
3. Click "Send Email" to send the message
4. To view the sent email:
   - Open http://localhost:8025 in your web browser
   - You'll see all sent emails in the MailHog interface

## Notes

- This is a basic setup for testing purposes only
- No authentication is required
- All emails are caught by MailHog and can be viewed in its web interface
- This setup is perfect for development and testing
- No emails will actually be delivered to real email addresses

## Troubleshooting

If you encounter any issues:

1. Make sure ports 1025, 8025, and 3000 are not in use by other applications
2. Check the Docker logs for any error messages:
   ```bash
   docker-compose logs
   ```
3. Ensure your firewall allows connections to these ports

## Security Notice

This setup is for testing purposes only and should not be used in production without proper security measures. 