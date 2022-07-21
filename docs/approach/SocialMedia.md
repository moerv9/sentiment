# Social Media Analysis

Which ones are even interesting?
- Twitter
- Facebook
- Instagram
- Reddit

Why not Facebook, Instagram & Reddit?
Facebook disallows nearly every scraping or collection of data ([Read this](https://www.octoparse.com/blog/5-things-you-need-to-know-before-scraping-data-from-facebook)) and has shown to be a platform where a lot of complaints and hate exists. Moreover, well-known personalities, like Presidents or CEO's, are more likely to be found on Twitter.

Instagram is being used for showing your life with pictures rather than sharing your opinion on particular topics. Analysing pictures for sentiment is rather laborious. It is also not the top choice for giving and getting opinions on particular topics.

Reddit is a good choice for gathering sentiment and has been quite popular amongst traders. Especially since it made the headlines when the reddit members of the room r/wallstreetbets with their 4.8m members (2021, 2022: 11.8m members) came together and bought stocks like crazy. 

> "Prompted by the information posted on social media retail investors began buying these so called “meme-stocks” including GameStop, AMC Entertainment, Blackberry, and Nokia. The activity sent their prices soaring, with the GameStop share prices climbing over 1000% in just two weeks." [Source](https://www.thetradenews.com/the-reddit-revolt-gamestop-and-the-impact-of-social-media-on-institutional-investors/)


But for gathering sentiment automatically it has the same problem as Instagram: A lot of pictures.

Twitter is perfect. A lot of Users, including well-known Personalities, who are talking about different topics in a somewhat appropriate manner. Twitter offers a well written Documentary and easy-to-use libraries for Python.

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

Authenticating with the Twitter API via Tweepy is easy as can be seen in all the Tweepy Notebooks (like [Get Tweets from Elon Musk](../jupyter_notebooks/getElonsTweets.ipynb)).

---

### What does the Law say?

The EU General Data Protection Regulation, or GDPR only applies to personal data.
 
Here "personal data" refers to the data that could be used to directly or indirectly identify a specific individual. This kind of information is known as Personally Identifiable Information(PII), which includes a person's name, physical address, email address, phone number, IP address, date of birth, employment info and even video/audio recording.
If you aren't scraping personal data, then GDPR does not apply.

If you are not scraping EU you are good to go.
([Source](https://www.octoparse.com/blog/gdpr-compliance-in-web-scraping))

