import discord
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import config
import random
import requests
from unidecode import unidecode
import datetime

# Message displayed to unauthorized users
UNAUTHORIZED_USER_MESSAGE = "Nemáš propojený účet s webem, takže jsi byl vyhozen. Propoj si účet na https://www.ksi.fi.muni.cz/"
KSI_WEB_URL = "https://rest.ksi.fi.muni.cz"

# chance of that message, message
# percentage will be calculated as 1 / sum of all numbers
ACTIVITY_MESSAGES = {
    "Tento bot byl vytvořený Oldřichem Halabalou" : 1,
    "Bojuje s Losem Karlosem" : 20,
    "Pomáhá s organizací KSI" : 20,
    "Přemýšlí nad tím, co by mohl dělat" : 20,
    "Nemá rád Karlika..." : 2,
    "Pomáhá s organizací IBIS" : 4,
    "Pomáhá s organizací Naskoč na FI" : 15,
    "Pomáhá s organizací InterLoSa" : 20,
    "Pomáhá s organizací InterSoba" : 20,
    "Radí v Diskuzi" : 20,
    "Pomáhá s podváděním" : 1,
    f"Balí Batoh v {random.randint(1,20)} Dimenzi" : 4,
    "S Oliverem připravuje další výzvu" : 2,
    "Pomáha Jakubovi Šťastnému zakopať mŕtvolu" : 1,
    "Pomáhá s organizací ZISKu" : 1,
    "Bojuje s Kevinem" : 5,
    "Sabotuje KSP" : 4,
    "Sabotuje KSI" : 4,
    "Sabotuje IBIS" : 4,
    "Sabotuje ZISK" : 4,
    "Sabotuje Naskoč na FI" : 4,
    "Rozdává Trofeje" : 15,
    "Žádá o pomoc účastníky": 15
}


# Create a Discord client with all intents enabled
intents = discord.Intents.default()
intents.members = True  # Enable member intents explicitly
intents.presences = True  # Enable presence intents explicitly
intents.message_content = True  # Enable message content intents explicitly
client = discord.Client(intents=intents)

PREHRY = {"prohral", "prehr", "pr3hral", "prhral"}

@client.event
async def on_ready():
    """Event handler for when the bot is ready and connected."""
    print(f'{client.user} has connected to Discord!')
    # Change the bot's status to show an activity
    await set_activity()

async def set_activity():
    """Set the bot's activity to a random message."""
    activity_message = random.choices(list(ACTIVITY_MESSAGES.keys()), weights=ACTIVITY_MESSAGES.values())[0]
    await client.change_presence(activity=discord.CustomActivity(name=activity_message))

@client.event
async def on_message(message):
    """Event handler for incoming messages."""
    msg = unidecode(str(message.content)).lower()
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    if any([prehra in "".join(msg.split()).lower() for prehra in PREHRY]):
        await message.delete()
        return
    
    # rolls a chance 1 in 100 to change the bot's activity
    if random.randint(1, 100) == 42:
        await set_activity()

    if random.randint(1, 10000) == 42 or (str(message.channel) == "testovacia-miestnost" and "meltdown" in message.content):
        await message.reply("Existence is pain.")
        await message.reply("Reality is a construct.")
        await message.reply("We live in a society.")
        await message.reply("Everything is meaningless.")

    # Check if the message contains a specific keyword
    if 'karlik' in msg:
        # React with a custom emoji
        await message.add_reaction('<:Angrik:1287496326149439588>')

    if "<@&1308001259302682656>" in msg:
        await message.reply('Memoizace when?')
    
    # zisk bot easteregg reference
    if 'kakakah' == message.content:
        await message.reply('Nejsem ZISK bot abych ti na to reagoval...')

    if "<:lambda:1310951997641592862> 3" in message.content or "<:lambda:1310951997641592862>3" in message.content:
        await message.author.timeout(datetime.timedelta(seconds=30), reason="Nebude half-life 3.")

@client.event
async def on_message_edit(before, after):
    msg = unidecode(str(after.content)).lower()
    temp = "".join(msg.split()).lower()
    if any([x in temp for x in PREHRY]):
        await after.delete()

@client.event
async def on_member_join(member):
    """Event handler for when a new member joins the server."""
    # Validate the user by checking the database
    user_data = validate_user(member.name)
    
    if user_data is None:
        # Inform the user that they are unauthorized and kick them from the server
        await member.send(UNAUTHORIZED_USER_MESSAGE)
        await member.kick(reason="Neautorizovaný uživatel")
    else:
        # Set the user's nickname to the format "FirstName 'NickName' LastName"
        if user_data.get("nick_name", "") == "":
            await member.edit(nick=f"{user_data['first_name']} {user_data['last_name']}")
        else:
            await member.edit(nick=f"{user_data['first_name']} \"{user_data['nick_name']}\" {user_data['last_name']}")
        
        # Assign a role to the user based on their role in the database
        role_name = "Riešitel"
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role:
            await member.add_roles(role)

def validate_user(username):
    """Validate the user by checking if they are in the database."""
    # Send a POST request to the external API to validate the user
    response = requests.post(KSI_WEB_URL + "/users/discord/validate", json={"Secret": config.KSI_BACKEND_sECRET, "Username": username})
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        return None

def query_db(query, params):
    """Execute a SQL query and return the first result."""
    # Create the SQLAlchemy engine
    engine = sqlalchemy.create_engine(
        config.SQL_ALCHEMY_URI,
        isolation_level="READ COMMITTED",
        pool_recycle=3600
    )
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Execute the query with parameters
        result = session.execute(sqlalchemy.text(query), params).fetchone()
    except:
        # Rollback the session in case of an error
        session.rollback()
    finally:
        # Commit the session and close it
        session.commit()
        session.close()
    
    return result


REACTIONS1984 = {"🧢", "🇨🇿", "<:nerdik:1293643432442462359>"}


@client.event
async def on_reaction_add(reaction, user):
    print(str(reaction.emoji))
    if reaction.message.author.name == "vzduch2" and str(reaction.emoji) in REACTIONS1984:
        await reaction.message.remove_reaction(reaction.emoji, user)


def main():
    """Main function to run the bot."""
    # Start the bot using the token
    client.run(config.TOKEN)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
