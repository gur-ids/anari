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
7. check how salary variance of a team reacts to team points?
8. player position salary statistics
9. give an estimate to what a player's salary should be

# C. Data: sources, wrangling, management

Source: http://www.hockeyabstract.com/testimonials

For wrangling and management, we use Python and Pandas.

The data does not contain a lot of missing values but we will impute missing values. For the columns we are interested, only Salary and Cap Hit has missing values, which were easy to fill manually. Missing draft year and round means the player was not drafted, but the team made a contract directly to the player.

Data is season-by-season which means that it does not contain information about the contract, such as, the length and expiry year.

# D. Data analysis: statistics, machine learning

TBD

# E. Communication of results: summarization & visualization

The project uses Plotly Dash for visualization and reporting the results.

# F. Operationalization: creating added value, end-user point of view

We will make (at least) millions or (most likely) billions. Sports analysis is always in high demand.
