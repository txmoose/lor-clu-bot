import json
import os

import discord
import redis
import requests

from discord.ext import commands
from dotenv import load_dotenv


# Config options are in .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX')
DATADRAGON_HOSTNAME = os.getenv('DATADRAGON_HOSTNAME')
BOT_OWNER = os.getenv('BOT_OWNER')
REDIS_HOST = os.getenv('REDIS_HOST')

r = redis.Redis(host=REDIS_HOST)

def load_cache(card_set: str):
    """
    Download card set json and load into Redis

    Arguments:
        card_set {str} -- set to download
    """
    DATADRAGON_URL = f'https://{DATADRAGON_HOSTNAME}/latest/{card_set}/en_us/data/{card_set}-en_us.json'
    cards = json.loads(requests.get(DATADRAGON_URL).content)

    for card in cards:
        card_code = card["cardCode"]

        # Champions have multiple cards with the same "name",
        # So we only store the Level 1 Card ID here for consistency
        if card["supertype"] == "Champion":
            card_code = card_code[:7]

        r.set(card["name"].lower(), card_code)
        r.set(card["cardCode"], json.dumps(card))


bot = commands.Bot(command_prefix=COMMAND_PREFIX)

@bot.command(name='reload-cache', hidden=True)
async def reload_cache(ctx):
    if str(ctx.author) != BOT_OWNER:
        await ctx.send(f"I'm sorry, {ctx.author}, but you can't do that.")
        return
    await ctx.send('Refreshing Set 1')
    load_cache('set1')
    await ctx.send('Refreshing Set 2')
    load_cache('set2')
    await ctx.send('Refresh Complete')


@bot.command(name="card", help='Will attempt to retrieve the specified card')
async def card_lookup(ctx, *, arg):
    lookup_name = arg
    try:
        # We're going to make a list and iterate over it because sometimes, cards are multiple cards
        game_absolute_paths = []

        # Here, we look up the card by name
        card_code = r.get(lookup_name)

        # And here, we look up the card JSON by the card ID that we got from the name above
        # There's probably a better way to do this
        card_info = json.loads(r.get(card_code))

        # There's probably a better way to do this
        game_absolute_paths.append(card_info.get("assets")[0].get("gameAbsolutePath"))

        # If the card is a champion, we're going to get the list of associated cards
        # from the JSON and check those associated cards to see which one is the other
        # unit card, and we'll show that one to the server, as well
        if card_info.get("supertype") == "Champion":
            associated_cards = card_info.get("associatedCardRefs")
            for associated_card in associated_cards:
                candidate_card = json.loads(r.get(associated_card))
                if candidate_card.get("type") == "Unit" and candidate_card.get("supertype") == "Champion":
                    game_absolute_paths.append(candidate_card.get("assets")[0].get("gameAbsolutePath"))
        
        # Now we send all the cards we got to the server
        for absolute_path in game_absolute_paths:
            await ctx.send(absolute_path)
    except:
        await ctx.send(f"I couldn't find a card named {arg}.")    

bot.run(TOKEN)
