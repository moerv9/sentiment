# Data Acquisition 

## Retrieving and Processing of Tweets with the Twitter API
Instead of dealing with HTTP Requests, Data Serialisation and Rate Limits it is easier to use pre-built libraries to access the Twitter API and be able to focus more on building functionality. There are hundreds of different libraries, but I've found two to be standing out and compared them: Twint and Tweepy.

| **Library**          | **Twint**                                                                   | *Tweepy*                                                                            |
|------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **Twitter API** | No authentification with official Twitter API necessary.                | Auth. with Twitter API needed                                                     |
| **Limits**           | No limits on search for last tweets                                     | Search tweets as early as 2006                                                    |
| **Development**      | 12,7k Stars on Github with 845 commits (last Commit in March 2021)      | 8,6k Stars on Github with 2914 commits (last Commit: 25.03.2022)                  |
| **Documentation**    | Minimal, Not many Tutorials                                             | Big, updated and easy to understand documentation and a lot of tutorials          |
| **Purpose**          | Good for grabbing Tweets from the past, not for posting or sending DM's | Everything what the Twitter API allows: From Scraping to Tweeting to Sending DM's |
|                  |                                                                         |                                                                                   |

Twint seems to have the upper hand because it does not need an authentication and has good filters for tweets (even Cashtag filter). I wrote a simple test to acquire some tweets with Twint, but a few days later this didn't work any longer. It appears that Twint wasn't retrieving any data any longer. 
I cannot say now if this will work later on but since the GitHub hasn't been updated in more than a year and others had this issue as well, I will just use Tweepy.

Getting authorized from Twitter was easy. Login to the [Twitter Developer Portal](developer.twitter.com) and create a new Project and App. There you can generate and copy the necessary token: API Key, API Secret, Access Token and Access Secret. The Twitter API also released a Version 2 which is able to authorize using only a bearer token.

Authorization and searching for Tweets with Tweepy is simple:
```
import tweepy
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
posts_for_elon_musk = api.user_timeline(screen_name="elonmusk", count=5,tweet_mode = "extended")
print(posts_for_elon_musk)
```

Output:
> #### Elon Musk's latest Tweets:
> 1)  The ratio of digital to biological compute is growing fast. Worth tracking.
> 2) Just came across this pretty good CNBC piece on SpaceX &amp; Starship https://t.co/RELYzC40M9
> 3) Tesla + Twitter = Twizzler
> 4) A new philosophy of the future is needed. I believe it should be curiosity about the Universe – expand humanity to become a multiplanet, then interstellar, species to see what’s out there.
> 5) The media is a click-seeking machine dressed up as a truth-seeking machine

---
### What does the Law say?

The EU General Data Protection Regulation, or GDPR only applies to personal data.

Here, "personal data" refers to the data that could be used to directly or indirectly identify a specific individual. This kind of information is known as Personally Identifiable Information (PII), which includes a person's name, physical address, email address, phone number, IP address, date of birth, employment info and even video/audio recording.
If you aren't scraping personal data, then GDPR does not apply.

If you are not scraping in the EU you are good to go.
([Source](https://www.octoparse.com/blog/gdpr-compliance-in-web-scraping))

---

### Retrieving Tweets with Tweepy



#TODO: how i did it and first filter for keywords

### Filter Tweets 
We want the data to be significant, which means we don't want Tweets from Bots in our list since they are repeating the same thing over and over and deflect the overall opinion.

But what differentiates a tweet by a bot from a tweet by a human?
1. Bots often retweet
2. Bot Accounts are created quite often thus fairly new to the platform
3. Bots (especially when new) have little following
4. They often offer giveaways or free coins 
5. They repeat themselves... a lot

Accounts with less than 500 followers or when they have just been created in the last two months are filtered out. Also Retweets and Tweets that contain blacklisted Words like *Giveaway, Free or Gift*.

The next step is cleaning the tweet itself. 
Most often a tweet can contain a lot of characters like *underscores, hashtags or emojis* and special characters like *"&amp"* (which is used in Html entities for a normal "&"-Symbol. There was one in one of Elon Musks Tweet [above](#elon-musks-latest-tweets)).

I've built a function to clean it using regex. This is an excerpt from the `cleanTweets`-Function in the [filter.py](#TODO:link filter.py) file:
```
text = re.sub(r'@[A-Za-z0-9]+',"",text,flags=re.IGNORECASE) 
text = re.sub(r'_*|\+*',"",text) # removes _ and +
text = re.sub(r'&amp;*|&amp|amp',"",text) 
text = demoji.replace(text, "") 
cleaned_words = [x for x in words if not bool(re.search('^[0-9]+$|^$', x))]
```
With `re.sub` you can substitute the text you don't want. 
The first three lines remove the "@", "_", "+" and different variations of "amp" (You can find it in the second Tweet from Elon Musk in the output above)
All these are substituted with empty strings which are being removed in the last line. The last line also cleans alone standing numbers like "734982" but leaves numbers with characters in the string like "$20k".

As an example, this is a tweet before cleaning:

> "_boii &amp people think is high now wait till it’s $20k + by the end of this week $50k+ by end of 734982 this month  y’all should follow  he's    a super underrated !bitcoiner i’ve been :following her tweets  and tips seriously  i’ve  been doing really great! #btc #ada"

After cleaning, it looks like this:
> "boii people think is high now wait till it’s $20k by the end of this week $50k by end of this month y’all should follow hes a super underrated bitcoiner i’ve been following her tweets and tips seriously i’ve been doing really great"


---

The next thing is to find and delete all the duplicates:

<img src=./img/sentiment/duplicatetweets.png width=900/>
As can be seen in the picture above, the same tweet was tweeted 10 times in one minute. It is the exact same tweet and it kept on tweeting for quite a bit. Since this is oviously a bot I need to filter out these duplicates.

At first, I did that by adding the collected tweets to a list, and after the list had 40 items, run a function that checks for duplicates and deletes them. I choose 40 items because there were approximately 40 tweets in a minute.

The following function converts the list to a Pandas Dataframe and checks for duplicate Tweets with their innate `duplicated()`-method. I added the `keep=False`-parameter because I don't want any of these tweets to be included in the sentiment analysis. 

    def check_duplicates(tweet_list):
        cols = ["Tweet", "Keyword", "Time", 
                "Location","Verified","Followers",
                "User created", "Sentiment Score"]
        df = pd.DataFrame(tweet_list,columns=cols)
        duplicates = list(df.index[df.duplicated(subset=["Tweet"],keep=False)])
        df.drop(labels=duplicates,inplace=True)
        return df.values.tolist()

Unfortunately this lead to the following problem:

Firstly, even though this function found and deleted some duplicates nearly every time it was called, checking only 40 tweets at a time is not sufficient to delete **all** duplicates.

This is why I decided not to use this function before inserting the tweets but instead apply it later when reading the whole database. 
When applying this function once, it deleted 774 duplicates from a total of 5622 tweets. That's about 14%. That's massive. This would've distorted the calculation of the sentiment significantly. 
