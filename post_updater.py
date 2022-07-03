#!/usr/bin/env python
import datetime
import os

from typing import Any

import discord
import pytz

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
    if channel is None:
        print("Channel could not be found! Aborting")
        return
    message_id = get_actions_environ("DISCORD_MESSAGE", channel.last_message_id)

    post_file_path = get_actions_environ("POST_FILE", "/etc/discord-post-updater/post")
    with open(post_file_path) as post_file:
        post = post_file.read()

    use_embed = bool(get_actions_environ("USE_EMBED", False))

    args = {}
    if use_embed:
        args["content"] = ""
        args["embed"] = discord.Embed(
            title=post.split("\n")[0].split("#")[1].strip(),
            description="\n".join(post.split("\n")[1:]).strip(),
            colour=int(get_actions_environ("EMBED_COLOR", '0'))
        )
        current_uk_time = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
        args["embed"].set_footer(
            text=f"Last updated: {current_uk_time.strftime('%a, %d %b %Y %H:%M:%S %Z')}"
        )
    else:
        args["content"] = post

    if message_id and message_id != "new":
        message = await channel.fetch_message(message_id)
        await message.edit(**args)
    else:
        await channel.send(**args)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await post_or_update()
    await client.close()


client.run(get_actions_environ("DISCORD_TOKEN", required=True))
