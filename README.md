# S3NDER

![Terminal Preview](docs/terminal.png)

A fast, highly scalable manual email outreach script designed for niche-agnostic professionals. It generates outcome-focused cold emails in 19 languages using built-in A/B testing templates and spintax, letting you preview everything in your native terminal language before sending via Gmail.

## ✨ Features
- **Dynamic A/B Testing**: Randomly rotates between Direct, Empathetic, Provocative, and Neutral strategy templates per company to find what converts best.
- **19 Languages & Localized UI**: All templates and the terminal interface itself automatically translate to match your selected target language ( `pt`, `en`, `es`, `ja`, `ar`, `da`, `de`, `fi`, `fr`, `hi`, `it`, `ko`, `nl`, `no`, `pl`, `ru`, `sv`, `tr`, `zh`).
- **Outcome-Focused Spintax**: Built-in variables like `{{Strong_Point}}` and `{{Value_Hook}}` to focus on revenue leverage and authority, not just selling tools. 
- **Custom Mode**: Need to send a one-off custom email? Select `custom` as your language to type your email body directly in the terminal while still using dynamic variables!
- **Manual QA**: Review every generated email in the terminal before pressing send.

---

## 🚀 Installation & Setup

### 1. Requirements
- Python 3.8+

### 2. Get the Project
Clone the repository and install the requirements:

```bash
git clone https://github.com/zckLab/email--s3nder.git
cd email--s3nder
pip install -python-dotenv
```
*(Note: Uses standard libraries mostly, `python-dotenv` is recommended for managing secrets).*

### 3. Configure Your Gmail Credentials
To send emails, the script uses your Gmail account securely through an **App Password** (this keeps your real password safe).

1. Rename `example.env` to `.env`.
2. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
3. Ensure **2-Step Verification** is turned ON.
4. Go to [App Passwords](https://myaccount.google.com/apppasswords).
5. Open the app selector and choose "Mail". Open the device selector and choose "Windows Computer" (or your OS).
6. Click **Generate**.
7. Copy the 16-character password provided by Google.
8. Open the `.env` file and replace the placeholder credentials:

```env
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=xxxx xxxx xxxx xxxx
```

---

## 🛠️ Usage Guide

To start the program, open your terminal in the project folder and run:

```bash
python s3nder.py
```

### 1. Enter Your Details (Signature)
The script will first ask for your personal details for the `{Name} | {Occupation} | {WebSite/Portfolio}` signature format.
```text
Your Name: John Doe
Your Occupation: Strategic Consultant
Your Portfolio/Website: johndoe.com
```

### 2. Select a Language & UI
Type the language code you want to use (e.g., `en`, `pt`, `es`). The terminal UI will switch to this language automatically.

**Not sure which languages are supported?** 
Type `help` when prompted to see the full list of available 19 language codes:
```text
Select Language (e.g. pt, en, es) (or 'help' for list): help

Available Languages:
  pt    en    es    fr    de
  ...
```
*(Tip: Type `custom` here to write an ad-hoc email directly in the terminal!)*

### 3. Input Company Data
The script will ask how many companies you want to email. For each company, you need to provide data that will fill the dynamic templates:
- **Company Email**
- **Company Name**
- **City**
- **Their Industry/Service** 
- **Rating** (e.g., "4.8")
- **Number of Reviews**
- **Your Service/Offer** (This is the `{{Value_Hook}}`, e.g., "workflow automation" or "revenue scaling")

### 4. Preview and Send
S3NDER randomly selects a strategy template matching your language and fills it with spintax. It will show you a preview before anything is sent. 

```text
  Subject: Idea for Tech Solutions Inc.
  ------------------------------
  Hello,
  I saw the work you are doing at Tech Solutions Inc. and the quality of your strong online presence caught my attention.
  
  I work helping companies scale their authority and revenue...
  ------------------------------

  Send to info@techsolutions.com? (y/n): 
```
- Type `y` and press Enter to send the email.
- Type `n` and press Enter to skip this company and move to the next one.

At the end of the process, you will see a summary of how many emails were successfully sent versus failed.
