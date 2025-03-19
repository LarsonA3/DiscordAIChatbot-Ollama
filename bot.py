import discord
import ollama
import re

from collections import deque



##### SETUP #####

#change name to ollama model name
desiredModel = 'mistral-nemo' #mistral nemo is my recommendation, but you can replace this with whatever ollama model you want so long as it's installed properly on your system

#put discord bot token here
DISCORD_TOKEN = 'replace with token'

#put discord channel id here
target_channel_id = 123123234234

#NOTE THAT THERE IS MORE TO CHANGE BELOW, MOST IMPORTANTLY THE CHARACTER DESCRIPTION.
##################




#stored messages
user_messages = {}

#initialization
intents = discord.Intents.default()
intents.message_content = True  #required to read message content
client = discord.Client(intents=intents)

def generate_response(user_id, user_message):
    if user_id in user_messages:
        last_messages = list(user_messages[user_id])[-2:] # this saves last 2 user messages
    else:
        last_messages = []

    ###### PUT CHARACTER DESCRIPTION HERE ########
    character_description = """
    You are [insert name], a user on Discord. [Insert background here].
    
    [Insert other important info, such as chat examples, mannerisms, and bot instructions]

    """

    #plug in name here
    conversation = "You are a discord user named [name]\n" + character_description

    #adds last messages to context
    for msg in last_messages:
        conversation += f"\nUser: {msg}"

    #add newest message
    conversation += f"\nUser: {user_message}\nKrypt:"

    #gets response from the model
    try:
        response = ollama.chat(model=desiredModel, messages=[{'role': 'user', 'content': conversation}])
        return response['message']['content']
    except Exception as e:
        print(f"Error getting response from Ollama: {e}")
        return "Sorry, I couldn't think of a response right now."




def split_message(message, max_length=2000):
    """Split a long message into chunks of max_length."""
    chunks = [message[i:i + max_length] for i in range(0, len(message), max_length)]
    return chunks


def remove_thinking(message):
    """Removes <think>...</think> sections from the response."""
    return re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL).strip()

#when the bot is ready, do this
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

#when a message is received, do this
@client.event
async def on_message(message):
    #dont respond to bots own messages
    if message.author == client.user:
        return

    #debug info for terminal, not necessary but recommended to keep on
    print(f"Received message: {message.content} from {message.author.name} in channel {message.channel.id}")

    #checks for pings in the channel specified
    if message.channel.id == target_channel_id:
        if client.user in message.mentions:
            #get message
            user_message = message.content
            user_message = user_message.replace(f"<@!{client.user.id}>", "").replace(f"<@{client.user.id}>", "").strip()

            #debug info for terminal, not necessary but recommended to keep on
            print(f"User message: {user_message}")

            if message.author.id not in user_messages:
                user_messages[message.author.id] = deque(maxlen=2)  #keeps this many number of messages. should be same as the one further above.
            user_messages[message.author.id].append(user_message)

            roleplay_response = generate_response(message.author.id, user_message)

            print(f"Original response: {roleplay_response}")

            roleplay_response = remove_thinking(roleplay_response)

            response_chunks = split_message(roleplay_response)

            # Send the response in chunks
            for chunk in response_chunks:
                await message.channel.send(chunk)
                
# Start the bot
client.run(DISCORD_TOKEN)
