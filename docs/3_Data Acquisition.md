# Data Acquisition 
</br>

## Retrieving and Processing of Tweets with the Twitter API
The development phase starts with the acquisition of data from Twitter, as being stated in the *Must-Have*-Requirements (compare [[FR 10]](/2_Concept.md#must-have)).
Instead of dealing with HTTP Requests, Data Serialisation and Rate Limits it is easier to use pre-built libraries to access the Twitter API and be able to focus more on building functionality. There are hundreds of different libraries, but I've found two to be standing out and compared them: Twint and Tweepy.

| **Library**          | **Twint**                                                                   | **Tweepy**                                                                       |
|------------------|-------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **Twitter API** | No authentification with official Twitter API necessary.                | Auth. with Twitter API needed                                                     |
| **Limits**           | No limits on search for last tweets                                     | Search tweets as early as 2006                                                    |
| **Development**      | 12,7k Stars on Github with 845 commits (last Commit in March 2021)      | 8,6k Stars on Github with 2914 commits (last Commit: 25.03.2022)                  |
| **Documentation**    | Minimal, Not many Tutorials                                             | Big, updated and easy to understand documentation and a lot of tutorials          |
| **Purpose**          | Good for grabbing Tweets from the past, not for posting or sending DM's | Everything what the Twitter API allows: From Scraping to Tweeting to Sending DM's |
|                  |                                                                         |                                                                                   |

Twint seems to have the upper hand because it does not need an authentication and has good filters for tweets (even Cashtag filter). Acquiring some tweets with Twint was done in a few lines of code, but a few days later this didn't work any longer. It appears that Twint wasn't retrieving any data any longer. 
This could've been a temporary problem and may work later on, but since their GitHub hasn't been updated in more than a year and others had this issue as well, Twint no longer seemed as a good option. 

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

</br>

---
### What does the Law say?

The EU General Data Protection Regulation, or GDPR only applies to personal data.

Here, "personal data" refers to the data that could be used to directly or indirectly identify a specific individual. This kind of information is known as Personally Identifiable Information (PII), which includes a person's name, physical address, email address, phone number, IP address, date of birth, employment info and even video/audio recording.
If you aren't scraping personal data, then GDPR does not apply.

If you are not scraping in the EU you are good to go.
([Source](https://www.octoparse.com/blog/gdpr-compliance-in-web-scraping))

</br>

---

</br>

## Retrieving Tweets with Tweepy

Using the [Stream](https://docs.tweepy.org/en/stable/stream.html) Class from Tweepy allows filtering and sampling of realtime Tweets with the Twitter API.

A Listener for certain keywords is initiated and every time a tweet contains these keywords, it is collected. 

This default dictionary contains the keywords that filter the tweets for each coin:

    default_keyword_dict = {
                "btc":["$btc","#btc","bitcoin","#bitcoin"],
                "ada":["#ada","$ada","cardano"],
                "eth":["#eth","$eth","ether","ethereum","etherum"],
                "bnb":["#bnb","$bnb","binance coin"],
                "xrp":["#xrp","$xrp","ripple"]}

The keyword class builds a list of keywords from above dictionary and combines the single lists, so it is possible to filter for multiple coins at the same time.

It also contains the method to search through each word in the tweet for the keywords.

</br>



### Tweet Metrics
I am not only collecting the tweet but some other information/metrics about the tweet or the user: 
| Timestamp           | id    | Tweet                                                                                                                                                                                                           | Keyword | Location            | User verified | Followers | User created        | Sentiment Score |
|---------------------|-------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|---------------------|---------------|-----------|---------------------|-----------------|
| 2022-08-04 11:54:37 | 25708 | $btc support holding for now                                                                                                                                                                                    | $btc    | Egypt Lake-Leto, FL | False         | 972       | 2021-11-27 14:20:42 | 0.4019          |
| 2022-08-04 11:54:34 | 25707 | scalpers its very simple #bitcoinwhat are you betting on                                                                                                                                                        | bitcoin | Everywhere          | False         | 36598     | 2016-08-02 14:31:10 | 0.0             |
| 2022-08-04 11:54:34 | 25706 | he need to focus on his #bitcoin investment                                                                                                                                                                     | bitcoin | Ivory Coast         | False         | 786       | 2020-06-04 10:55:58 | 0.0             |
| 2022-08-04 11:54:25 | 25704 | who wants a #bitcoin update video hit up that like button                                                                                                                                                       | bitcoin | Magic Internet Bank | False         | 3810      | 2021-02-11 15:29:52 | 0.3612          |
| 2022-08-04 11:54:15 | 25703 | picture perfectthe $4250 resistance will be hard to break thoseeing a small retracement from hereif $btc $eth behave and hopefully pump we may see another ~50% pump from here for $metis as well to around $65 | $btc    |                     | False         | 505       | 2022-03-14 15:14:53 | 0.7964          |
|

</br>

Using the Location to filter for different timezones, so it is possible to enable the bot at different places at different times. It would be more efficient to collect tweets p.e. from America when most people are awake and able to tweet and not asleep. The problem is that the Location is not automatically read and set by Twitter, but rather manually set by the user. This means it is nearly useless to filter it since some tweets are from *"Everywhere"* or from the *"Magic Internet Bank"*, as can be seen in the table above.

For the tweet the timestamp, the found keyword and the calculated sentiment are included. More about sentiment in [this](/5_Sentiment.md) section.

The information about the user includes their follower base, when the user was created and if they are verified. No personal information with which one can conclude the identity of the person is acquired.

These metrics are collected to filter the tweets, so we have more high quality data at hand.

</br>

---

</br>

## Filter Tweets 
The data needs to be as significant as it can be, which means Tweets from Bots should not be included since they are deflecting the overall opinion by spreading the **exact** same opinion/tweet repeatedly. Applying filters is increasing the quality of the final product [FR 50].

But what differentiates a tweet by a bot from a tweet by a human?
1. Bots often retweet
2. Bot Accounts are created quite often thus fairly new to the platform
3. Bots (especially when new) have little following
4. They often offer giveaways or free coins 
5. They repeat themselves... a lot

Accounts with less than 500 followers or when they have just been created in the last two months are filtered out. Also Retweets and Tweets that contain blacklisted Words like *Giveaway, Free or Gift*.

The next step is cleaning the tweet itself. 
Most often a tweet can contain a lot of characters like *underscores, hashtags or emojis* and special characters like *"&amp"* (which is used in Html entities for a normal "&"-Symbol. There was one in one of Elon Musks Tweet [above](#elon-musks-latest-tweets)).

With the help of regex functions it can be done to filter and substitute words or symbols that are not useful. This is an excerpt from the `cleanTweets`-Function in the [filter.py](#TODO:link filter.py) file:
```
text = re.sub(r'@[A-Za-z0-9]+',"",text,flags=re.IGNORECASE) 
text = re.sub(r'_*|\+*',"",text) # removes _ and +
text = re.sub(r'&amp;*|&amp|amp',"",text) 
text = demoji.replace(text, "") 
cleaned_words = [x for x in words if not bool(re.search('^[0-9]+$|^$', x))]
```
With `re.sub` we can substitute the text we don't want. 
The first three lines remove the "@", "_", "+" and different variations of "amp" (You can find it in the second Tweet from Elon Musk in the output above)
All these are substituted with empty strings which are being removed in the last line. The last line also cleans alone standing numbers like "734982" but leaves numbers with characters in the string like "$20k".

As an example, this is a tweet before cleaning:

> "_boii &amp people think is high now wait till it’s $20k + by the end of this week $50k+ by end of 734982 this month  y’all should follow  he's    a super underrated !bitcoiner i’ve been :following her tweets  and tips seriously  i’ve  been doing really great! #btc #ada"

After cleaning, it looks like this:
> "boii people think is high now wait till it’s $20k by the end of this week $50k by end of this month y’all should follow hes a super underrated bitcoiner i’ve been following her tweets and tips seriously i’ve been doing really great"

</br>

---

</br>

## Duplicates
The next thing is to find and delete all the duplicates:

<img src=./img/sentiment/duplicatetweets.png width=900/>
As can be seen in the picture above, the same tweet was tweeted 10 times in one minute. It is the exact same tweet and it kept on tweeting for quite a bit. Since this is obviously a bot, a way to filter out these duplicates was needed.

The first approach was as follows: Adding the collected tweets to a list, and after the list had 40 items, run a function that checks for duplicates and deletes them. There were about 40 collected items a minute, so it seemed like a good choice.

The following function converts the list to a Pandas Dataframe and checks for duplicate Tweets with their innate `duplicated()`-method. The `keep=False`-parameter deletes the found duplicates.

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

When applying this function to the whole database, it deleted 17318 duplicates from a total of 32698. More than 50% duplicate Tweets is massive! This would've deflected the calculation of the sentiment significantly. 
This lead to the decision to apply the deletion of duplicates for the entire database before calculation of the sentiment.

</br>

---

</br>

<div style="display: inline;" >
<a href=""><button onclick="" type="button"  style="border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">< Previous Chapter</button></a>
<a href=""><button type="button"  style="float:right; border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">Next Chapter ></button></a>
</div>

</br>