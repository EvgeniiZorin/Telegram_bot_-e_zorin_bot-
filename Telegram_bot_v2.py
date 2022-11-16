import telebot
import config
import random
from telebot import types
from pyowm.owm import OWM
import requests
import time
import datetime
import csv
from typing import List, Dict
import time
import pandas as pd
import os


telebot_token = os.environ.get('TELEBOT_API')
bot = telebot.TeleBot(telebot_token)
owm_api = os.environ.get('OWM_API')
owm = OWM(owm_api)
mgr = owm.weather_manager()


# Handle incoming /start, /help messages
@bot.message_handler(commands=['start', 'help'])
def welcome(message):
	# Buttons
	markup = types.ReplyKeyboardMarkup()
	button_quotes = types.KeyboardButton('/quote')
	button_weather = types.KeyboardButton('/weather')
	button_help = types.KeyboardButton('/help')
	markup.add(button_quotes, button_weather, button_help)
	# bot.send_message(message.chat.id, 'Welcome, dear user! Commands:', reply_markup=markup)
	bot.send_message(message.chat.id, """Welcome, dear user! 
	
	Below are some of the commands that you can call:

	/help - print this help message
	/quote - print a randomly-selected motivational quote
	/weather - print a forecast for a specific city
	""", reply_markup=markup)



# Respond to the button commands
@bot.message_handler(content_types=['text'])
def reply(message):
	if message.text == '/quote':
		# bot.send_message(message.chat.id, 'here is a quote for you')
		df = pd.read_csv('https://raw.githubusercontent.com/EvgeniiZorin/FILES_DATABASE/main/quotes.csv')
		quote = df.sample(1)
		quote_author, quote_text = list(quote['Author'])[0], list(quote['Quote'])[0]
		# print(f"{quote_text} -by- {quote_author}")
		bot.send_message(message.chat.id, f'"{quote_text}"\n - {quote_author}')
	if message.text == '/weather':
		message1 = bot.send_message(message.chat.id, "For which city would you like to know the weather forecast?")
		bot.register_next_step_handler(message1, process_name_step)
def process_name_step(message):
	bot.send_message(message.chat.id, f"You have typed: {message.text}")
	from pyowm.owm import OWM
	from geopy.geocoders import Nominatim
	# Example input
	# city_country = 'Toluca, Mexico'
	# Example exception (doesn't work for some reason)
	# city_country = 'Moscow, Russia'
	city_country = message.text

	owm = OWM('245ade4c3a60e993b30476c52868eacc')
	mgr = owm.weather_manager()
	# dir(mgr)

	observation = mgr.weather_at_place(city_country)
	temp_dict = observation.weather.temperature('celsius')



	# Initialize Nominatim API
	geolocator = Nominatim(user_agent="MyApp")
	location = geolocator.geocode(city_country)
	# print(location)
	# print(f"{location.latitude}, {location.longitude}")

	failure = 0
	try:
		one_call = mgr.one_call(location.latitude, location.longitude)
	except:
		failure = 1


	output = ''
	# print(f"Weather at location: \n - Current: {temp_dict['temp']}\n - Min today: {temp_dict['temp_min']}\n - Max today: {temp_dict['temp_max']}")
	# print(f"Weather in {location}: \n - Current: {temp_dict['temp']}")
	output += f"Weather in {location}: \n - Current: {temp_dict['temp']}\n"
	if failure == 0:
		for i in range(2, 11, 2):
			# print(f" - In {i} hours: {one_call.forecast_hourly[i].temperature('celsius')['temp']}")
			output += f" - In {i} hours: {one_call.forecast_hourly[i].temperature('celsius')['temp']}\n"
	else:
		# print(' - Failed to get forecast for this location.')
		output += " - Failed to get hourly forecast for this location"
	bot.send_message(message.chat.id, output)


def run():
	bot.polling(none_stop=True)
	# bot.infinity_polling()

# To run the program
if __name__ == '__main__':
	run()

