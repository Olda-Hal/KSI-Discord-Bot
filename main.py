import discord
import os


# loads token from .env file
token = os.getenv("DISCORD_TOKEN")
# creates a discord client
client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    # changes the bot's status
    await client.change_presence(activity=discord.Game(name="Píše Příští Vlnu..."))

@client.event
async def on_message(message):
    # ignores messages from the bot itself
    if message.author == client.user:
        return

    # checks if the message contains a specific string
    if 'karlik' in message.content.lower():
        # reacts with a custom emoji
        await message.add_reaction('<:Angrik:1287496326149439588>')

# assigns a role to a member when they join the server
@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Riešitel")
    await member.add_roles(role)


# runs the bot with the token

client.run(token)