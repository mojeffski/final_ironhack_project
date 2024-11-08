import imaplib
import email
from bs4 import BeautifulSoup
import sqlite3
import datetime
import logging

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('config.env')

# Setup basic configuration for logging
logging.basicConfig(filename='tris_email_scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_date(email_date):
    parsed_date = email.utils.parsedate_to_datetime(email_date)
    formatted_date = parsed_date.strftime('%Y-%m-%d')
    end_date = (parsed_date + datetime.timedelta(weeks=5)).strftime('%Y-%m-%d')
    return formatted_date, end_date

# Database setup
conn = sqlite3.connect('..data/scraper_data.db')

cur = conn.cursor()

# Create tables if they don't exist
cur.execute('''
CREATE TABLE IF NOT EXISTS tris_scraper_stack (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tris_id TEXT UNIQUE,
    status TEXT DEFAULT 'not scraped',
    message_number TEXT,
    email_from TEXT,
    email_date TEXT,
    end_date TEXT,
    url TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS log_scraper (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_datetime DATETIME DEFAULT CURRENT_TIMESTAMP,
    new_cases_count INTEGER
)
''')

# Retrieve the latest email_date from the database
cur.execute('SELECT MAX(email_date) FROM tris_scraper_stack')
row = cur.fetchone()
latest_email_date = row[0]

conn.commit()

# If there is a latest date in the database, format it for the IMAP search query
if latest_email_date is not None:
    date_for_imap = datetime.datetime.strptime(latest_email_date, '%Y-%m-%d').strftime('%d-%b-%Y')
    search_criterion = f'(SINCE {date_for_imap})'
else:
    # If there are no entries in the database yet, don't restrict the search by date
    search_criterion = 'ALL'

# Access the environment variables
imap_server = os.getenv('IMAP_SERVER')
email_address = os.getenv('EMAIL_ADDRESS')
email_password = os.getenv('EMAIL_PASSWORD')
email_selector = os.getenv('EMAIL_SELECTOR')

# IMAP setup
imap = imaplib.IMAP4_SSL(imap_server)
imap.login(email_address, email_password)

# Select the email folder
imap.select(email_selector)

print("Logged in and selected the folder successfully.")

_, msgnums = imap.search(None, f'(FROM "EU CORPORATE NOTIFICATION" SUBJECT "New notification" {search_criterion})')

new_cases = 0

log_tris_id = [] 


for msgnum in msgnums[0].split():
    _, data = imap.fetch(msgnum, "(RFC822)")
    message = email.message_from_bytes(data[0][1])
    tris_id = message.get('Subject').split('TRIS - New notification ')[1] if len(message.get('Subject').split('TRIS - New notification ')) > 1 else None
    email_date, end_date = process_date(message.get('Date'))


    if tris_id is not None:
        for part in message.walk():
            if part.get_content_type() == "text/html":
                html_content = part.get_payload(decode=True)
                soup = BeautifulSoup(html_content, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith("https://technical-regulation-information-system.ec.europa.eu/en/notification/") and href.split("/")[-1].isdigit():
                        insert_data = (tris_id, msgnum.decode(), message.get('From'), email_date, end_date, href)
                        try:
                            cur.execute('INSERT OR IGNORE INTO tris_scraper_stack (tris_id, message_number, email_from, email_date, end_date, url) VALUES (?, ?, ?, ?, ?, ?)', insert_data)
                            if cur.rowcount > 0:
                                new_cases += 1
                                log_tris_id.append(tris_id)
                            conn.commit()
                        except Exception as e:
                            print(f"An error occurred: {e}")


# Log the run
cur.execute('INSERT INTO log_scraper (new_cases_count) VALUES (?)', (new_cases,))
conn.commit()

logging.info(f"Script executed. New cases scraped: {new_cases}: {log_tris_id}")

imap.close()
conn.close()

print(f"Scraping complete. Log updated. found: {new_cases} new cases")