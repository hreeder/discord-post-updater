#!/usr/bin/env python
import os

from typing import Any

import discord

client = discord.Client()


def get_actions_environ(
    key: str, default_value: Any = None, required: bool = False
) -> Any:
    if key in os.environ:
        return os.environ[key]
    elif f"INPUT_{key.upper()}" in os.environ:
        return os.environ[f"INPUT_{key.upper()}"]
    elif required:
        raise KeyError(f"{key} not found in environment.")

    return default_value


async def post_or_update():
    channel = client.get_channel(
        int(get_actions_environ("DISCORD_CHANNEL", required=True))
    )
    message_id = get_actions_environ("DISCORD_MESSAGE", channel.last_message_id)

    post_file_path = get_actions_environ("POST_FILE", "/etc/discord-post-updater/post")
    with open(post_file_path) as post_file:
        post = post_file.read()

    if message_id and message_id != "new":
        message = await channel.fetch_message(message_id)
        await message.edit(content=post)
    else:
        await channel.send(content=post)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await post_or_update()
    await client.logout()


client.run(get_actions_environ("DISCORD_TOKEN", required=True))
