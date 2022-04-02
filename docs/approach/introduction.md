# Introduction 

## My Approach

### Research
My research will include the following
- [Analysis of Top 5 Cryptocurrencies](coins.ipynb)
- [Analysis of Social Media Platforms](SocialMedia.ipynb)
- [How to get the Sentiment](Sentiment.ipynb)

### Programming
![Concept as Flow Diagram](../../img/concept.png)


## Abstract


## My initial Proposal

My Thesis is supposed to cover two topics:
It will analyse specific signals in social networks and their impact on trading digital assets, specifically cryptocurrency. This research will be used in a real-world test with the development of a bot that automatically trades cryptocurrency while considering the analysis of social signals.

Thus, the title is going to be: 
Social Signal Sentiment-Based Prediction for Cryptocurrency Trading.

**Goal**

My goal for this thesis is twofold. As being said by Schoen et al. (2013) about social media: “… little is known about their overall potential, limitations and general applicability to different domains.” Chainsulting, a blockchain-company from Flensburg (see Context), is open for publishing my thesis, as it will greatly contribute to a scientific area where not much has been done before. I can only guess the reason there isn’t much about this, is, because if an automatic trading bot can increase the revenue this will not likely be published. 
This leads to another reason for my thesis. To build a reliable database and develop new strategies to get reliable buy and sell signals for successful trading with cryptocurrency. 

**Why social media?**

The amount of data social media can offer us is just to big to grasp but we can use them to our advantage. Studies have already shown that search trends have an impact on the price of stocks (Kristoufek, 2013).
In my thesis I will analyse a couple different social networks (Instagram, Twitter, Facebook, etc.) with respect to their userbase, availability of API’s and other factors to see which one is best for my use-case.

I will then build a list of keywords the trading bot is supposed to use as signals. Signals are buy, sell and neutral. Neutral meaning that if one position is already bought, the bot should hold the position and not buy a new one or there is no immediate action to be taken. A function to bet against the market (shorting) could also be implemented if the signals lead to that sentiment.

This list of keywords will be in english because it is the most used language and will lead to the most data. A tool is most likely being used for creating a database, which means I have to do some research here as well.

My keyword list needs to be validated in terms of relevance and impact. 
There is a big room for error here. For example:
How much impact does a tweet from Elon Musk (60M Followers) have in comparison to a tweet from a no-name account with only 10 followers (who could also be a bot) and how is the content of the message being interpreted?

I am focussing on one cryptocurrency and to find the right one I will analyse the Top 5 cryptocurrencies (based on marketcap.) in relation to their trading volume, user base, API Access, amount of tweets about the cashtag($btc, $eth, etc.), etc.. If it finds a real-world use-case the costs of trading need to be considered as well. 
As Garcia and Schweitzer (S.8, 2015) are saying in their research: “Trading costs can potentially erode the profitability of trading strategies, especially if they require many movements.” 

For the development of the trading bot I am going to compare different programming languages to see which one is suited best for web crawling, building a database and automated trading.

I am going to focus on one social network, one cryptocurrency and one language so I can get the best results in the time I have at hand. My guess is, that I will most likely use Twitter (because of their good documentation), Bitcoin or Ether (the two most used currencies) and Python (good for handling big data and automation). I will not go into too much detail of mathematic formulas or trading techniques. The result could either be a list about what trades the bot could’ve made and their outcome or a real-world-simulation. It would also be great if the bot can learn and adapt it’s trading (Machine Learning).

**Action Plan**
The following numbered list could be a possible action plan and structure for my thesis:
1. Research
	1. Social Network
Building a list of criterias to compare networks
Build a keyword list to use as signals
Validation of keywords and signals
	2. Cryptocurrency
       	- Analysis the Top 5 currencies 
	3.  Programming Language
       	- Analysis of different languages and frameworks
       4. Summarising all the results to a guideline (optional) 
2. Programming
	- Implementing the server-architecture from Chainsulting
	- Developing the bot
3. Writing 
	- Technical Documentation
	- Documentation of my Actions
	- Thesis

As can be seen, my time will be spent on three things: Research, Programming and Writing.
I will spend 50% of the time researching, probably 40% on programming and the last 10% are for writing. Creating the database will connect the two phases of research and programming. The programming part will be split into using the database, building the bot, testing and validating the results. During the whole process I will document everything so it will be easier at the end to write everything together.


**Context**

My thesis will find context in the R&D Department of Chainsulting, a blockchain-company based in Flensburg. Like them, I will use Github Projects for project management. 
Contact person will be Yannik Heinze, CEO of Chainsulting. (y.heinze@chainsulting.de)

“Chainsulting is a consulting and development company, on the subject of Distributed Ledger Technology (DLT) & Digital Assets. We show ways, opportunities, risks and offer comprehensive solutions. “ (https://chainsulting.de/about-us/)

Chainsulting is keen on finding out if the idea behind social signals is working and interested in increasing their revenue and improving their trading methods. 
As mentioned above there are a couple of studies who already analyse the impact of social media on the stock market. 
My thesis can lay a foundation for further studies so everyone can have a guideline for their individual use-case.
And if I get useful results Chainsulting may use my bot in their trading desk. Code and Research will be a 100% public.


#### Literature

Garcia, D., & Schweitzer, F. (2015). Social signals and algorithmic trading of Bitcoin. Royal Society Open Science, 2(9), 150288. https://doi.org/10.1098/rsos.150288

Kristoufek, L. (2013). BitCoin meets Google Trends and Wikipedia: Quantifying the relationship between phenomena of the Internet era. Scientific Reports, 3(1). https://doi.org/10.1038/srep03415

Schoen, H., Gayo-Avello, D., Takis Metaxas, P., Mustafaraj, E., Strohmaier, M., & Gloor, P. (2013). The power of prediction with social media. Internet Research, 23(5), 528–543. https://doi.org/10.1108/intr-06-2013-0115


