import re

def extract_entities(text: str):
    text = text.strip()

    # 📞 Phone numbers (India + International support)
    phone_pattern = r'\+?\d{10,15}'
   
    # 📧 Emails
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
   
    # 🌐 URLs
    url_pattern = r'https?://\S+|www\.\S+'
   
    # 🏦 UPI IDs (exclude real emails later)
    upi_pattern = r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9]{2,}\b'
   
    # 💰 Amounts (₹, $, Rs, INR)
    amount_pattern = r'(?:₹|\$|Rs\.?|INR)\s?\d+(?:,\d{3})*(?:\.\d+)?'
   
    # 🏦 Bank Account (9–18 digits)
    bank_pattern = r'\b\d{9,18}\b'
   
    # 🏦 IFSC Code (Indian format)
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
   
    # 🌍 IP Address
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'

    phones = re.findall(phone_pattern, text)
    emails = re.findall(email_pattern, text)
    urls = re.findall(url_pattern, text)
    upi_ids = re.findall(upi_pattern, text)
    amounts = re.findall(amount_pattern, text)
    bank_accounts = re.findall(bank_pattern, text)
    ifsc_codes = re.findall(ifsc_pattern, text)
    ip_addresses = re.findall(ip_pattern, text)

    upi_ids = [u for u in upi_ids if u not in emails]

    return {
        "phones": list(set(phones)),
        "emails": list(set(emails)),
        "urls": list(set(urls)),
        "upi_ids": list(set(upi_ids)),
        "amounts": list(set(amounts)),
        "bank_accounts": list(set(bank_accounts)),
        "ifsc_codes": list(set(ifsc_codes)),
        "ip_addresses": list(set(ip_addresses))
    }