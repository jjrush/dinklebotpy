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
    weight = utilities.getWeight(activity)
    total = float(points) * float(weight)

    CHALLENGERS[activity][name] = total
    utilities.save(CHALLENGERS, utilities.CHALLENGE_FILE)

    CHALLENGERS = utilities.readChallengersFile()
    return CHALLENGERS[activity][name]

#----------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} : {bot.user.id}')
    print('------')

@bot.command(name="changeGoal")
async def changeGoal(ctx, goal):
    global GOAL
    utilities.changeGoal(utilities.readGoalFile(), goal)
    GOAL = utilities.getCurrentGoal()
    await ctx.send(f"Goal updated to {GOAL}")

@bot.hybrid_command(name="goal")
async def goal(ctx):
    global GOAL
    GOAL = utilities.getCurrentGoal()
    await ctx.send(f"Goal for {utilities.CHALLENGE}: {GOAL} pts")

@bot.hybrid_command()
async def points(ctx):
    name = str(ctx.author)
    points = utilities.getChallengerTotal(name)
    await ctx.send(f"User {name} has {points} this challenge")

@bot.hybrid_command(name="total")
async def total(ctx):
    name = str(ctx.author)
    total = utilities.getChallengerTotal(CHALLENGERS, name)
    if(total != -1):
        await ctx.send(f"Total: {total}/{GOAL}")
    else:
        await ctx.send(f"Sorry, challenger {name} not found")

@bot.hybrid_command(name="hello")
async def hello(ctx):
    await ctx.send("Hello! :)")

@bot.hybrid_command(name="run")
async def run(ctx, points):
    name = str(ctx.author)
    activity = "Running"
    newTotal = updateChallengerPoints(name, points, activity)
    await ctx.send(f"Adding {points} to challenger {name}. You now have {newTotal} points towards this challenge")

@bot.hybrid_command(name="weights")
async def weights(ctx, points):
    name = str(ctx.author)
    activity = "Weights"
    newTotal = updateChallengerPoints(name, points, activity)  
    await ctx.send(f"Adding {points} to challenger {name}. You now have {newTotal} points towards this challenge")


#----------------------------------------------------------------------------
token = open("token.json")
bot.run(json.load(token)["token"])