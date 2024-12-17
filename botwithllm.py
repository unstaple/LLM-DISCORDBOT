import discord
from discord.ext import commands
import asyncio
import os
from datetime import datetime, date
from dotenv import load_dotenv
from llama_handle import load_model, days, infer, template
from os.path import expanduser
from datetime import date, datetime
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import json
from dotenv import load_dotenv
import os

load_dotenv()
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
model_path = expanduser(os.getenv("MODEL_PATH"))
llm = load_model(model_path, callback_manager)
self_id = os.getenv("BOT_ID")

intents = discord.Intents.all()
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)
message_queue = asyncio.Queue()

history = f"I just got boosted up on discord server at {days[date.today().weekday()]} {(str(datetime.now()))[:-7]}"

@client.event
async def on_ready():
    global channel
    channel = client.get_channel(int(os.getenv("CHANNEL")))
    if channel is None:
        print("Channel not found!")
    else:
        message = "bot is now online!"
        print(message + '\n' + '-'*len(message))
        # Start the message processing coroutine
        client.loop.create_task(process_messages())

async def process_messages():
    global history
    while True:
        message = await message_queue.get()
        if message is None:
            break  # Stop the worker if None is sent to the queue
        text = f'{{"name" : "{str(message.author)}", "message" : "{message.content}", "time" : "{days[date.today().weekday()]} {(str(datetime.now()))[:-7]}"}}'
        chat = template.format(chat_history=history, text=text)
        result, history = infer(chat, llm, history, text)
        print(history)
        
        if result:
            await channel.send(str(result["respond"]))
        else:
            await channel.send("Empty message.")

@client.event
async def on_member_join(member):
    result = "test"
    await channel.send(result)
    print(member)

@client.event
async def on_member_remove(member):
    result = "test"
    await channel.send(result)

@client.event
async def on_message(message):
    author = message.author
    if str(author.id) != self_id and message.channel == channel:
        await message_queue.put(message)

@client.command()
async def test(ctx):
    await ctx.send("test message")

client.run(os.getenv("BOT_TOKEN"))
