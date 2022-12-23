# the os module helps us access environment variables
# i.e., our API keys
import os
from dotenv import load_dotenv

# these modules are for querying the Hugging Face model
import json
import requests
import re

# the Discord Python API
import discord
import logging
from discord.ext import tasks, commands 
from discord.ui import View, Button

import random

# TODO: Some emoji is reported as unknown, consider using a fixed emoji for each category
reaction_emojis = {
    'ok': ['👌', '🆗', '🙆‍♀', '🙆‍♂'],
    'anger': ['😡', '💢', '🗡', '💔'],
    'joy': ['😊', '😇', '😀'],
    'love': ['❤', '🥰', '😊', '😘', '🤗'],
    'sadness': ['😭', '😢', '😿', '🥲', '🥶', '💔'],
    'fear': ['😱', '😰', '😨'],
    'surprise': ['🥳', '🤗'],
}


load_dotenv()
token = os.getenv('BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
    await send_event_embed()


@client.event
async def on_message(message):
    # ignore the message if it comes from the bot itself
    if message.author == client.user:
        return
    
    # the user must @ the bot to talk to it
    if "@1009744" not in message.content:
        return
    
    # TODO: restrict to listening on event channel only 
    message.content = re.sub('<@.?[0-9]*>', '', message.content).strip()
    async with message.channel.typing():
        response = 'You are smart!'

    await message.add_reaction(get_emoji('ok')[0])
    # send the model's response to the Discord channel
    
    await message.reply(response)

def check_balance():
    pass

def increase_balance():
    pass

def decrease_balance():
    pass

def claim_daily_reward():
    pass

def wish(member, tier):
    pass

def claim_gift():
    pass

def view_prize_pool():
    pass



def get_emoji(type, n=[1, 1]):
    num = random.randint(n[0], n[1])
    # return [random.choice(reaction_emojis[type]) for _ in range(num)]
    return ['👌']

async def send_event_embed():
    # get the test channel 
    test_channel = client.get_channel(1055319238149144576)
    # TODO: add checking and not resend the event embed if it already exists
    event_embed = create_event_embed()

    image_url = "jerwhiko.png"
    file = discord.File(image_url, filename="jerwhiko.png")

    component_view = View()

    button = Button()
    button.label = 'test'
    button.custom_id = 'test'
    button.callback = reply_on_interact

    disabled_button = Button()
    disabled_button.label = 'disabled'
    disabled_button.custom_id = 'disabled'
    disabled_button.disabled = True

    component_view.add_item(button)
    component_view.add_item(disabled_button)

    event_embed.set_image(url="attachment://jerwhiko.png")

    await test_channel.send(file=file, embed=event_embed, view=component_view)


async def reply_on_interact(interaction):
    author = interaction.user.name
    await interaction.response.send_message((f"{author}, you're so cool!"))


def create_event_embed():
    title = "Test Embed"
    desc = "Test Description"
    
    embed = discord.Embed(title=title, description=desc)
    
    return embed

client.run(token, log_handler=handler)