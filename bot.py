from typing import Optional
from discord.ext import commands
from discord.utils import get
from discord import (
    Embed,
    Guild,
    Message,
    Intents,
    HTTPException
)

import json
import openai
import asyncio

from errors import *

with open('config.json', 'r') as f:
    config = json.load(f)

class ChatBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            command_prefix='?',
            case_insensitive=True,
            intents = Intents.all()
        )

bot = ChatBot()
openai.api_key = config['api_token']

async def bot_reply(content: str) -> str:
        completions = openai.Completion.create(prompt=content, engine="text-davinci-002",)
        return completions.choices[0].text.strip()


@bot.listen()
async def on_guild_join(guild: Guild) -> None:
    try:
        await guild.text_channels[0].send(
            'Thank you for inviting me!\nBefore trying Chat GPT, use `?setup` command.'
        )
    except HTTPException:
        pass


@bot.listen()
async def on_message(message: Message) -> None:

    if message.channel.name != 'chat-bot' or message.author.bot:
        return

    try:
        bot_message = await asyncio.wait_for(bot_reply(message.content), timeout=60)
    except asyncio.TimeoutError:
        raise Timeout

    await message.channel.send(bot_message)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    content: Optional[str] = None

    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.UserInputError):
        return
    elif isinstance(error, MyError):
        content = error.message
    elif isinstance(error, commands.BotMissingPermissions):
        content = f'In order to invoke this command, please give me the following permissions\n\
            **{", ".join(error.missing_permissions)}**'

    if content:
        await ctx.send(content)
        return
    else:
        raise error


@bot.event
async def on_ready():
    print('Bot ready.')


@bot.command()
async def setup(ctx: commands.Context) -> None:

    if get(ctx.guild.text_channels, name='chat-bot') is not None:
        raise ChannelAlreadyExists

    try:
        channel = await ctx.guild.create_text_channel(name='chat-bot')
    except HTTPException:
        raise ChannelFailedToCreate

    await ctx.send('Successfully create `chat-bot` channel.')
    message = await channel.send(
        embed=Embed(
            title="Welcome to Chat-bot channel!!",
            description="If you say something in this channel, the chat bot will reply to you!",
            color=0xfffacd
        )
    )

    try:
        await message.pin()
    except HTTPException:
        pass

bot.run(config['bot_token'])
