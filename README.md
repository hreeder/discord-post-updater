# discord-post-updater
A quick tool for updating a post on Discord.

Servers like to have information posts, however due to (reasonable) restrictions by
discord, these posts have to be edited by their original author.

This project solves that by storing the posts as markdown, and updating them in
Discord by a bot, with the intention that this project is used within a CI system.

## Usage - Docker
This project publishes an official docker image at `hreeder/discord-post-updater`.

Supply the following environment variables:
* `DISCORD_TOKEN` - Your discord bot token
* `DISCORD_CHANNEL` - Discord Channel ID in which to make the post

Optionally supply:
* `POST_FILE` - A path to the file containing the post content. Defaults to
  `/etc/discord-post-updater/post`.
* `DISCORD_MESSAGE` - If not supplied, the bot will update the last message in the
  channel. If supplied as `new` the bot will make a new post, and if supplied as a
  message ID, it will update the specified message.

## Usage - GitHub Actions
```yaml
- uses: hreeder/discord-post-updater
  with:
    discord_token: ${{ secrets.discord_bot_token }}
    post_file: README.md
    discord_channel: '1234567890' # N.B. The quote marks here are required
    discord_message: new # Optional, use quotes if specifying an ID
```

Please see the Docker section for a description of each variable.

## Usage - Source
```
pip install -r requirements.txt
DISCORD_TOKEN=foo POST_FILE=/path/to/post DISCORD_CHANNEL=1234567890 python post_updater.py
```

As before, please see the Docker section for which environment varibles to set.
