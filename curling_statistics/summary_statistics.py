# Curling Game Summary Statistics Script Generator

######################
## Import Libraries ##
######################

import pandas as pd
import tkinter as tk
from tkinter import simpledialog

##########################
## Creating User Inputs ##
##########################

#Single input

ROOT = tk.Tk()

ROOT.withdraw()

# Simple Input Variables

seasons = simpledialog.askstring(title="Season",
                                  prompt="What curling season did the game occur in? YYYY-YYYY:")
date = simpledialog.askstring(title="Date",
                                  prompt="What day was game played? Format - MM/DD/YYYY:")
game_type = simpledialog.askstring(title="Game Type",
                                  prompt="What type of game? Playdown/League/Bonspiel/Nationals/Scrimmage:")
location = simpledialog.askstring(title="Game Location",
                                  prompt="What club did game occur in?:")
event_name = simpledialog.askstring(title="Event Name",
                                  prompt="What is the event name?:")
team_name = simpledialog.askstring(title="Team Name",
                                  prompt="What is your Team Name?:")
opp_name = simpledialog.askstring(title="Opposition Name",
                                  prompt="What is the Opposition's Team Name?:")
opposition_team_type = simpledialog.askstring(title="Opposition Team Type",
                                  prompt="What is the Opposition Team Type? Mens/Womens/Mixed:")
sheet = simpledialog.askstring(title="Sheet",
                                  prompt="What Sheet did you play on:")
planned_ends = simpledialog.askstring(title="Planned Ends",
                                  prompt="How many ends planned?:")
played_ends = simpledialog.askstring(title="Played Ends",
                                  prompt="How many ends were played?:")
ends_won = simpledialog.askstring(title="Ends Won",
                                  prompt="How many ends did you win?:")
ends_lost = simpledialog.askstring(title="Ends Lost",
                                  prompt="How many ends did you lose?:")
ends_blanked = simpledialog.askstring(title="Blanked Ends",
                                  prompt="How many ends were blanked?:")
points_scored = simpledialog.askstring(title="Points Scored",
                                  prompt="How many points did your team score?:")
points_allowed = simpledialog.askstring(title="Points Allowed",
                                  prompt="How many points did the opposition score?:")
uni = simpledialog.askstring(title="Uniform Worn",
                                  prompt="What Uniform did your team wear?:")
stone_color = simpledialog.askstring(title="Stone Color",
                                  prompt="What is your stone color?:")
hammer_start = simpledialog.askstring(title="Hammer Start",
                                  prompt="Did you start with Hammer? Y,N,NA:")
game_outcome = simpledialog.askstring(title="Game Outcome",
                                  prompt="What is the Game Outcome? Win/Loss/Tie:")

########################################
## Generate Row of Data for Appending ##
########################################

cols = ["Season","Date","Game Type","Location","Event Name","Team Name","Opposition Name",
           "Opposition Team Type", "Sheet","Planned Ends","Played Ends","Ends Won","Ends Lost",
           "Blanked Ends","Points Scored","Points Allowed","Uniform","Stone Color",
           "Started with Hammer?","Win/Loss","Played","Point Differential"]
play = "Y"
diff = int(points_scored) - int(points_allowed)
varbs = [seasons, date, game_type, location, event_name, team_name, opp_name,
         opposition_team_type, sheet, planned_ends, played_ends, ends_won, ends_lost,
         ends_blanked, points_scored, points_allowed, uni, stone_color, 
         hammer_start, game_outcome, play, diff]
tmp = pd.DataFrame([varbs] ,columns = cols)

dat = pd.read_excel('Summary Stats.xlsx')
dat = dat.append(tmp,ignore_index = True)
dat["Uniform"] = dat["Uniform"].fillna("NA")
dat.to_excel('Summary Stats.xlsx', index = False)


