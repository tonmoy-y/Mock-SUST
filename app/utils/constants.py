import re

PHISHING_KEYWORDS = [
    "otp", "pin", "password", "scam", "called asking", "fake", "hacked", "phishing"
]

WRONG_TRANSFER_KEYWORDS = [
    "wrong number", "wrong recipient", "sent by mistake", "wrong account", "wrong person", "wrong transfer"
]

PAYMENT_FAILED_KEYWORDS = [
    "failed", "deducted", "balance deducted", "did not go through", "error", "unsuccessful"
]

REFUND_KEYWORDS = [
    "refund", "money back", "return my money", "cancel my last transaction"
]

# Safety keywords to avoid in summaries
SENSITIVE_DATA_KEYWORDS = [
    "pin", "otp", "password", "card number"
]
