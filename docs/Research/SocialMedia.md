# Social Media Analysis


---

### Python Libraries for easy-to-use Access of the Twitter API

Instead of dealing with HTTP Requests, Data Serialisation and Rate Limits it is easier to use pre-built libraries to focus building the functionality. There are hundreds of different libraries but I've found two to be standing out and compared them: Tweepy vs. Twint.

**Twint**
* Does not need access to the official Twitter API and no Authentication
* No limits on tweets
* 12,7k Stars on Github with 845 commits (last Commit in March 2021)
* Meant for grabbing tweets not for posting or sending DMs
* Minimal documentation and not many tutorials

**Tweepy**
* uses Twitter API 
* Limits to last 3200 Tweets
* 8,6k Stars on Github with 2914 commits (last Commit: 25.03.2022)
* A lot of tutorials and good documentation 

Twint seems to have the upper hand because it does not need an authentication and has good filters for tweets (even cashtag filter). I wrote a simple test to acquire some tweets with Twint but a few days later this didn't work any longer. It appears that Twint can't retrieve any data. Look at [this](../jupyter_notebooks/SavedCodeSnippets.ipynb#Test-Twint). 
I cannot say now if this will work later on but since the Github hasn't been updated in more than a year I will just use Tweepy.

Getting authorized from Twitter was easy. Login to the [Twitter Developer Portal](developer.twitter.com) and create a new Project and App. There you can generate and copy the neccessary token: API Key and Secret, Bearer Token for Twittert API V2 and the Access Token and Secret. The other four are needed for the Twitter API V1.  


Authenticating with the Twitter API via Tweepy is easy as can be seen in one of my example Notebooks, to... [Get Tweets from Elon Musk](../jupyter_notebooks/getElonsTweets.ipynb).

---

### What does the Law say?

The EU General Data Protection Regulation, or GDPR only applies to personal data.
 
Here "personal data" refers to the data that could be used to directly or indirectly identify a specific individual. This kind of information is known as Personally Identifiable Information(PII), which includes a person's name, physical address, email address, phone number, IP address, date of birth, employment info and even video/audio recording.
If you aren't scraping personal data, then GDPR does not apply.

If you are not scraping EU you are good to go.
([Source](https://www.octoparse.com/blog/gdpr-compliance-in-web-scraping))

