from datetime import date, datetime, timedelta
import re
import glob
import os

def extract_names_coming(text):
    coming_section = re.search(r'Coming 🧓 \(\d+👥\)(.*?)Not Coming', text, re.DOTALL)
    if coming_section:
        # Extract the content between "Coming" and "Not Coming"
        names_text = coming_section.group(1).strip()
        names = [name.strip() for name in names_text.split('\n') if name.strip()]
        return names
    else:
        return []

def extract_names_not_coming(text):
    not_coming_section = re.search(r'Not Coming 🥲 \(\d+👥\)\n([\s\S]*)', text)
    
    if not_coming_section:
        # Extract the content after "Not Coming"
        names_text = not_coming_section.group(1).strip()
        
        # Split the text into names and remove any empty entries
        names = re.findall(r'\S+(?:\s+\([^)]+\))?', names_text)
        
        return names
    else:
        return []

def get_todays_date():
    """
    Returns date in DD/MM/YYYY format
    """
    return date.today().strftime("%d-%m-%Y")

def get_next_saturday_date():
    today = datetime.now()
    days_ahead = (5 - today.weekday() + 7) % 7
    if days_ahead == 0:
        days_ahead = 7
    next_saturday = today + timedelta(days=days_ahead)
    return next_saturday.strftime("%d %b %Y")

def is_today_saturday():
    # Get the current UTC time and add 8 hours for GMT+8
    current_time = datetime.now()
    
    # Check if the current day is Saturday (where Monday is 0 and Sunday is 6)
    return current_time.weekday() == 5

def get_doc_filepath_from_folder(filepath):
    directory_contents = glob.glob(f'{filepath}/*')
    if len(directory_contents) > 0:
        file_path = directory_contents[0]
    else:
        file_path = ""

    return file_path

def delete_file_from_filepath(filepath):
    os.unlink(filepath)