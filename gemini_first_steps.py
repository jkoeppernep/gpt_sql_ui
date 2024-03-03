"""
gemini_first_steps.py
2024-03-03

Look at Google's quickstart guide: https://colab.research.google.com/github/google/generative-ai-docs/blob/main/site/en/tutorials/python_quickstart.ipynb

# Goal
Use Gemini Pro as replacement for OpenAI's GPT-3.5

# Steps
- Install Gemini Pro
- Create a Gemini Pro account and set API key as environment variable (https://makersuite.google.com/app/apikey)

"""
import pathlib
import textwrap
import json
import pathlib


import google.generativeai as genai

# readf json file api_key.json
api_key_file = pathlib.Path("api_key.json")

with open(api_key_file, "r") as f:
    api_key = json.load(f)

google_api_key = api_key["google-api-key"]

genai.configure(api_key=google_api_key)

# List models
for m in genai.list_models():
  if 'generateContent' in m.supported_generation_methods:
    print(m.name)

print("Done.")
