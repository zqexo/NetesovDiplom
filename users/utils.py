from smsaero import SmsAero

from netesovdiplom.settings import SMS_AERO_API_KEY, SMS_AERO_EMAIL

SMSAERO_EMAIL = SMS_AERO_EMAIL
SMSAERO_API_KEY = SMS_AERO_API_KEY


def send_sms(phone: int, message: str) -> dict:
    api = SmsAero(SMSAERO_EMAIL, SMSAERO_API_KEY)
    return api.send_sms(phone, message)
