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

    CHALLENGE_PREV = f"{YEAR_PREV}-{MONTH_PREV}"
    CHALLENGE_PREV_FILE = os.path.join("challenges", CHALLENGE_PREV + ".csv")

    ACTIVITIES = readActivitiesFile()

init()

#------ PANDAS OPERATIONS ----------------------------------------------------
def getChallengerTotal(dataframe, name):
    df = dataframe.copy(deep=True)
    df['Total'] = df.sum(axis=1, numeric_only=True)
    try:
        total = df["Total"][name]
    except:
        return -1
    return total

def getLeaderboard(dataframe):
    df = dataframe.copy(deep=True)
    df['Total'] = df.loc[:, df.columns != "Total"].sum(axis=1, numeric_only=True)
    df = df.sort_values(by="Total", ascending=False)
    index = df.index
    idx = []
    for i in index:
        i = i[:-5] # strip off the #0001 at the end of everyone's names
        idx.append(i)
    df2 = df.reindex(idx) # create a new df with these new indices
    df2["Running"] = df["Running"].values
    df2["Weights"] = df["Weights"].values
    df2["Total"] = df["Total"].values
    
    return '```' + df2.to_string() + '```'

def getOverallTotal(dataframe):
    df = dataframe.copy(deep=True)
    df['Total'] = dataframe.sum(axis=1, numeric_only=True)
    return df['Total'].sum()

def addChallenger(dataframe, name):
    df = dataframe.copy(deep=True)
    series = pd.Series(dict(zip(df.columns,[0] * df.shape[1]))).rename(name)
    df = dataframe.df(series)
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
    if( exists(GOAL_FILE) ):
        df = pd.read_csv(GOAL_FILE, index_col=0)
        return df["Goal"][CHALLENGE_PREV]

#------ GENERIC OPERATIONS ----------------------------------------------------
def save(dataframe, file):
    dataframe.to_csv(file)

def isNewMonth():
    if(exists(CHALLENGE_FILE)):
        return False
    else:
        return True

def setupNewMonth():
    if(isNewMonth()):
        # reset the leaderboard
        df = readChallengersFile()
        df = df[0:0]
        
        # get last month's goal dataframe
        goal = getCurrentGoal()
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

def isEmpty(dataframe):
    if( len(dataframe.index) == 0 ):
        return True
    else: 
        return False
