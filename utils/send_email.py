import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_notification(subject="Execution Failed!", body="Error occurred during the execution file not found in container.",to_mail=""):
    """
    Send email notification for execution failures or other alerts
    
    Args:
        subject (str): Email subject line
        body (str): Email body content
    """
    
    # SMTP server settings
    smtp_server = 'smtp.gmail.com'  # For Gmail; use your SMTP server if different
    smtp_port = 587  # TLS port
    
    # Email credentials - Replace with your actual credentials
    username = ''  # Your Gmail username (email address)
    password = ''  # Replace with the app password generated from Gmail
    from_addr = ''  # Sender email address (usually same as username)
    to_addrs = [to_mail]  # Recipient email addresses
    
    # Validate that credentials are provided
    if not username or not password or not from_addr:
        breakpoint()
        print("Error: Please provide username, password, and from_addr")
        return False
    breakpoint()
    # Create the multipart email message
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = ', '.join(to_addrs)
    msg['Subject'] = subject
    
    # Email body content
    msg.attach(MIMEText(body, 'plain'))
    
    server = None
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.ehlo()
        
        # Start TLS encryption
        server.starttls()
        server.ehlo()
        
        # Login with app password
        server.login(username, password)
        
        # Send the email
        server.sendmail(from_addr, to_addrs, msg.as_string())
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False
        
    finally:
        # Disconnect from the SMTP server
        if server is not None:
            try:
                server.quit()
            except Exception as e:
                print(f"Error closing SMTP connection: {e}")

def send_success_notification():
    """Send a success notification email"""
    subject = "Execution Successful!"
    body = "The process has completed successfully."
    return send_email_notification(subject, body)

def send_failure_notification(error_message="Unknown error occurred"):
    """Send a failure notification email with custom error message"""
    subject = "Execution Failed!"
    body = f"Error occurred during execution: {error_message}"
    return send_email_notification(subject, body)

# Example usage
# if __name__ == "__main__":
    # Test the email function
    # Make sure to fill in the credentials above before running
    
    # Example 1: Send default failure notification
    # send_email_notification()
    
    # Example 2: Send custom notification
    # send_email_notification(
    #     subject="Custom Alert", 
    #     body="This is a custom notification message."
    # )
    
    # Example 3: Send success notification
    # send_success_notification()
    
    # Example 4: Send failure notification with custom error
    # send_failure_notification("File not found in container")