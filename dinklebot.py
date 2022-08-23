import discord
from discord.ext import tasks, commands

import os
import json
import shutil
import utilities
from datetime import datetime

description = "Dinklebot"
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='$', description=description, intents=intents)
#----------------------------------------------------------------------------
CHALLENGERS = utilities.readChallengersFile()
GOAL = utilities.getCurrentGoal()
ADMINS = ["ToastyWombat#0001", "Verus#0077"]

#----------------------------------------------------------------------------
def addChallenger(name):
    global CHALLENGERS
    CHALLENGERS = utilities.addChallenger(name)

def updateChallengerPoints(name, activity, points):
    global CHALLENGERS
    weight = utilities.getWeight(activity)
    total = float(points) * float(weight)

    CHALLENGERS[activity][name] = round(total + float(CHALLENGERS[activity][name]),2)
    utilities.save(CHALLENGERS, utilities.CHALLENGE_FILE)

    CHALLENGERS = utilities.readChallengersFile()
    return total

def subtractChallengerPoints(name, activity, points):
    global CHALLENGERS
    points = float(points)
    activity = activity.lower()

    CHALLENGERS[activity][name] = round(float(CHALLENGERS[activity][name]) - points, 2)
    utilities.save(CHALLENGERS, utilities.CHALLENGE_FILE)
    CHALLENGERS = utilities.readChallengersFile()
    
    activityTotal = CHALLENGERS[activity][name]
    return activityTotal

#----------------------------------------------------------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()

    setupNewMonth.start()
    saveBackup.start()

    print(f'Logged in as {bot.user.name} : {bot.user.id}')
    print('------')

#----------------------------------------------------------------------------
@bot.hybrid_command(name="change", description="Changes the current challenge's total point goal")
async def change(ctx, goal):
    global GOAL
    try: 
        utilities.changeGoal(utilities.readGoalFile(), goal)
        GOAL = utilities.getCurrentGoal()
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")
        return
    await ctx.send(f"Goal updated to {GOAL}")

@bot.hybrid_command(name="points", description="Get your total points in the curent challenge")
async def points(ctx):
    global CHALLENGERS
    name = str(ctx.author)
    try: 
        points = utilities.getChallengerTotal(CHALLENGERS, name)
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")
        return
    await ctx.send(f"User {name} has {points} points this challenge")

@bot.hybrid_command(name="total", description="Get the total points of everybody towards the curent goal")
async def total(ctx):
    global CHALLENGERS
    try: 
        total = utilities.getOverallTotal(CHALLENGERS)
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")
        return
    await ctx.send(f"Total: {total}/{GOAL}")

@bot.hybrid_command(name="subtract", description="Subtract points from your total (in case you added more than you meant to or typoed)")
async def subtract(ctx, activity, points):
    global CHALLENGERS
    name = str(ctx.author)
    if( points < 0 ):
        await ctx.send("Value to subtract can't be negative")
        return
    if( activity not in utilities.getActivities(utilities.ACTIVITIES)):
        await ctx.send(f"Couldnt find an activity named {activity} in activity list. Supported activities are cardio and weights")
        return
    try: 
        activityTotal = subtractChallengerPoints(name, activity, points)
        newTotal = utilities.getChallengerTotal(CHALLENGERS, name)
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")
        return
    await ctx.send(f"Challenger {name} now has {activityTotal} {activity} points and {newTotal} total points")
        
@bot.hybrid_command(name="cardio", description="Log a cardio session (miles)")
async def cardio(ctx, miles):
    points = round(float(miles),2)
    name = str(ctx.author)
    activity = "cardio"
    try: 
        newTotal = updateChallengerPoints(name, activity, points)
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")
        return
    await ctx.send(f"{miles} mile cardio session worth {newTotal} points added to challenger {name}")

@bot.hybrid_command(name="weights", description="Log a weights session (minutes)")
async def weights(ctx, minutes):
    points = round(float(minutes)/60,2)
    name = str(ctx.author)
    activity = "weights"
    try: 
        newTotal = updateChallengerPoints(name, activity, points)  
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")
        return
    await ctx.send(f"{minutes} minute workout worth {newTotal} points added to challenger {name}")

@bot.hybrid_command(name="leaderboard", description="Get the current leaderboard")
async def leaderboard(ctx):
    global CHALLENGERS
    await ctx.send(utilities.getLeaderboard(CHALLENGERS))

@bot.hybrid_command(name="sync", description="Sync the commands on the server")
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Synced")

@bot.hybrid_command(name="refresh", description="Refresh the database")
async def refresh(ctx):
    global CHALLENGERS
    try:
        CHALLENGERS = utilities.readChallengersFile()
    except:
        await ctx.send("Something went wrong :(")
        return
    await ctx.send("Successfully refreshed database")

@bot.hybrid_command(name="modify", description="ADMIN ONLY: Modify a challenger's points")
async def sync(ctx, challenger, operation, activity, points):
    points = float(points)
    name = str(ctx.author)
    if( name not in ADMINS ):
        await ctx.send("Not authorized to use this command. If you want to change your own points use /cardio, /weights or /subtract")
    try:
        if( operation == "subtract" or operation == "sub" or operation == "-" or operation == "minus"):
            activityTotal = subtractChallengerPoints(challenger, activity, points)
            await ctx.send(f"Success, subtracted {points} points from challenger {challenger}. They have {activityTotal} points in {activity} now")
        if( operation == "add" or operation == "+"  or operation == "plus"):
            val = 0
            if( activity == "weights" ):
                val = points / 2
            else:
                val = points * 2
            updateChallengerPoints(str(challenger), activity, val)
            activityTotal = CHALLENGERS[activity][challenger]
            await ctx.send(f"Success, added {points} points to challenger {challenger}. They have {activityTotal} points in {activity} now")
    except:
        await ctx.send("Whoops that didn't work. Something went wrong on the backend :(")

#----------------------------------------------------------------------------
@tasks.loop(hours=24)
async def setupNewMonth():
    date = datetime.now()
    if date.day == 1:
        utilities.setupNewMonth()

@tasks.loop(hours=24)
async def saveBackup():
    date = datetime.now()
    day = str(date.day)
    month = str(date.month)
    year = str(date.year)
    dirname = os.path.dirname(__file__)
    try:
        src = os.path.join(dirname, "challenges", f"{utilities.CHALLENGE}.csv")
        dst = os.path.join(dirname, "backups", f"{utilities.CHALLENGE}-{day}-{month}-{year}.csv")
        shutil.copy(src, dst)
    except:
        print("Failed saving backup")

#----------------------------------------------------------------------------
token = open("token.json")
bot.run(json.load(token)["token"])