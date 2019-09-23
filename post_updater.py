#!/usr/bin/env python
import os

import discord

POST_FILE = os.environ.get("POST_FILE", "/etc/discord-post-updater/post")
with open(POST_FILE) as content_file:
    content = content_file.read()

client = discord.Client()


async def post_or_update():
    channel = client.get_channel(int(os.environ["DISCORD_CHANNEL"]))
    message_id = os.environ.get("DISCORD_MESSAGE_ID", channel.last_message_id)
    if message_id:
        message = await channel.fetch_message(message_id)
        await message.edit(content=content)
    else:
        await channel.send(content=content)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await post_or_update()
    await client.logout()


client.run(os.environ["DISCORD_TOKEN"])
