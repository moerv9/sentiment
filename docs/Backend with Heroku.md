# Backend with Heroku

## Why Heroku?
At first, I thought to only look back with the Twitter API and schedule this task for every minute or so. However, after looking closer into the Documentation, I quickly discovered that the search service with the Twitter API doesn't show all available tweets. This would lead to incomplete data, which would deflect the strategy and therefore wasn't an option.


## Steps
1. Create App and initialize Heroku git
#TODO: insert images
2. Add Heroku Postgres Add-On

[Heroku Postgres Documentation](https://devcenter.heroku.com/articles/heroku-postgresql)
3. Add Credentials from Postgres Settings to local .env file and Heroku config vars
This can be done either in the Settings in the Heroku Dashboard or via CLI:
    
```
heroku config:set DB_URL=postgresql://wjhgxflbnaygwb:65c900f1fb2e477ae1fa161e543db8b81d613fe7b8b6fbdb1f2e370bd07a6017@ec2-54-228-218-84.eu-west-1.compute.amazonaws.com:5432/db1m9hb4f699st
```

For SQLAlchemy to work we need to change the DB URL from `postgres://...` to `postgresql://...`

4. Connect to Heroku with DB URL and insert Datasets
```
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
```
[Explanation from Heroku Docs](https://devcenter.heroku.com/articles/connecting-heroku-postgres)

## Running Script in the Background
Heroku works with containerization: I only need to deploy my app from Github or with the Heroku CLI and Heroku will package the code and dependencies and runs it in lightweight, scalable and isolated containers. Heroku calls their containers *dynos*.
Dynos are needed to execute the code and I will use it to 

Add Procfile to main folder and add the following line: 

```
worker: python3 sentiment/runner.py
```



## Saving Tweets to Postgres Database


## Challenges and Solutions
### Connecting with Heroku

### Row Limit of 10000 
The Free Hobby Plan for Heroku Postgres Database has a limit of 10000 rows and it got filled very quickly. The database was filled in 5h.
But nothing happened. A week passed and the database was filling up until I got an email from Heroku: 
<img src=./img/heroku//heroku_email_databasefull.PNG width=300 alt="Email from Heroku: Database Full"/> 

The Heroku Database got filled such quickly because I was collecting Tweets about Bitcoin and Cardano.
It would be very interesting to compare different coins side by side, but I decided to only look at Bitcoin after this point, so I can gather more Tweets.
In the end this was a waste of time because Chainsulting was so kind and upgraded the Heroku Database Plan. Now with a row limit of 10M, which should last for about a month of Tweets.
Of course, this can be improved by better filters 



