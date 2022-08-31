# Visualisation with Streamlit


When scripts are running in the background and acting on their own, a lot of work will never be seen.
Since all the tweet and trade data are stored in a database and the sentiment analysis and price charts can be visualised in plots and diagrams.

[Streamlit](https://streamlit.io) is an open-source Framework for building simple and interactive Machine-Learning and Data Science Web-Apps. It was perfect for this project, because it contained all the features for charts and DataFrames and was easy to implement and therefore allowed rapid prototyping. 

Actually, Streamlit and [Jupyter Notebooks](9_Appendices.md#j) were used to test the code before it entered Heroku, because each execution on Heroku consumed dynos and obviously increased the row count in the database. The jupyter notebooks can be found in this [folder](./jupyter_notebooks/), but are not used in this documentation and therefore a bit messy.

In this project, [pandas](https://pandas.pydata.org) was used for data analysis and [Matplotlib](https://matplotlib.org) to visualise the data. They both work seamlessly with streamlit.

In the following section are explanations with screenshots (from the 24th August 2022) for the single parts that have been visualised on a Website [[FR 60](2_Concept.md#should-have)].


A video was made to explain the whole visualisation in total (It is also in the [visualisation](./img/visualisation/) folder).

[![Watch the Video](https://img.youtube.com/vi/bHvFifWAr1A/hqdefault.jpg)](https://youtu.be/bHvFifWAr1A)

##### *Figure 24: Visualisation of tweet, sentiment and trading metrics*
</br>

</br>

---

</br>


## Final Visualisation

The site starts by explaining what a sentiment is and shows the `last collected sentiment` and the `correspending signal`. The site is structured in a way the whole project was planned. First came the collection of tweets, followed by the sentiment analysis and lastly the trading part.

![explanation](./img/visualisation/explanation.png)
##### *Figure 25: Explanation and most important Metrics*
</br>
</br>

### Last collected Tweets

With a slider, the rows of single tweets to retrieve from the database can be adapted (figure 26). It is basically the same table as in the [Data-Acquisition](3_Data%20Acquisition.md#tweet-metrics)-Section, but now in real-time. It was very good to work with streamlit during the whole development phase to have a look at the current status of the Heroku database without needing to go through the whole Heroku dashboard (which takes quite a few steps to look at the Dataclip of the database).

![last collected tweets](./img/visualisation/last_coll_tweets.png)
##### *Figure 26: Last collected tweets with some metrics*
</br>

</br>

### Sentiment Metrics

Figure 27 shows some metrics about sentiment. At the date of collection (24-08-2022), a total of 40k Tweets were collected in the past four days and 8273 in the past 24h. The average follower count was 13.314, which is okay, considered only accounts under 500 followers are filtered. It means there are quite a lot of accounts with a high follower account, speaking for a high quality of tweets.

![sent metrics](./img/visualisation/sent_metrics.png)
##### *Figure 27: Sentiment Metrics*
</br>
</br>

> More than a quarter of all tweets are duplicates! Presumably posted by bots.

</br>

In the [Data-Acquisition](3_Data%20Acquisition.md#duplicates)-Section it was already seen, that more than half of all tweets were duplicates. But because this was only a snapshot from one single moment, a further analysis over a longer period of time had to be made. 

The Results from looking for duplicates at two time periods from the whole database were as follows:

```
Time period 1: 1st August - 12th August
30731 duplicates in 100000 tweets from 20113 users.

time period: 20th August - 27th August
26604 duplicates in 100000 tweets from 17690 users.
```
</br>

More than a quarter of tweets were duplicates and unique users were 20 % or less. 
In other words: 

> Nearly a third of all tweets were coming from the same 80% of accounts.

</br>

These two values are not as high as 42 % (Figure 27), but show that there are many bots tweeting and trying to influence the opinion about Bitcoin. It has been the most eye-opening fact from this project.

It is particularly interesting because Elon Musk's attempt from April 2022 to buy Twitter is on hold because Twitter will not publish evidence about how they calculate the amount of bots on Twitter:

</br>

> "Twitter has repeatedly said that spam bots represent less than 5% of its total user base. Musk, meanwhile, has complained that the number is much higher, and has threatened to walk away from his agreement to buy the company for $44 billion until he gets confirmation about Twitter’s bot percentage." [11]

</br>

If this project could easily find an indicator for the amount of bots, it makes you wonder why Twitter can't or better **won't** say, how many bots are on their platform. 

</br>

The cake diagram on the left shows the sentiment for the last timeframe. It corresponds to the first line from the table on the right. Neutral tweets have been removed as being explained in [Sentiment](5_Sentiment.md#more-filters).
The table shows the last five time periods with the calculated sentiment average and total tweets. This was the base for the trading-part.

</br>

### Word Analysis

The wordcloud on the left visualises the usage and frequency of words in all the tweets from the last time period. 

In the middle, the usage of words which signal a buy- or sell-signal is shown. 
It stems from the following subdivision of words:

| BUY-Signal       | SELL-Signal          |
|------------------|----------------------|
| - buy & bought   | - sell               |
| - bullish & bull | - down               |
| - high           | - bearish            |
| - pump           | - sold               |
| - growth         | - never              |
| - up & uptrend   | - bad                |
| - revolution     | - low                |
| - hold           | - dump               |
| - love           | - decline            |
| - trust          | - downfall & downtrend |
| - success        | - decay              |
| - hodl           | - recession          |
| - like           | - short              |
| - profit         | - hate               |
| - gain           | - #short             |
| - #pump          | - #dump              |
| - long           | - loss & lost & lose |

</br>


This word analysis was primarily done to eventually build a strategy based on the usage of these words and compare it to the overall sentiment-strategy. Out of time shortage, this couldn't be implemented during this project, but lead to some interesting insights.

The overall sentiment of all tweets was negative, but most of the above used words signaled a buy-trade (Figure 28).

![word analysis](./img/visualisation/word_analysis.png)
##### *Figure 28: Word Metrics*
</br>
</br>

### Trading

For the trading part the first thing to have a look at are the most important metrics.
The trading was started on the 16th August 2022 and after 8 days, a total of 90 trades were executed. The current holdings stood at 1785 $ USDT and the Bitcoin Balance was 0.0117 ₿ Bitcoin. 

As being said in [Challenges](6_Trading.md#different-sandbox-prices) in the Trading-Section, the sandbox price is different from the real price of Bitcoin. It was attempted to find a factor, but the sandbox price has unusual and incomprehensible price movements. This meant, the results could not be evaluated that easily. At the time of writing (24th August, 9:46) the holdings in Bitcoin equalled 250$, which would lead to a total loss of 2965 $. 


![account metrics](./img/visualisation/acc_metrics.png)
##### *Figure 29: Kucoin Account Metrics*
</br>

Figure 30 shows the last trades, visualised with the corresponding real-time Bitcoin price. Working with Matplotlib to visualise the data has been an essential part for understanding the collected data and make predictions. 

A valuable statement can be made with this chart:

> The sentiment about Bitcoin on Twitter is as volatile as the Bitcoin price.

</br>

![last trades chart](./img/visualisation/last_trades_chart.png)
##### *Figure 30: Chart of last trades*
</br>

Buying at the lowest price and selling at the highest is the ultimate goal of trading. Since this is achieved very rarely and near impossible to persevere, fast trading looks for indicators to buy or sell quickly. Long-Term Investors on the other hand normally ride out short-time losses. 

The strategy here was very simple and did not really take into account if a position of BTC is already held or if a sell-trade is being executed at a very bad price. The last part of the chart is a great example for this. The Buy-Trade happened on the 23rd August at 20:00 at the lowest price and then went only up afterwards, but the sentiment was always negative, so every hour a portion was sold. The system could wait for the first price drop after an uptrend and then sell. Same for the other way around. This would hold positions longer and lead to a better cost-average-effect.

This could be one way to improve the strategy. As can be seen below, a lot of trades are made during the day, because the system is scheduled to act every hour. If there wasn't that much price movement in Bitcoin, the trading times would be spread wider apart. For example, every 6 or even 12 hours. But this would mean that the calculated average moves more to *neutral*, which would decrease the significance of the score.

Figure 31 shows the list of all trades with some more metrics.
The first column shows if the trade was a buy or a sell. 
"TradeAt", "Avg" and "AvgFrom" are self-explanatory.
The balances are taken **after** the trade. 
The fee is very important if it comes to a more detailed calculation of Profit-And-Loss, as being stated in the Introduction.

At this point and after nearly `90` trades, the total fees are about 10$, which is negligible.

</br>

![last trades table](./img/visualisation/last_trades_table.png)
##### *Figure 31: Table of last trades*
</br>

Summing up, there is a lot of improvement for different strategies to trade cryptocurrency based on the sentiment, but the foundation of all the technological necessities has been set.
Visualising these metrics has been very insightful and helped a lot when figuring out the next steps and see what happens in the background. This way of development was similar to test-driven-development, because it allowed for easy debugging and testing locally before deploying to the real-time release.

</br>

---

</br>

<div style="display: inline;" >
<a href="https://github.com/moerv9/sentiment/blob/main/docs/6_Trading.md"><button onclick="" type="button"  style="border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">< Previous Chapter: Trading</button></a>
<a href="https://github.com/moerv9/sentiment/blob/main/docs/8_Conclusion.md"><button type="button"  style="float:right; border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">Next Chapter: Conclusion ></button></a>
</div>

</br>