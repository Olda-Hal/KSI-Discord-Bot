import discord
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import config
import random
import requests

# Message displayed to unauthorized users
UNAUTHORIZED_USER_MESSAGE = "Nemáš propojený účet s webem, takže jsi byl vyhozen. Propoj si účet na https://www.ksi.fi.muni.cz/"
KSI_WEB_URL = "https://www.ksi.fi.muni.cz/"

# chance of that message, message
# percentage will be calculated as 1 / sum of all numbers
ACTIVITY_MESSAGES = {
    1: "Tento bot byl vytvořený Oldřichem Halabalou",
    20: "Bojuje s Losem Karlosem",
    20: "Pomáhá s organizací KSI",
    20: "Přemýšlí nad tím, co by mohl dělat",
    2: "Nemá rád Karlika...",
    4: "Pomáhá s organizací IBIS",
    15: "Pomáhá s organizací Naskoč na FI",
    20: "Pomáhá s organizací InterLoSa",
    20: "Pomáhá s organizací InterSoba",
    20: "Radí v Diskuzi",
    1: "Pomáhá s podváděním",
    4: f"Balí Batoh v {random.randint(1,20)} Dimenzi",
    2: "S Oliverem připravuje další výzvu",
    1: "Pomáha Jakubovi Šťastnému zakopať mŕtvolu",
    1: "Pomáhá s organizací ZISKu",
    5: "Bojuje s Kevinem",
    4: "Sabotuje KSP",
    4: "Sabotuje KSI",
    4: "Sabotuje IBIS",
    4: "Sabotuje ZISK",
    4: "Sabotuje Naskoč na FI",
    15: "Rozdává Trofeje",
    15: "Žádá o pomoc účastníky"
}


# Create a Discord client with all intents enabled
intents = discord.Intents.default()
intents.members = True  # Enable member intents explicitly
intents.presences = True  # Enable presence intents explicitly
intents.message_content = True  # Enable message content intents explicitly
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    """Event handler for when the bot is ready and connected."""
    print(f'{client.user} has connected to Discord!')
    # Change the bot's status to show an activity
    await set_activity()

async def set_activity():
    """Set the bot's activity to a random message."""
    activity_message = random.choices(list(ACTIVITY_MESSAGES.values()), weights=ACTIVITY_MESSAGES.keys())[0]
    await client.change_presence(activity=discord.Game(name=activity_message))

@client.event
async def on_message(message):
    """Event handler for incoming messages."""
    # Ignore messages from the bot itself
    if message.author == client.user:
        return
    
    # rolls a chance 1 in 100 to change the bot's activity
    if random.randint(1, 100) == 42:
        await set_activity()

    # Check if the message contains a specific keyword
    if 'karlik' in message.content.lower():
        # React with a custom emoji
        await message.add_reaction('<:Angrik:1287496326149439588>')
    
    # zisk bot easteregg reference
    if 'kakakah' is message.content:
        await message.reply('Nejsem ZISK bot abych ti na to reagoval...')

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
        if user_data.nick_name is None:
            await member.edit(nick=f"{user_data["first_name"]} {user_data["last_name"]}")
        else:
            await member.edit(nick=f"{user_data["first_name"]} \"{user_data["nick_name"]}\" {user_data["last_name"]}")
        
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

def main():
    """Main function to run the bot."""
    # Start the bot using the token
    client.run(config.TOKEN)

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
