import os

import openai
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
    return redirect(url_for("chat_completions", result=response.choices[0].message.content))
  
  result = request.args.get("result")
  return render_template("chat_completions.html", result=result)
