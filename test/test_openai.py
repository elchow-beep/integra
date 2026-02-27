from dotenv import load_dotenv
import os
from openai import OpenAI

# Load your API key from .env
load_dotenv()

# Initialize the client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Send a test message
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "You are a warm, grounded psychedelic integration companion."
        },
        {
            "role": "user",
            "content": "I just had a profound experience and I'm trying to make sense of it. Where do I begin?"
        }
    ]
)

# Print the response
print(response.choices[0].message.content)