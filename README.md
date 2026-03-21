# S3NDER

![Terminal Preview](docs/terminal.png)

A lightweight, manual email sender script designed for outreach campaigns. It allows you to select from multiple languages, input company details directly in the terminal, preview generated templates with your personalized signature, and send emails securely via Gmail SMTP.

## Features

- **Multi-language Support**: 19 supported languages out of the box (English, Portuguese, Spanish, French, German, Japanese, Arabic, and more).
- **Spintax Support**: Built-in support for `{option1|option2}` variations in templates to keep your emails unique.
- **Dynamic Placeholders**: Automatically replaces company names, cities, ratings, reviews, and your personal signature in the templates.
- **Manual Control**: Preview every single email subject and body before confirming whether to send or skip it.

---

## 🚀 Installation & Setup

### 1. Prerequisites
Make sure you have **Python 3.8+** installed on your system.
You can download it from [python.org](https://www.python.org/).

### 2. Clone or Download the Project
Ensure all files (`s3nder.py`, `example.env`, `requirements.txt`, and the `languages/` folder) are in the same directory.

### 3. Install Dependencies
S3NDER only requires one external library to handle environment variables safely. Run the following command in your terminal:

```bash
pip install -r requirements.txt
```

### 4. Configure Your Gmail Credentials
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
The script will first ask for your personal details. These will be automatically inserted at the bottom of every template using the `{Name} | {Occupation} | {WebSite/Portfolio}` format.
```text
Your Name: John Doe
Your Occupation: Web Developer
Your Portfolio/Website: johndoe.com
```

### 2. Select a Language 
Type the language code you want to use for this batch of emails (e.g., `en`, `pt`, `es`).

**Not sure which languages are supported?** 
Type `language --help` when prompted to see the full list of available language codes:
```text
Select Email Language: language --help

Supported Languages:
  pt      en
  es      pl
  it      de
  ...
```

### 3. Input Company Data
The script will ask how many companies you want to email. For each company, you will need to provide:
- **Company Email**
- **Company Name**
- **City**
- **Service Type** (e.g., "Web Design", "Plumbing")
- **Rating** (e.g., "4.8")
- **Number of Reviews** (e.g., "120")

### 4. Preview and Send
Before anything is sent, S3NDER will show you a preview of the specific email generated for that company. 

```text
  Subject: Quick idea for Tech Solutions Inc.
  ------------------------------
  Hello,
  I found Tech Solutions Inc. while searching for Web Design...
  ------------------------------

  Send to info@techsolutions.com? (y/n): 
```
- Type `y` and press Enter to send the email.
- Type `n` and press Enter to skip this company and move to the next one.

At the end of the process, you will see a summary of how many emails were successfully sent and how many failed.
