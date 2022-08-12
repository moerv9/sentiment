# Backend with Heroku

## Why Heroku?
Tweepy uses two ways of searching for tweets: Searching through the history or listening to real-time tweets.
One approach would be to schedule a task, p.e. for every hour, that searches the history of tweets and does the trading afterwards. However, after looking closer into the Documentation, it was discovered that the search service with the Twitter API doesn't show all available tweets. This would lead to incomplete data, which would deflect the strategy and therefore wasn't an option.

When listening to real-time tweets, the python script needs to run the whole time in the background. It is no option to only run it on the local machine when it is intended to run for days or weeks. When the laptop is closed, the script stops running.

That is where cloud platforms as services come in handy. Today, most of the SaaS-products run in some sort of cloud since it is not very desirable for smaller companies to run and maintain servers for their clients when other bigger corporations such as Google, Amazon or Microsoft offer better, more scalable and cheaper services.

For this project [Heroku](https://www.heroku.com/) was the used cloud provider, because it works well with Python, has a free tier available and an easy-to-use Postgres Add-On and GitHub Continuous Integration.

Heroku works with containerization: Heroku automatically detects a change in the GitHub Repository and starts a new Deployment. Because this did not always work, it is still possible to manually deploy in the Heroku Dashboard or with the Heroku CLI.

Heroku will then package the code and dependencies and runs it in lightweight, scalable and isolated containers. Heroku calls their containers *dynos*.
In the free tier you have free 550 Dynos a month and each time a web service is called or a worker is run a dyno is consumed. 



## Setting up Heroku
1. Create App and initialize Heroku git

#TODO: insert images
![heroku: create app](/img/heroku/heroku_create_app.png)

![heroku: init git](/img/heroku/heroku_init_git.png)



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

Add Procfile to main folder and add the following line: 

```
worker: python3 sentiment/runner.py
```



## Saving Tweets to Postgres Database
#TODO

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



