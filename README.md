# LatenessTracker
A flask based webserver to track and shame your coursemates for being late.
## Running LatenessTracker
To run the tracker, simply navigate to the `./LatenessTracker/` and run:
```
flask --app flaskr run --debug
```
If you want to host it locally, instead run:
```
flask --app flaskr run --debug --host=0.0.0.0
```
First time you run the application, you should run to build the database:
```
flask --app flaskr init-db
```
The same command resets the database (**This will delete users and passwords**)

If you want to run custom SQL-insertions or -updates (or anything else, where you do not need the output) edit the `run.sql`-file and run it with:
```
flask --app flaskr sql_file  
```

## Roadmap
### Need-to-have
- ~~Login~~
- ~~Game creation~~
- Scoring
- Easier navigation
- If a person with a game against them arrives on time, they are awarded points
- Toggle academic quarter

### Nice-to-have
- Achievements
- Better CSS
- Leaderboard (most points, most won games, most lates)

## Known Bugs
- can click "join game" more than once
- ~~guesses can be added after the fact~~
- ~~Clicking refresh on the win-page gives +1 point to the winner~~
