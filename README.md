# DiscordAIChatbot-Ollama

This program has a bot reacting to being pinged and subsequently responding to it using a pre-defined personality prompt given to the AI, while storing a definite number of messages in an array acting as short-term memory.

It can act as any character provided you give a detailed enough description of the person's background, mannerisms, and any other details. Note that if more context info is given, you will most likely need a better ollama model which will use more system resources.

REQUIREMENTS:
* Ollama downloaded
* Model chosen and installed properly
These are required for the program to run properly.

Note that your choice of ollama model is very important. If you are on a weaker system, consider using a model with a smaller context size that takes up less resources. If responses are lackluster, consider using a higher context size model should your system allow for it.

Change the .env file as well as the character description located in bot.py.
