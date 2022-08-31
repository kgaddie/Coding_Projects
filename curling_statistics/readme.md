# Readme
## Project: Curling Team Statistics

### Description
This project involves the compilation of data from curling matches in the form of scoreboard results and the resultant dataframe of analytics provided by team. The calculations included inside will enable users/teams to see the trends in a variety of important aspects of the game, including (but not limited to): hammer efficiency, steal efficiency, steal defense efficiency, and average points scored aggregated by opponents, season, and in total overall performance history.

### Files Included
##### curling_data_formatting.ipynb
Curling Data Formatting takes the input dataset from users of scoreboards by end and compiles them into a useable format to calculate a vareity of statistics based on set parameters such as team, season, competition location, event type, and opponent. 

##### Curling_analytics.py
Curling Analytics outlines the requisite formulas required for ingesting the formatted dataframe and outputting the desired calculations for consideration through created python functions.

##### Curling Analytics Dashboard - Tableau
The Curling Analytics Dashboard is a sample version of a dashboard highlighting a team's performance over the course of four seasons. The dashboard shows a vareity of ways for viewing trends across seasons, areas of improvement for the team, and areas of decline for recommended areas of focus for teams to practice. 

##### Data
Included datasets here are a csv of sample responses from competitors and sample output of calculated analytics.

### Definition of Statistics
##### Hammer Efficiency (HE)
The percentage of time a team takes 2 or more points with hammer, in ends which are scored. Includes all non-blank ends in which a team has hammer.

##### Steal Defense (SD)
The ability to limit the number of stolen ends. Calculated byt he number of ends stolen against divided by ends with hammer. Blank ends are included. LOWER IS BETTER.

##### Hammer Factor (HF)
Found via the subtractino of Hammer Efficiency and Steal Defense

##### Force Efficiency (FE)
Calculated by number of ends in which the opponent took 1 point divided by all ends without hammer where the opponent scores. Stolen and blank ends are not included.

##### Steal Efficiency (SE)
Percentage of ends a team steals one or more points. Calculated by dividing ends stolen without hammer by total ends played without hammer. Blank ends are included.

##### Average Points Scored
Calculated by aggregating the sum of all points scored in the selected scope divided by number of games.

##### Average Points Allowed
Calculated by aggregating the sum of all points opponents scored in the selected scope divided by number of games.

##### Big Ends Scored
Defined by number of ends in which 4+ points were scored

##### Big Ends Allowed
Defined as the number of ends in which 4+ points were scored by the opponents
