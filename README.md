# LatenessTracker
A flask based webserver to track and shame your coursemates for being late.
## Running LatenessTracker
To run the tracker, simply navigate to the `/LatenessTracker/` and run:
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
## Roadmap
Features to be added:
- ~~Login~~
- ~~Game creation~~
- Scoring
- Achievements
- Better CSS
- Easier navigation

## Known Bugs
- 