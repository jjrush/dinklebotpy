import discord
from discord.ext import tasks, commands
import json
import utilities
from datetime import datetime

description = "Dinklebot"
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='$', description=description, intents=intents)
#----------------------------------------------------------------------------
CHALLENGERS = utilities.readChallengersFile()
GOAL = utilities.getCurrentGoal()

#----------------------------------------------------------------------------
def addChallenger(name):
    global CHALLENGERS
    CHALLENGERS = utilities.addChallenger(name)

def updateChallengerPoints(name, points, activity):
    global CHALLENGERS
    weight = utilities.getWeight(activity)
    total = float(points) * float(weight)

    CHALLENGERS[activity][name] = round(total + CHALLENGERS[activity][name],2)
    utilities.save(CHALLENGERS, utilities.CHALLENGE_FILE)

    CHALLENGERS = utilities.readChallengersFile()
    return total

#----------------------------------------------------------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    setupNewMonth.start()
    print(f'Logged in as {bot.user.name} : {bot.user.id}')
    print('------')

#----------------------------------------------------------------------------
@bot.hybrid_command(name="change", description="Changes the current challenge's total point goal")
async def change(ctx, goal):
    global GOAL
    utilities.changeGoal(utilities.readGoalFile(), goal)
    GOAL = utilities.getCurrentGoal()
    await ctx.send(f"Goal updated to {GOAL}")

@bot.hybrid_command(name="points", description="Get your total points in the curent challenge")
async def points(ctx):
    name = str(ctx.author)
    points = utilities.getChallengerTotal(CHALLENGERS, name)
    await ctx.send(f"User {name} has {points} points this challenge")

@bot.hybrid_command(name="total", description="Get the total points of everybody towards the curent goal")
async def total(ctx):
    total = utilities.getOverallTotal(CHALLENGERS)
    await ctx.send(f"Total: {total}/{GOAL}")

@bot.hybrid_command(name="subtract", description="Subtract points from your total (in case you added more than you meant to or typoed)")
async def subtract(ctx, activity, points):
    global CHALLENGERS
    name = str(ctx.author)
    points = int(points)
    activity = activity.lower()

    if( points < 0 ):
        await ctx.send("Value to subtract can't be negative")
        return
    if( activity not in utilities.getActivities(utilities.ACTIVITIES)):
        await ctx.send(f"Couldnt find an activity named {activity} in activity list. Supported activities are cardio and weights")
        return

    CHALLENGERS[activity][name] = round(CHALLENGERS[activity][name] - points, 2)
    utilities.save(CHALLENGERS, utilities.CHALLENGE_FILE)
    CHALLENGERS = utilities.readChallengersFile()
    
    activityTotal = CHALLENGERS[activity][name]
    newTotal = utilities.getChallengerTotal(CHALLENGERS, name)

    await ctx.send(f"Challenger {name} now has {activityTotal} {activity} points and {newTotal} total points")
        

@bot.hybrid_command(name="cardio", description="Log a cardio session (miles)")
async def cardio(ctx, miles):
    points = round(float(miles),2)
    name = str(ctx.author)
    activity = "cardio"
    newTotal = updateChallengerPoints(name, points, activity)
    await ctx.send(f"{miles} mile cardio session worth {newTotal} points added to challenger {name}")

@bot.hybrid_command(name="weights", description="Log a weights session (minutes)")
async def weights(ctx, minutes):
    points = round(float(minutes)/60,2)
    name = str(ctx.author)
    activity = "weights"
    newTotal = updateChallengerPoints(name, points, activity)  
    await ctx.send(f"{minutes} minute workout worth {newTotal} points added to challenger {name}")

@bot.hybrid_command(name="leaderboard", description="Get the current leaderboard")
async def leaderboard(ctx):
    await ctx.send(utilities.getLeaderboard(CHALLENGERS))

@bot.hybrid_command(name="sync", description="Sync the commands on the server")
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Synced")

#----------------------------------------------------------------------------
@tasks.loop(hours=24)
async def setupNewMonth():
    date = datetime.now()
    if date.day == 1:
        utilities.setupNewMonth()

#----------------------------------------------------------------------------
token = open("token.json")
bot.run(json.load(token)["token"])