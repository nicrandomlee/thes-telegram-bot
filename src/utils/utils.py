from datetime import date

def get_todays_date():
    """
    Returns date in DD/MM/YYYY format
    """
    return date.today().strftime("%d/%m/%Y")
