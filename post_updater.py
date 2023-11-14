#!/usr/bin/env python
import datetime
import os
import sys
import xml.etree.ElementTree as ElementTree

from typing import Any

import discord
import pytz

client = discord.Client()


def get_actions_environ(
    key: str, default_value: Any = None, required: bool = False
) -> Any:
    """
    Get the specified enivironment variable. If it does not exist, try appending
    INPUT_ to match any GitHub Action-created ones.

    :param str key: The environment variable to retrieve.
    :param Any default_value: The default value if this is an optional key.
    :param bool required: Whether to raise an exception if the key doesn't exist.
    """
    if key in os.environ:
        return os.environ[key]
    elif f"INPUT_{key.upper()}" in os.environ:
        return os.environ[f"INPUT_{key.upper()}"]
    elif required:
        raise KeyError(f"{key} not found in environment.")

    return default_value


async def post_or_update():
    """
    Main function. Read a file from the POST_FILE or POST_XML environment vars,
    construct a message and send it to a specified channel, or otherwise edit
    an existing message.
    """

    # Fetch the channel to which to send the message to
    channel = client.get_channel(
        int(get_actions_environ("DISCORD_CHANNEL", required=True))
    )
    if channel is None:
        print("Channel could not be found! Aborting")
        return

    # If there is no specific message ID (or the string "new") specified, use
    # the last message in the channel. This can fail if anyone can post messages
    # in this channel, since the bot can only edit its own messages.
    message_id = get_actions_environ("DISCORD_MESSAGE", channel.last_message_id)

    # Read either the raw markdown or the XML, but not both.
    post_file_path = get_actions_environ("POST_FILE", None)
    post_xml_path = get_actions_environ("POST_XML", None)
    if not post_file_path and not post_xml_path:
        print("Neither POST_FILE nor POST_XML was supplied to the action.")
        sys.exit(1)

    if post_file_path and post_xml_path:
        print("Both POST_FILE and POST_XML was supplied: use one only.")
        sys.exit(1)

    # Construcct the arguments to pass to channel.send()
    message_args = {}
    if post_file_path:
        # If we're using raw markdown
        with open(post_file_path) as post_file:
            post = post_file.read()

            message_args["content"] = post
    else:
        # If we're using XML:
        tree = ElementTree.parse(post_xml_path)
        message_tag = tree.getroot()

        # Make sure to use getattr with XML since the tag may not be there
        message_args["content"] = getattr(message_tag.find("./content"), "text", "")
        message_args["embeds"] = []

        # There can be up to 10 embeds
        for embed_tag in message_tag.findall("./embed"):
            embed = discord.Embed(
                title=getattr(embed_tag.find("./title"), "text", ""),
                description=getattr(embed_tag.find("./content"), "text", ""),
                colour=int(embed_tag.attrib.get("colour", 0))
            )

            # An embed can have multiple fields
            for field_tag in embed_tag.findall("./field"):
                field = discord.EmbedField(
                    name=getattr(field_tag.find("./title"), "text", ""),
                    value=getattr(field_tag.find("./content"), "text", ""),
                    inline=bool(field_tag.attrib.get("inline", False))
                )
                embed.append_field(field)

            # Set a time footer unconditionally to indicate this was an auto-
            # generated message.
            current_uk_time = datetime.datetime.now(tz=pytz.timezone('Europe/London'))
            embed.set_footer(
                text=f"Last updated: {current_uk_time.strftime('%a, %d %b %Y %H:%M:%S %Z')}"
            )
            message_args["embeds"].append(embed)

        # Set up a view for any buttons. If there are no buttons, this will do nothing.
        message_args["view"] = discord.ui.View(timeout=None)
        # There can be up to 25 buttons, max 5 rows and max 5 cols
        for button_tag in message_tag.findall("./button"):
            button = discord.ui.Button(
                style=getattr(discord.ButtonStyle, button_tag.attrib.get("style", "secondary"), discord.ButtonStyle.secondary),
                custom_id=button_tag.attrib.get("id", None),
                url=button_tag.attrib.get("url", None),
                disabled=button_tag.attrib.get("disabled", None) == "true",
                label=getattr(button_tag.find("./label"), "text", ""),
                emoji=getattr(button_tag.find("./emoji"), "text", None),
                row=int(button_tag.attrib.get("row", 0))
            )
            message_args["view"].add_item(button)

    # Edit existing message if an ID was specified, otherwise create anew.
    if message_id and message_id != "new":
        message = await channel.fetch_message(message_id)
        await message.edit(**message_args)
    else:
        await channel.send(**message_args)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    try:
        await post_or_update()
    except Exception:
        sys.exit(1)
    await client.close()


client.run(get_actions_environ("DISCORD_TOKEN", required=True))
