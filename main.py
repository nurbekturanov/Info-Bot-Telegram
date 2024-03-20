import requests
import ssl
import certifi
import geopy
from geopy.geocoders import Nominatim
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import settings

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx

currency_url = f"https://cbu.uz/uz/arkhiv-kursov-valyut/json/"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [["Weather", "Currency"], ["Location"]]

    await update.message.reply_text(
        "👨‍🏫Hi, My name is Professor Bot. Choose a button to get information",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True),
    )


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Type /start command to use the bot!")


async def hande_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Weather":
        await update.message.reply_text(
            '⛅️You can get weather info by typing /weather for Tashkent, or "/weather Buxoro" for other region'
        )
    elif text == "Currency":
        await update.message.reply_text(
            "💸You can get USD to UZS rate by typing /USD command"
        )
    elif text == "Location":
        await update.message.reply_text(
            "📍You can know where you are, by typing /location command"
        )


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.split()

    if len(text) == 1:
        location = "Toshkent"
    else:
        location = text[1]

    api_key = "82c4e7ad571cc34ef96574e4dab80635"

    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        city = data["name"]
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]

        weather_text = f"Weather in {city}:\n\nDescription: {weather_description}\nTemperature: {temperature:.1f}C"
        await update.message.reply_text(weather_text)
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(
            f"🙅‍♀️Error: Unable to retrive weather informatioin for {location}. ({e})"
        )


async def command_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("/weather"):
        weather(update, context)


async def currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
    try:
        respone = requests.get(url)
        respone.raise_for_status()
        data = respone.json()
        rate = data[0]["Rate"]
        await update.message.reply_text(f"$1 = {rate} UZS")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"Something went wrong: {e}")


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [[KeyboardButton("Send Location", request_location=True)]]
    await update.message.reply_text(
        "Manzilingizni jo'nating!",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, resize_keyboard=True, one_time_keyboard=True
        ),
    )


async def location_define(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_location = update.message.location
    lat = user_location.latitude
    lon = user_location.longitude
    geolocator = Nominatim(user_agent="http/")
    location = geolocator.reverse(f"{lat}, {lon}")
    await update.message.reply_text(location.address)


def main() -> None:
    app = Application.builder().token(settings.BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("USD", currency))
    app.add_handler(CommandHandler("location", location))
    app.add_handler(MessageHandler(filters.LOCATION, location_define))
    app.add_handler(
        MessageHandler(
            filters.Regex("Weather")
            | filters.Regex("Currency")
            | filters.Regex("Location"),
            hande_message,
        )
    )
    app.add_handler(MessageHandler(filters.Regex("/weather"), command_message))
    app.add_handler(MessageHandler(filters.ALL, echo))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
