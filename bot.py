import os
import json
import base64
import gspread
import datetime
from dotenv import load_dotenv, find_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

load_dotenv(find_dotenv())

BOT_TOKEN = os.getenv("BOT_API_KEY")
SHEET_ID = os.getenv("GOOGLE_SHEETS_ID")
SHEET_NAME = "Data"

google_encoded_key = os.getenv("GOOGLE_CREDENTIALS")

google_encoded_key = str(google_encoded_key)[2:-1] # remove the first two chars and the last char in the key

google_credentials_dict=json.loads(base64.b64decode(google_encoded_key).decode('utf-8')) # decode

# print(google_credentials_dict['private_key_id'])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_credentials_dict, scope) 
client = gspread.authorize(credentials)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

async def start(update: Update, context: CallbackContext):
    """ Handles the /start command """
    await update.message.reply_text("Hello! Send me a 4-line message to log your transaction.")

async def log_transaction(update: Update, context: CallbackContext):
    """ Processes user messages and logs them into Google Sheets """
    text = update.message.text.strip()
    lines = text.split("\n")

    if len(lines) != 4:
        await update.message.reply_text("⚠️ Invalid format! Send a message in 4 lines:\n1️⃣ Description\n2️⃣ D (debit) / C (credit)\n3️⃣ Amount\n4️⃣ Category")
        return

    description = lines[0].strip()
    transaction_type = lines[1].strip().upper()
    amount = lines[2].strip()
    category = lines[3].strip()

    try:
        amount = float(amount)
    except ValueError:
        await update.message.reply_text("⚠️ Invalid amount! Please enter a numeric value.")
        return

    if transaction_type not in ["D", "C"]:
        await update.message.reply_text("⚠️ Invalid transaction type! Use 'D' for Debit and 'C' for Credit.")
        return

    now = datetime.datetime.now() # current date and time
    date = now.strftime("%d-%m-%Y") # getting current date only
    month = now.strftime("%B")  # making full month-name (eg: January)
    year = now.strftime("%Y") # getting the Year from datetime

    debit = amount if transaction_type == "D" else ""
    credit = amount if transaction_type == "C" else ""

    row = [date, month, year, description, category, debit, credit]

    sheet.append_row(row)

    await update.message.reply_text(f"✅ Transaction logged successfully!\n📌 {date} | {description} | {amount} | {category}")

def main():
    """ Runs the bot once when triggered """
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_transaction))
    
    app.run_polling(timeout=30)

if __name__ == "__main__":
    main()