import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")


def get_currency_rates(amount, from_currency, to_currency):

    url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"

    response = requests.get(url)

    if response.status_code != 200:
        return {
            "error": "Currency API request failed"
        }

    data = response.json()

    if data["result"] != "success":
        return {
            "error": "Currency conversion failed"
        }

    rate = data["conversion_rates"].get(to_currency)

    if not rate:
        return {
            "error": "Target currency not found"
        }

    converted_amount = round(amount * rate, 2)

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount,
        "exchange_rate": rate,
        "converted_amount": converted_amount
    }