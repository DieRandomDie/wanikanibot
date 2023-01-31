import discord
import json
import dat
from datetime import datetime
import pytz
from discord.ext import tasks
from functions import get_reviews, get_stages

client = discord.Bot()


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='The Crabigator'))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.command(description="Get number of available lessons and reviews.")
async def reviews(ctx):
    review_embed = discord.Embed(title="Studies")
    d = get_reviews(str(ctx.author.id))
    if not d:
        await ctx.respond("You haven't provided your API key yet. (command doesn't exist yet)")
    review_embed.add_field(name="Type", value="Lessons:\nReviews:\nReviews (12h):\nReviews (24h):")
    review_embed.add_field(name="Available", value=f"{d['lessons']}\n{d['reviews']}\n{d['twelve']}\n{d['twentyfour']}")
    review_embed.add_field(name="Next", value=d['next'], inline=False)
    await ctx.respond(embed=review_embed)


@client.command(description="Get a summary of your SRS stages.")
async def stages(ctx):
    await ctx.defer()
    stages_embed = discord.Embed(title="Stages")
    d = get_stages(str(ctx.author.id))
    if not d:
        await ctx.followup.send("You haven't provided your API key yet. (command doesn't exist yet)")
    stages_embed.add_field(name="Level", value="Unlearned:\nAppr. 1:\nAppr. 2:\nAppr. 3:\nAppr. 4:\nGuru 1:\nGuru 2:\nMaster:\nEnlightened:\nBurned:")
    stages_embed.add_field(name="Count", value=f"{d['unlocked']}\n{d['apprentice_1']}\n{d['apprentice_2']}\n{d['apprentice_3']}\n{d['apprentice_4']}\n{d['guru_1']}\n{d['guru_2']}\n{d['master']}\n{d['enlightened']}\n{d['burned']}")
    await ctx.followup.send(embed=stages_embed)


client.run(dat.TOKEN)
