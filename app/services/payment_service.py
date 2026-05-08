from datetime import datetime


def verify_payment(card_number, cvv, expiry_date):

    if len(card_number) != 16:
        return False

    if len(cvv) != 3:
        return False

    try:
        expiry = datetime.strptime(expiry_date, "%m/%y")

        if expiry < datetime.now():
            return False

    except:
        return False

    return True