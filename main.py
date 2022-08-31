import discord
from discord.ext import commands
import random, datetime, asyncio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

#The prefix to use the bot commands
client = commands.Bot(command_prefix='$')

#Bot is online
@client.event
async def on_ready():
    #terminal print
    print(f'Logged on as {client.user}')

#set up bot
@client.command(name="setup")
async def setup(ctx, hour:int, minute:int, second:int):
    #print(hour, minute, second)

    #catching bad arguments
    if not (0 < hour < 24 and 0 <= minute <= 60 and 0 <= second < 60):
        raise commands.BadArgument()

    time = datetime.time(hour, minute, second)
    timestr = time.strftime("%I:%M:%S %p")
    await ctx.send(f"A message will be sent of the games that are currently free on epic games\nat {timestr} in this channel.\nConfirm by simply replying 'yes'.")
    try:
        #bot waits for 30 seconds for a message
        msg = await client.wait_for("message", timeout=30, check=lambda message: message.author == ctx.author)
    except asyncio.TimeoutError:
        #bot doesnt recieve message within the timeout duration then send message and cancel
        await ctx.send("You took too long to respond! Cancelling setup")
        return

    #if the message is yes then start the schedule message
    if msg.content == "yes":
        await ctx.send("Setup up complete. Thank you!")
        await schedule_message(hour, minute, second, ctx.channel.id)
    else:
        #if anything other then a yes then cancel
        await ctx.send("Setup up cancelled.")

@setup.error
async def daily_error(ctx, error):
    if isinstance(error, commands.BadArgument):
        await ctx.send("Incorrect format. Use command this way: 'hour minute second', it is a 24 hour clock. For Example: '15 30 0' for a time of 3:30pm")

async def schedule_message(h, m, s, channelid):
    while True:
        #Stores the now time
        now = datetime.datetime.now()
        #then = now + datetime.timedelta(days=1)
        then = now.replace(hour=h, minute=m, second=s)
        if then < now:
            then += datetime.timedelta(days=1)
        wait_time = (then - now).total_seconds()
        await asyncio.sleep(wait_time)

        #The channel to send the message in
        channel = client.get_channel(channelid)

        #The path to the driver for chrome
        ser = Service("C:\Program Files (x86)\chromedriver.exe")
        op = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=ser, options=op)

        #Epic Games Store Page
        driver.get("https://store.epicgames.com/en-US/free-games")

        #Finding the free games elements on the epic games page
        free_games_epic = driver.find_elements(By.CSS_SELECTOR, 'div.css-1h2ruwl')

        #finds the time for all the free games
        times = driver.find_elements(By.CSS_SELECTOR, 'span.css-nf3v9d')

        #send the list of free games
        await channel.send('The Free Epic Games Are...')
        for x in range(len(free_games_epic)):
            await channel.send(free_games_epic[x].text + ', ' + times[x].text)

        #quit the current driver
        driver.quit()

        await asyncio.sleep(1)


#The token that allows the bot to run
client.run('MTAxMzgyODYwNzQ3MjMyMDU2NA.GJ9kOG.VIez0vRq0eiousx_uwM0rZKj6VWovzp0EbeZWE')