from dotenv import load_dotenv
import os
import discord
from discord import app_commands	
from discord.ext import commands
import asyncio
import json
import mysql.connector
import time
from discord.ext import tasks


# Get configuration.json
# print(os.listdir())
# with open("configuration.json", "r") as config: 
# 	print(os.listdir())
# 	data = json.load(config)
# 	token = data["token"]
# 	# prefix = data["prefix"]
# 	owner_id = data["owner_id"]

owner_id = os.getenv("owner_id")
token = os.getenv("token")
prefix = ''

class Greetings(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self._last_member = None

# Intents
intents = discord.Intents.all()
intents.members = True
intents.guilds = True

# The bot
bot = commands.Bot(command_prefix = '!@#', intents = intents, owner_id = owner_id)
client = commands.Bot(command_prefix = "!", intents = intents)

envhost = os.getenv('host')
envuser = os.getenv('user')
envpassword = os.getenv('password')
envdatabase = os.getenv('database')

# Database Init
mydb = mysql.connector.connect(
	host=envhost,
	user=envuser,
	password=envpassword,
	database = envdatabase)
cursor = mydb.cursor(dictionary=True, buffered=True)

# # Load cogs
# if __name__ == '__main__':
# 	for filename in os.listdir("Cogs"):
# 		if filename.endswith(".py"):
# 			bot.load_extension(f"Cogs.{filename[:-3]}")

@bot.event
async def on_ready():
	print(f"We have logged in as {bot.user}")
	print(discord.__version__)
	await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Created by dr3gos!"))
	# await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name =f"{bot.command_prefix}help"))
	owner = bot.get_user(owner_id)
	await owner.send("Bot online!")
	try:
		synced = await bot.tree.sync()
		print(f"Synced {len(synced)} command(s)")
	except Exception as e:
		print(e)
	keepalive.start()	

# init of ids
hrid = 1067615240256225370
shrid = 1091129949768921109
ocsoid = 1067615254307164193
wspid = 1067615253128556554
dotid = 1067615255297015888
platinumid = 1103113628674166824
hyperplatid = 1112510328450859089

@bot.tree.command(name='register', description='Register your Vehicle into the database.')
@app_commands.describe(plate='License Plate of your vehicle.')
@app_commands.describe(year='Year of your vehicle.')
@app_commands.describe(make='Make of your vehicle.')
@app_commands.describe(model='Model of your vehicle.')
@app_commands.describe(color='Color of your vehicle.')
async def register(interaction: discord.Interaction, plate: str, year: str, make: str, model: str, color: str):
	
	# init id objects
	platinum = discord.utils.get(interaction.guild.roles, id=platinumid)
	hyperplat = discord.utils.get(interaction.guild.roles, id=hyperplatid)
	hr = discord.utils.get(interaction.guild.roles, id=hrid)
	shr = discord.utils.get(interaction.guild.roles, id=shrid)
	ocso = discord.utils.get(interaction.guild.roles, id=ocsoid)
	wsp = discord.utils.get(interaction.guild.roles, id=wspid)
	dot = discord.utils.get(interaction.guild.roles, id=dotid)

	limit = 3
	if platinum in interaction.user.roles:
		limit = 6
	elif hr in interaction.user.roles:
		limit = 6

	# check roles and cars
	cursor.execute(f"SELECT * FROM cars WHERE userid = '{interaction.user.id}'")
	rows = cursor.fetchall()
	if len(rows) < limit or shr in interaction.user.roles or hyperplat in interaction.user.roles:
	# add cars
		sql = f"INSERT INTO cars (USERID, PLATE, YEAR, MAKE, MODEL, COLOR) VALUES ('{interaction.user.id}', '{plate.upper()}', '{year}', '{make.capitalize()}', '{model.capitalize()}', '{color.capitalize()}')"
		cursor.execute(sql)
		mydb.commit()
		lastid = cursor.lastrowid
		cursor.execute(f"SELECT * FROM cars WHERE carid = '{lastid}'")
		lastentry = cursor.fetchone()
		if lastentry['PLATE'] == plate.upper():
			await interaction.response.send_message('Registered car!', ephemeral=True)
		else:
			await interaction.response.send_message('Error!', ephemeral=True)
	else:
		await interaction.response.send_message("Sorry, but you have exceeded the registration limit. You can either edit an existing car or delete one and try registering again.", ephemeral=True)

@bot.tree.command(name='civ-lookup', description='Look up a civilian from the database.')
@app_commands.describe(name='Civilian you want to look up.')
async def civlookup(interaction: discord.Interaction, name: str):
	name = name[2:-1]

	# init id objects
	platinum = discord.utils.get(interaction.guild.roles, id=platinumid)
	hyperplat = discord.utils.get(interaction.guild.roles, id=hyperplatid)
	hr = discord.utils.get(interaction.guild.roles, id=hrid)
	shr = discord.utils.get(interaction.guild.roles, id=shrid)
	ocso = discord.utils.get(interaction.guild.roles, id=ocsoid)
	wsp = discord.utils.get(interaction.guild.roles, id=wspid)
	dot = discord.utils.get(interaction.guild.roles, id=dotid)
	perms = None

	# perms check
	if hr in interaction.user.roles:
		perms = True
	elif shr in interaction.user.roles:
		perms = True
	elif ocso in interaction.user.roles:
		perms = True
	elif wsp in interaction.user.roles:
		perms = True
	elif dot in interaction.user.roles:
		perms = True
	else:
		perms = False

	if perms:
		cursor.execute(f"SELECT * FROM cars WHERE userid = '{name}'")
		rows = cursor.fetchall()
		if not len(rows) == 0:
			localrows = []
			for row in rows:
				info = []
				info.append("---------------\n")
				# info.append("Discord Member: " + "<@" + row['USERID'] + ">" + "\n")
				info.append("> Car ID: " + str(row['CARID']) + "\n")
				info.append("> Plate: " + row['PLATE'] + "\n")
				info.append("> Year: " + row['YEAR'] + "\n")
				info.append("> Make: " + row['MAKE'] + "\n")
				info.append("> Model: " + row['MODEL'] + "\n")
				info.append("> Color: " + row['COLOR'])
				localrows.append(info)
			localrows.append("---------------")
			embed = discord.Embed(title="Civilian Police Database", description='\n'.join(''.join(x) for x in localrows), colour=16777215)
			await asyncio.sleep(delay=0)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			await interaction.response.send_message('Civilian has no cars!', ephemeral=True)
	else:
		await interaction.response.send_message('Only HR+ and LEO are allowed to use this command!', ephemeral=True)

@bot.tree.command(name='plate-lookup', description='Look up a vehicle from the database.')
@app_commands.describe(plate='License Plate of the vehicle.')
async def platelookup(interaction: discord.Interaction, plate: str):

	# init id objects
	platinum = discord.utils.get(interaction.guild.roles, id=platinumid)
	hyperplat = discord.utils.get(interaction.guild.roles, id=hyperplatid)
	hr = discord.utils.get(interaction.guild.roles, id=hrid)
	shr = discord.utils.get(interaction.guild.roles, id=shrid)
	ocso = discord.utils.get(interaction.guild.roles, id=ocsoid)
	wsp = discord.utils.get(interaction.guild.roles, id=wspid)
	dot = discord.utils.get(interaction.guild.roles, id=dotid)
	perms = None

	# perms check
	if hr in interaction.user.roles:
		perms = True
	elif shr in interaction.user.roles:
		perms = True
	elif ocso in interaction.user.roles:
		perms = True
	elif wsp in interaction.user.roles:
		perms = True
	elif dot in interaction.user.roles:
		perms = True
	else:
		perms = False

	if perms:
		cursor.execute(f"SELECT * FROM cars WHERE plate = '{plate}'")
		rows = cursor.fetchall()
		if not len(rows) == 0:
			localrows = []
			for row in rows:
				info = []
				info.append("---------------\n")
				info.append("> Discord Member: " + "<@" + row['USERID'] + ">" + "\n")
				info.append("> Car ID: " + str(row['CARID']) + "\n")
				info.append("> Plate: " + row['PLATE'] + "\n")
				info.append("> Year: " + row['YEAR'] + "\n")
				info.append("> Make: " + row['MAKE'] + "\n")
				info.append("> Model: " + row['MODEL'] + "\n")
				info.append("> Color: " + row['COLOR'])
				localrows.append(info)
			localrows.append("---------------")
			embed = discord.Embed(title="Car Police Database", description='\n'.join(''.join(x) for x in localrows), colour=16777215)
			await asyncio.sleep(delay=0)
			await interaction.response.send_message(embed=embed, ephemeral=True)
		else:
			await interaction.response.send_message('No vehicles found with that plate!', ephemeral=True)
	else:
		await interaction.response.send_message('Only HR+ and LEO are allowed to use this command!', ephemeral=True)

@bot.tree.command(name='my-cars', description='Gives you a list of the cars you have registered.')
async def mycars(interaction: discord.Interaction):
	cursor.execute(f"SELECT * FROM cars WHERE userid = '{interaction.user.id}'")
	rows = cursor.fetchall()
	if not len(rows) == 0:
		localrows = []
		for row in rows:
			info = []
			info.append("---------------\n")
			info.append("> Car ID: " + str(row['CARID']) + "\n")
			info.append("> Plate: " + row['PLATE'] + "\n")
			info.append("> Year: " + row['YEAR'] + "\n")
			info.append("> Make: " + row['MAKE'] + "\n")
			info.append("> Model: " + row['MODEL'] + "\n")
			info.append("> Color: " + row['COLOR'])
			localrows.append(info)
		localrows.append("---------------")
		embed = discord.Embed(title="Your cars:", description='\n'.join(''.join(x) for x in localrows), colour=16777215)
		await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		await interaction.response.send_message("You do not have any cars!", ephemeral=True)

@bot.tree.command(name='delete-car', description='Deletes the car from the Registration Database.')
@app_commands.describe(carid="The Car ID of the vehicle which you're trying to delete (you can only choose one of your own cars).")
async def deletecar(interaction: discord.Interaction, carid: int):

	# init id objects
	platinum = discord.utils.get(interaction.guild.roles, id=platinumid)
	hyperplat = discord.utils.get(interaction.guild.roles, id=hyperplatid)
	hr = discord.utils.get(interaction.guild.roles, id=hrid)
	shr = discord.utils.get(interaction.guild.roles, id=shrid)
	ocso = discord.utils.get(interaction.guild.roles, id=ocsoid)
	wsp = discord.utils.get(interaction.guild.roles, id=wspid)
	dot = discord.utils.get(interaction.guild.roles, id=dotid)
	perms = None

	#member check
	cursor.execute(f"SELECT * FROM cars WHERE carid = '{carid}'")
	lastentry = cursor.fetchone()

	# perms check
	if lastentry['USERID'] == str(interaction.user.id):
		perms = True
	elif hr in interaction.user.roles:
		perms = True
	elif shr in interaction.user.roles:
		perms = True
	else:
		perms = False

	if perms == True:
		cursor.execute(f"DELETE FROM cars WHERE carid='{carid}';")
		mydb.commit()
		await interaction.response.send_message('Vehicle deleted!', ephemeral=True)
	else:
		await interaction.response.send_message('You cannot delete a vehicle that you do not own!', ephemeral=True)

@bot.tree.command(name='edit-car', description="Edit an attribute of a car.")
@app_commands.describe(carid='The Car ID of the vehicle you want to edit.')
@app_commands.describe(newvalue='New value for the attribute you want to edit.')
@app_commands.describe(attribute='Attribute you want to change.')
@app_commands.choices(attribute=[
    app_commands.Choice(name="Plate", value="plate"),
    app_commands.Choice(name="Year", value="year"),
    app_commands.Choice(name="Make", value="make"),
	app_commands.Choice(name="Model", value="model"),
	app_commands.Choice(name="Color", value="color")
    ])
async def editcar(interaction: discord.Interaction, attribute: discord.app_commands.Choice[str], carid: str, newvalue: str):

	# init id objects
	platinum = discord.utils.get(interaction.guild.roles, id=platinumid)
	hyperplat = discord.utils.get(interaction.guild.roles, id=hyperplatid)
	hr = discord.utils.get(interaction.guild.roles, id=hrid)
	shr = discord.utils.get(interaction.guild.roles, id=shrid)
	ocso = discord.utils.get(interaction.guild.roles, id=ocsoid)
	wsp = discord.utils.get(interaction.guild.roles, id=wspid)
	dot = discord.utils.get(interaction.guild.roles, id=dotid)
	perms = None

	#member check
	cursor.execute(f"SELECT * FROM cars WHERE carid = '{carid}'")
	lastentry = cursor.fetchone()

	# perms check
	if lastentry['USERID'] == str(interaction.user.id):
		perms = True
	elif hr in interaction.user.roles:
		perms = True
	elif shr in interaction.user.roles:
		perms = True
	else:
		perms = False


	if perms == True:
		if attribute.value == 'plate':
			newvalue = newvalue.upper()
		elif attribute.value in ['make', 'model', 'color']:
			newvalue = newvalue.capitalize()
		cursor.execute(f"UPDATE cars SET {attribute.value} = '{newvalue}' WHERE carid = '{carid}'")
		mydb.commit()
		await interaction.response.send_message('Vehicle updated!', ephemeral=True)
	else:
		await interaction.response.send_message('You cannot edit a vehicle that you do not own!', ephemeral=True)

		


@bot.tree.command(name='all-cars', description='Shows all car registered on the server.')
async def testing(interaction: discord.Interaction):
	if interaction.user.id == owner_id:
		cursor.execute('SELECT * FROM cars')
		rows = cursor.fetchall()
		localrows = []
		for row in rows:
			localrows.append(str(row))
			# await interaction.send_message(f'{str(row)}', ephemeral=False)
		embed = discord.Embed(title="Stuff looked up:", description='```' + '\n'.join(''.join(x) for x in localrows) + '```')
		await interaction.response.send_message(embed=embed, ephemeral=True)
	else:
		await interaction.response.send_message('You do not have permission for this command!', ephemeral=True)
		mydb.commit()
		await interaction.response.send_message('Vehicle deleted!', ephemeral=True)

@bot.command()
async def ping(ctx):
	await ctx.send("pong")

@tasks.loop(hours=5)
async def keepalive():
	# owner = bot.get_user(owner_id)
	# await owner.send('Keep alive!')
	cursor.execute("SELECT 'KEEP_ALIVE';")

bot.run(token)