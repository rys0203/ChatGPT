import os

import openai
import json
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=("GET", "POST"))
def index():
	return render_template("index.html")

@app.route("/pet_generator", methods=("GET", "POST"))
def pet_generator():
	if request.method == "POST":
		animal = request.form["animal"]
		response = openai.Completion.create(
			model="text-davinci-003",
			prompt=generate_prompt(animal),
			temperature=0.6,
		)
		return redirect(url_for("pet_generator", result=response.choices[0].text))

	result = request.args.get("result")
	return render_template("pet_generator.html", result=result)


def generate_prompt(animal):
	return """
			Suggest three names for an animal that is a superhero.
				Animal: Cat
				Names: Captain Sharpclaw, Agent Fluffball, The Incredible Feline
				Animal: Dog
				Names: Ruff the Protector, Wonder Canine, Sir Barks-a-Lot
				Animal: {}
				Names:
	""".format(
		animal.capitalize()
	)

@app.route("/chat_completions", methods=("GET", "POST"))
def chat_completions():
	if request.method == "POST":
		response = openai.ChatCompletion.create(
				model="gpt-3.5-turbo",
				messages=[
					{"role": "system", "content": "You are a helpful assistant."},
					{"role": "user", "content": "Who won the world series in 2020?"},
					{"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
					{"role": "user", "content": "Where was it played?"}
				]
			)
		print('response, ', response)
		return redirect(url_for("chat_completions", result=response.choices[0].message.content)) # type: ignore
	result = request.args.get("result")
	return render_template("chat_completions.html", result=result)

@app.route("/function_calling", methods=("GET", "POST"))
def function_calling():
	if request.method == "POST":
		# Step 1: send the conversation and available functions to GPT
		messages = [
			{"role": "user", "content": "What's the weather like in Boston?"}
		]
		functions = [
				{
					"name": "get_current_weather",
					"description": "Get the current weather in a given location",
					"parameters": {
						"type": "object",
						"properties": {
							"location": {
								"type": "string",
								"description": "The city and state, e.g. San Francisco, CA",
							},
							"unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
						},
						"required": ["location"],
					},
				}
			]
		response = openai.ChatCompletion.create(
			model="gpt-3.5-turbo-0613",
			messages=messages,
			functions=functions,
			function_call="auto",
		)
		response_message = response["choices"]["0"]["message"] # type: ignore
		# Step 2: check if GPT wanted to call a function
		if response_message.get("function_call"):
			# Step 3: call the function
			# Note: the JSON response may not always be valid; be sure to handle error
			available_functions = {
				"get_current_weather": get_current_weather,
			} # only one function in this example, but you can have multiple
			function_name = response_message["function_call"]["name"]
			function_to_call = available_functions[function_name]
			function_args = json.loads(response_message["function_call"]["arguments"])
			function_response = function_to_call(
				location=function_args.get("location"),
				unit=function_args.get("unit"),
			)

			# Step 4: send the info on the function call and function response to GPT
			messages.append(response_message) # extend conversation with assistant's reply
			messages.append(
				{
					"role": "function",
					"name": function_name,
					"content": function_response,
				}
			) # extend the conversation with function response
			second_response = openai.ChatCompletion.create(
				model="gpt-3.5-turbo-0613",
				messages=messages,
			) # get a new response from GPT where it can see the function response
			return redirect(url_for("function_calling", result=second_response)) # type: ignore
	result = request.args.get("result")
	return render_template("function_calling.html", result=result)

def get_current_weather(location, unit="fahrenheit"):
	"""Get the current weather in a given location"""
	weather_info = {
		"location": location,
		"temperature": "72",
		"unit": unit,
		"forecast": ["sunny", "windy"],
	}
	return json.dumps(weather_info)