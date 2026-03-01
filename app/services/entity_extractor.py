import re

def extract_entities(text: str):
    text = text.strip()

    phone_pattern = r'\+?\d{10,15}'
   
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.-]+'
   

    url_pattern = r'https?://\S+|www\.\S+'
   
    upi_pattern = r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9]{2,}\b'
   
    amount_pattern = r'(?:₹|\$|Rs\.?|INR)\s?\d+(?:,\d{3})*(?:\.\d+)?'
   
    bank_pattern = r'\b\d{9,18}\b'
   
    ifsc_pattern = r'\b[A-Z]{4}0[A-Z0-9]{6}\b'
   
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