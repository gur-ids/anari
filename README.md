This is a NHL meik mani application

# Prerequisites

Install requirements with:

```
python -m pip install --user -r requirements.txt
```

Run the app from folder where app.py resides (relative resource location) with

```
cd ./anari/anari/
python app.py
```

Open http://localhost:4200 to view it in the browser.

# A. Title of the project

NRI data analysis

# B. Elevator pitch [max 400 characters]

Basic info of NHL: players are hired from team's budget (cap hit) which is same for all teams. Use cases are related to how should we hire players and are players worth the money:

1. Calculate which players are worth the money (won games, points scored)
2. Which general managers are good in making teams?
3. Based on 2. who should you bet on
4. Is there/how strong is correlation of 1?
5. What makes a well-balanced team ratio of expensive and cheap players?
6. Did the player play better season than his average and why, that is, is PAX > 0?
7. Check how salary variance of a team reacts to team points?
8. Player position salary statistics
9. Give an estimate to what a player's salary should be

# C. Data: sources, wrangling, management

Player Source: http://www.hockeyabstract.com/testimonials
Team source: http://www.nhl.com/stats/team?reportType=season&seasonFrom=20172018&seasonTo=20172018&gameType=2&filter=gamesPlayed,gte,1&sort=points,wins

For wrangling and management, we use Python and Pandas.

The data does not contain a lot of missing values but we will impute missing values. For the columns we are interested, only Salary and Cap Hit has missing values, which were easy to fill manually. Missing draft year and round means the player was not drafted, but the team made a contract directly to the player.
Player position has been modified to have only a single value and the reason for this is that player position does not vary much e.g a left field attacked cannot also be a defender but can be a central attacker.
Data is season-by-season which means that it does not contain information about the contract, such as, the length and expiry year.

- consider player position (attacker, defender, goalee)
- consider time on ice
- consider players who have played in many teams
- some data might be already pre-calculated in the sheet

# D. Data analysis: statistics, machine learning

TBD

# E. Communication of results: summarization & visualization

The project uses Plotly Dash for visualization and reporting the results.

# F. Operationalization: creating added value, end-user point of view

We will make (at least) millions or (most likely) billions. Sports analysis is always in high demand.
