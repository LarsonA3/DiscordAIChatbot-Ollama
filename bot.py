import os
import re
from collections import deque

import discord
import ollama
from dotenv import load_dotenv
from requests.exceptions import ConnectionError as ReqConnectionError



# ---------------------------------------------------------------------------
#  Setup & config
# ---------------------------------------------------------------------------


load_dotenv()

# OVERRIDE
os.environ['OLLAMA_HOST'] = 'http://127.0.0.1:11434'

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OLLAMA_ENDPOINT = os.getenv("OLLAMA_HOST")
desired_model = os.getenv("OLLAMA_MODEL")
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

print(f"OLLAMA_ENDPOINT is set to: {OLLAMA_ENDPOINT}")

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set. Export it or place it in a .env file.")



# ---------------------------------------------------------------------------
#  Initialise Ollama & Discord
# ---------------------------------------------------------------------------
ollama_client = ollama.Client(host=OLLAMA_ENDPOINT) # Initialize AFTER setting the env var

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

user_messages: dict[int, deque[str]] = {}




# ---------------------------------------------------------------------------
#  Helper func.
# ---------------------------------------------------------------------------

def generate_response(user_id: int, user_message: str) -> str:
    """Send the conversation to Ollama and return Krypt's reply."""

    history = list(user_messages.get(user_id, []))[-2:]

    character_description = (
        "Insert description of character HERE" 
    )

    conversation = [
        {"role": "user", "content": "You are a discord user named Krypt.\n" + character_description}
    ]

    for msg in history:
        conversation.append({"role": "user", "content": msg})

    conversation.append({"role": "user", "content": user_message})

    try:
        reply = ollama_client.chat(model=desired_model, messages=conversation)
        return reply["message"]["content"]
    except (ReqConnectionError, ConnectionError):
        return "couldn't find ollama"
    except Exception as exc:
        print(f"[ERROR] Unexpected error from Ollama: {exc}")
        return "Sorry, we couldn't think of a response right now."


def split_message(text: str, max_len: int = 2000) -> list[str]:
    return [text[i:i + max_len] for i in range(0, len(text), max_len)]


def remove_thinking_sections(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()



# ---------------------------------------------------------------------------
#  Discord event hooks
# ---------------------------------------------------------------------------
@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print(f"Listening in channel {TARGET_CHANNEL_ID} – Ctrl‑C to quit")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.channel.id != TARGET_CHANNEL_ID or client.user not in message.mentions:
        return

    cleaned = (
        message.content.replace(f"<@!{client.user.id}>", "")
        .replace(f"<@{client.user.id}>", "")
        .strip()
    )

    if message.author.id not in user_messages:
        user_messages[message.author.id] = deque(maxlen=4)
    user_messages[message.author.id].append(cleaned)

    raw_reply = generate_response(message.author.id, cleaned)
    raw_reply = remove_thinking_sections(raw_reply)

    for chunk in split_message(raw_reply):
        await message.channel.send(chunk)



# ---------------------------------------------------------------------------
#  Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
