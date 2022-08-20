import discord
from discord.ext import commands
import json
import utilities

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

    CHALLENGERS[activity][name] = round(total + CHALLENGERS[activity][name])
    utilities.save(CHALLENGERS, utilities.CHALLENGE_FILE)

    CHALLENGERS = utilities.readChallengersFile()
    return total

#----------------------------------------------------------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user.name} : {bot.user.id}')
    print('------')

@bot.hybrid_command(name="change", description="Changes the current challenge's total point goal")
async def change(ctx, goal):
    global GOAL
    utilities.changeGoal(utilities.readGoalFile(), goal)
    GOAL = utilities.getCurrentGoal()
    await ctx.send(f"Goal updated to {GOAL}")

@bot.hybrid_command(name="goal", description="Get the current challenge's total point goal")
async def goal(ctx):
    global GOAL
    GOAL = utilities.getCurrentGoal()
    await ctx.send(f"Goal for {utilities.CHALLENGE}: {GOAL} pts")

@bot.hybrid_command(name="points", description="Get your total points in the curent challenge")
async def points(ctx):
    name = str(ctx.author)
    points = utilities.getChallengerTotal(CHALLENGERS, name)
    await ctx.send(f"User {name} has {points} points this challenge")

@bot.hybrid_command(name="total", description="Get the total points of everybody towards the curent goal")
async def total(ctx):
    name = str(ctx.author)
    total = utilities.getChallengerTotal(CHALLENGERS, name)
    if(total != -1):
        await ctx.send(f"Total: {total}/{GOAL}")
    else:
        await ctx.send(f"Sorry, challenger {name} not found")

@bot.hybrid_command(name="hello", description="Say hello :)")
async def hello(ctx):
    await ctx.send("Hello! :)")

@bot.hybrid_command(name="run", description="Log a running session (miles)")
async def run(ctx, miles):
    points = float(miles)
    name = str(ctx.author)
    activity = "Running"
    newTotal = updateChallengerPoints(name, points, activity)
    await ctx.send(f"{miles} mile run worth {newTotal} points added to challenger {name}")

@bot.hybrid_command(name="weights", description="Log a weights session (minutes)")
async def weights(ctx, minutes):
    points = round(float(minutes)/60,2)
    name = str(ctx.author)
    activity = "Weights"
    newTotal = updateChallengerPoints(name, points, activity)  
    await ctx.send(f"{minutes} minute workout worth {newTotal} points added to challenger {name}")

@bot.hybrid_command(name="leaderboard", description="Get the current leaderboard")
async def leaderboard(ctx):
    await ctx.send(utilities.getLeaderboard(CHALLENGERS))

#----------------------------------------------------------------------------
token = open("token.json")
bot.run(json.load(token)["token"])