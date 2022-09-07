from calendar import month
from logging import exception
import os
from os.path import exists
import sys
import json
import datetime
import pandas as pd

#------ FILE OPERATIONS ----------------------------------------------------
def readChallengersFile():
    if( exists(CHALLENGE_FILE) ):
        return pd.read_csv(CHALLENGE_FILE, index_col=0)
    else:
        df = pd.read_csv(CHALLENGE_PREV_FILE, index_col=0)
        return df[0:0]

def readActivitiesFile():
    if( exists(ACTIVITIES_FILE) ):
        return pd.read_csv(ACTIVITIES_FILE, index_col=0)
    return

def readGoalFile():
    if( exists(ACTIVITIES_FILE) ):
        return pd.read_csv(GOAL_FILE, index_col=0)
    return

#------ SETUP ----------------------------------------------------
YEAR = ""
MONTH = ""
YEAR_PREV = ""
MONTH_PREV = ""
CHALLENGE = ""
CHALLENGE_FILE = ""
CHALLENGE_PREV = ""
CHALLENGE_PREV_FILE = ""
ACTIVITIES = ""
ACTIVITIES_FILE = "activities.csv"
GOAL_FILE = "goals.csv"

def init():
    global YEAR
    global MONTH
    global YEAR_PREV
    global MONTH_PREV
    global ACTIVITIES
    global CHALLENGE
    global CHALLENGE_FILE
    global CHALLENGE_PREV
    global CHALLENGE_PREV_FILE

    YEAR = datetime.date.today().year
    MONTH = datetime.date.today().month
    YEAR_PREV = YEAR - 1
    MONTH_PREV = MONTH - 1

    if (MONTH_PREV == 0):
        MONTH_PREV = "12"
        YEAR_PREV = f"{YEAR - 1}"
    elif ( MONTH_PREV < 10):
        MONTH_PREV = f"0{MONTH_PREV}"

    if( MONTH < 10 ):
        MONTH = f"0{MONTH}"
    else:
        MONTH = f"{MONTH}"

    CHALLENGE = f"{YEAR}-{MONTH}"
    CHALLENGE_FILE = os.path.join("challenges", CHALLENGE + ".csv")

    if( MONTH_PREV == "12" ):
        CHALLENGE_PREV = f"{YEAR_PREV}-{MONTH_PREV}"
    else:
        CHALLENGE_PREV = f"{YEAR}-{MONTH_PREV}"
    CHALLENGE_PREV_FILE = os.path.join("challenges", CHALLENGE_PREV + ".csv")

    ACTIVITIES = readActivitiesFile()

init()

#------ PANDAS OPERATIONS ----------------------------------------------------
def getActivities(dataframe):
    return list(dataframe.index.values)

def getChallengerTotal(dataframe, name):
    df = dataframe.copy(deep=True)
    df['total'] = df.sum(axis=1, numeric_only=True)
    try:
        total = df["total"][name]
    except:
        return -1
    return total

def getLeaderboard(dataframe):
    df = dataframe.copy(deep=True)
    df['total'] = df.loc[:, df.columns != "total"].sum(axis=1, numeric_only=True)
    df = df.sort_values(by="total", ascending=False)
    index = df.index
    idx = []
    for i in index:
        i = i[:-5] # strip off the #0001 at the end of everyone's names
        idx.append(i)
    df2 = df.reindex(idx) # create a new df with these new indices
    df2["cardio"] = df["cardio"].values
    df2["weights"] = df["weights"].values
    df2["total"] = df["total"].values

    dflist =  df2.to_string().split('\n')
    dflist[0] = dflist[0].replace("    ","name", 1)
    dflist.pop(1)
    dfstr = ""
    for line in dflist:
        dfstr = dfstr + line + "\n"
    
    return '```\n' + dfstr + '\n```'

def getOverallTotal(dataframe):
    df = dataframe.copy(deep=True)
    df['total'] = df.sum(axis=1, numeric_only=True)
    return round(df['total'].sum(),2)

def addChallenger(dataframe, name):
    df = dataframe.copy(deep=True)
    series = pd.Series(dict(zip(df.columns,[0] * df.shape[1]))).rename(name)
    df = dataframe.append(series)
    save(df, CHALLENGE_FILE)
    return df

def changeGoal(dataframe, goal):
    df = dataframe.copy(deep=True)
    df["Goal"][CHALLENGE] = goal
    save(df, GOAL_FILE)

def getWeight(row):
    global ACTIVITIES
    return ACTIVITIES["Weighting"][row]

def getCurrentGoal():
    if( exists(GOAL_FILE) ):
        df = pd.read_csv(GOAL_FILE, index_col=0)
        return df["Goal"][CHALLENGE]

def getPreviousGoal():
    global GOAL_FILE
    global CHALLENGE_PREV
    if( exists(GOAL_FILE) ):
        df = pd.read_csv(GOAL_FILE, index_col=0)
        return df["Goal"][CHALLENGE_PREV]

def setupNewMonth():
    global CHALLENGE
    global CHALLENGE_FILE
    global GOAL_FILE
    
    # reset the leaderboard
    df = readChallengersFile()
    df = df[0:0]
    
    # get last month's goal dataframe
    goal = 0
    try:
        goal = getCurrentGoal()
    except:
        goal = getPreviousGoal()
    goalDf = pd.read_csv(GOAL_FILE, index_col=0)

    # refresh all of the globals
    init()

    # add a new row for this month's goal
    series = pd.Series(dict(zip(goalDf.columns,[0] * goalDf.shape[1]))).rename(CHALLENGE)
    goalDf = goalDf.append(series)
    goalDf["Goal"][CHALLENGE] = goal

    # save files
    save(goalDf, GOAL_FILE)
    save(df, CHALLENGE_FILE)

    if(exists(CHALLENGE_FILE)):
        return True
    return False
    
#------ GENERIC OPERATIONS ----------------------------------------------------
def save(dataframe, file):
    dataframe.to_csv(file)

def isNewMonth():
    if(exists(CHALLENGE_FILE)):
        return False
    else:
        return True

def isEmpty(dataframe):
    if( len(dataframe.index) == 0 ):
        return True
    else: 
        return False
