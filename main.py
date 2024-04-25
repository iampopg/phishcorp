import imaplib
import email
import socket

# IMAP server credentials
IMAP_SERVER = 'imap.gmail.com'
USERNAME = 'cailbank.mail@gmail.com'
PASSWORD = 'zoqyzbftcccgjogl'

# Function to resolve IP address from domain
def resolve_ip(domain):
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror:
        return None

# Connect to the IMAP server
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(USERNAME, PASSWORD)

# Load processed email IDs from file
try:
    with open('processed_ids.txt', 'r') as f:
        processed_ids = set(f.read().splitlines())
except FileNotFoundError:
    processed_ids = set()

# Select the mailbox (e.g., 'INBOX')
mail.select('INBOX')

# Search for all unseen emails
status, email_ids = mail.search(None, 'SEEN')

if status == 'OK':
    # Iterate through each email
    for email_id in email_ids[0].split():
        # Check if the email has already been processed
        if email_id in processed_ids:
            continue
        
        # Fetch the email
        status, email_data = mail.fetch(email_id, '(RFC822)')
        if status == 'OK':
            raw_email = email_data[0][1]
            # Parse the raw email
            msg = email.message_from_bytes(raw_email)
            # Extract email content
            sender = msg['From']
            receiver = msg['To']
            subject = msg['Subject']
            date = msg['Date']
            # Extract domain and name of sender
            sender_name, sender_email = email.utils.parseaddr(sender)
            sender_domain = sender_email.split('@')[-1]
            sender_ip = resolve_ip(sender_domain)
            receiver_name, receiver_email = email.utils.parseaddr(receiver)
            receiver_domain = receiver_email.split('@')[-1]
            # Iterate through email parts
            content = ""
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    # Extract email body
                    email_body = part.get_payload(decode=True).decode()
                    content += email_body
            # Print email details
            print("Email ID:", email_id)
            print("Sender Name:", sender_name)
            print("Sender Email:", sender_email)
            print("Sender Domain:", sender_domain)
            print("Sender IP:", sender_ip)
            print("Receiver Name:", receiver_name)
            print("Receiver Email:", receiver_email)
            print("Receiver Domain:", receiver_domain)
            print("Subject:", subject)
            print("Date:", date)
            print("Content:", content)
        
        # Mark the email as seen
        mail.store(email_id, '+FLAGS', '\Seen')
        # Add the email ID to the set of processed IDs and save to file
        processed_ids.add(email_id)
        with open('processed_ids.txt', 'a') as f:
            f.write(str(email_id) + '\n')

# Close the connection
mail.close()
mail.logout()
