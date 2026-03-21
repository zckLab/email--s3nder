import smtplib
import os
import random
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple, Optional

# Ensure paths are relative to this script, not the working directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Try to load dotenv, ignore if not found (standard library fallback)
try:
    from dotenv import load_dotenv # type: ignore
    # Force loading example.env as requested
    load_dotenv(os.path.join(SCRIPT_DIR, 'example.env'))
except ImportError:
    pass

# Standard library fallback for loading simple env files if dotenv is missing
def manual_load_env(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

if 'EMAIL_USER' not in os.environ:
    manual_load_env(os.path.join(SCRIPT_DIR, 'example.env'))

SUPPORTED_LANGUAGES = [
    "pt", "en", "es", "pl", "it", "de", "ru", "fr", "nl", "sv", 
    "no", "da", "fi", "tr", "zh", "ja", "ko", "ar", "hi"
]

def parse_spintax(text: str) -> str:
    """Parses spin-tax in the format {option1|option2|option3}."""
    def replace_spin(match):
        options = match.group(1).split("|")
        return random.choice(options)
    return re.sub(r"\{([^{}]*\|[^{}]*)\}", replace_spin, text)

def validate_email(email: str) -> bool:
    """Simple check for @ in email."""
    return "@" in email

def validate_rating(rating: str) -> bool:
    """Validates rating format: integer (1-5) or decimal (0.0-5.0)."""
    return bool(re.match(r"^[0-5](\.\d)?$", rating))

def get_template_path(lang: str) -> str:
    """Returns the path for the specific language template or default."""
    lang_path = os.path.join(SCRIPT_DIR, "languages", f"PROMPTemail_{lang}.md")
    if os.path.exists(lang_path):
        return lang_path
    default_lang_path = os.path.join(SCRIPT_DIR, "languages", "PROMPTemail.md")
    if os.path.exists(default_lang_path):
        return default_lang_path
    return os.path.join(SCRIPT_DIR, "PROMPTemail.md")

def parse_template(lang: str, company_name: str, city: str, service_type: str, rating: str, reviews: str, sender_name: str = "", sender_occupation: str = "", sender_portfolio: str = "") -> Tuple[Optional[str], Optional[str]]:
    """Reads the template and replaces placeholders with provided data."""
    template_path = get_template_path(lang)
    if not os.path.exists(template_path):
        print(f"Error: Template file {template_path} not found.")
        return None, None

    with open(template_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if not lines:
        return None, None

    subject: str = "Quick idea"
    body_lines: List[str] = []
    first_line = lines[0].strip()
    if ":" in first_line or "：" in first_line:
        sep = ":" if ":" in first_line else "："
        subject = first_line.split(sep, 1)[1].strip()
        body_lines = lines[1:]  # type: ignore
    else:
        body_lines = lines
    body: str = "".join(body_lines).strip()

    placeholders = {
        "{{company_name}}": company_name,
        "{{city}}": city,
        "{{service_type}}": service_type,
        "{{rating}}": rating,
        "{{reviews}}": reviews
    }
    for key, value in placeholders.items():
        subject = subject.replace(key, value)
        body = body.replace(key, value)

    # Replace signature placeholders with user-provided sender info
    signature_placeholders = {
        "{Name}": sender_name,
        "{Occupation}": sender_occupation,
        "{WebSite/Portfolio}": sender_portfolio
    }
    for key, value in signature_placeholders.items():
        body = body.replace(key, value)

    subject = parse_spintax(subject)
    body = parse_spintax(body)
    return subject, body

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Sends the email via Gmail SMTP server."""
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")
    if not sender_email or not sender_password:
        print("Error: EMAIL_USER or EMAIL_PASS not configured in example.env file.")
        return False

    msg = MIMEMultipart()
    msg["From"] = str(sender_email)
    msg["To"] = to_email
    msg["Subject"] = str(subject)
    msg.attach(MIMEText(str(body), "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(str(sender_email), str(sender_password))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def show_language_help():
    print("\nSupported Languages:")
    for i in range(0, len(SUPPORTED_LANGUAGES), 2):
        row = SUPPORTED_LANGUAGES[i:i+2]  # type: ignore
        print("  " + "    ".join(f"{lang:<4}" for lang in row))
    print("")

def main():
    splash = r"""
                            .
                          A       ;
                |   ,--,-/ \---,-/|  ,
               _|\,'. /|      /|   `/|-.
           \`.'    /|      ,            `;.
          ,'\   A     A         A   A _ /| `.;
        ,/  _              A       _  / _   /|  ;
       /\  / \   ,  ,           A  /    /     `/|
      /_| | _ \         ,     ,             ,/  \
     // | |/ `.\  ,-      ,       ,   ,/ ,/      \/
     / @| |@  / /'   \  \      ,              >  /|    ,--.
    |\_/   \_/ /      |  |           ,  ,/        \  ./' __:..
    |  __ __  |       |  | .--.  ,         >  >   |-'   /     `
  ,/| /  '  \ |       |  |     \      ,           |    /
 /  |<--.__,->|       |  | .    `.        >  >    /   (
/_,' \\  ^  /  \     /  /   `.    >--            /^\   |
      \\___/    \   /  /      \__'     \   \   \/   \  |
       `.   |/          ,  ,                  /`\    \  )
         \  '  |/    ,       V    \          /        `-\
          `|/  '  V      V           \    \.'            \_
           '`-.       V       V        \./'\
               `|/-.      \ /   \ /,---`\         Z.KLIRT
                /   `._____V_____V'
                           '     '

    """
    print(splash)
    print("--- S3NDER ---")
    
    # Sender Credentials
    print("\n--- Your Credentials ---")
    sender_name = input("Your Name: ").strip()
    sender_occupation = input("Your Occupation: ").strip()
    sender_portfolio = input("Your Portfolio/Website: ").strip()
    print(f"Signature: {sender_name} | {sender_occupation} | {sender_portfolio}")

    # Language Selection
    while True:
        lang_input = input("\nSelect Email Language: ").strip().lower()
        if lang_input == "language --help":
            show_language_help()
            continue
        if lang_input in SUPPORTED_LANGUAGES:
            selected_lang = lang_input
            break
        print(f"Error: '{lang_input}' is not a valid language. Type 'language --help' for list.")

    while True:
        try:
            num_emails_input = input("How many companies do you want to email? ").strip()
            num_emails = int(num_emails_input)
            break
        except ValueError:
            print("Invalid number.")

    companies = []
    for i in range(num_emails):
        print(f"\n--- Company {i+1} of {num_emails} ---")
        
        while True:
            company_email = input("Company Email: ").strip()
            if validate_email(company_email):
                break
            print("Invalid email format.")

        company_name = input("Company Name: ").strip().title()
        city = input("City: ").strip().title()
        service_type = input("Service Type: ").strip().title()
        
        while True:
            rating = input("Rating (e.g., 4.8): ").strip()
            if validate_rating(rating):
                break
            print("Invalid rating format.")

        reviews = input("Number of Reviews: ").strip()
        
        companies.append({
            "email": company_email,
            "name": company_name,
            "city": city,
            "service_type": service_type,
            "rating": rating,
            "reviews": reviews
        })

    # Sending Loop
    print("\n" + "="*40)
    print("STARTING EMAIL SENDING PROCESS")
    print(f"Language: {selected_lang.upper()} | Companies: {len(companies)}")
    print("="*40)
    
    counts: dict[str, int] = {"sent": 0, "failed": 0}
    
    for i, company in enumerate(companies):
        print(f"\n[{i+1}/{len(companies)}] {company['name']} → {company['email']}")
        
        subject, body = parse_template(
            selected_lang, 
            company["name"], 
            company["city"], 
            company["service_type"], 
            company["rating"], 
            company["reviews"],
            sender_name,
            sender_occupation,
            sender_portfolio
        )

        if not subject or not body:
            print(f"  ⚠️ ERROR: Could not generate template for {company['name']}")
            counts["failed"] += 1
            continue
        
        subject = str(subject)
        body = str(body)
        
        # Manual mode: show preview and ask
        print(f"\n  Subject: {subject}")
        print("  " + "-" * 30)
        preview = body[:200]  # type: ignore
        print("  " + preview.replace("\n", "\n  ") + "...")
        print("  " + "-" * 30)
        
        confirm = input(f"\n  Send to {company['email']}? (y/n): ").lower().strip()
        if confirm != 'y':
            print(f"  ⏩ SKIPPED")
            continue
        
        print(f"  Sending email...")
        if send_email(company["email"], subject, body):
            print(f"  ✅ SENT!")
            counts["sent"] += 1
        else:
            print(f"  ❌ FAILED!")
            counts["failed"] += 1
    
    print("\n" + "="*40)
    print(f"COMPLETED! Sent: {counts['sent']} | Failed: {counts['failed']}")
    print("="*40)

if __name__ == "__main__":
    main()
