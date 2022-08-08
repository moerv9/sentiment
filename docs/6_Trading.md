# Trading

## Choosing an API
There are a lot of exchanges for trading cryptocurrencies. They all have pros and coins leading to a comparison of APIs with respect to this project's use case. It is important that the API has a good and easy documentation and an extensive python library/wrapper.

The following table shows the full comparison of five cryptocurrency API's, which was made using this [Article](https://www.abstractapi.com/guides/best-crypto-currency-apis):


| **Platform**                                  | [Binance](https://www.binance.com/en/binance-api)                                                                                                                                                       | [CoinBase](https://www.coinbase.com/cloud)                                            | [Kucoin](https://www.kucoin.com/api)                                                                           | [Coinmarketcap](https://coinmarketcap.com/api/)                                                                               | [Kraken](https://docs.kraken.com/rest/)                                                                                                                                                                                      |
|-----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Pros**                                      | Directly sell and buy with the API,</br>Connector to diff. Languages (python, Ruby),</br>Commission when using BNB coin, </br> 1200 free Requests per Minute, </br> Binance has one of the biggest markets | API can be used as an Exchange or Wallet,</br>Real-Time Notifications for Account Events | Many currencies(>200),</br>Telegram Group for Support,</br>1800 Free Requests per MinuteCrypto Lending available  | Good integration in many languages(python,node.js,php),</br>11 endpoints in real time for free                                   | Good python integration and code examples directly in documentation                                                                                                                                                             |
| **Cons**                                      | There have been outages in the past. </br>When exceeding the transaction limits, the IP will be temporarily banned                                                                                         | Only etc, eth, btc cash, litecoin, </br>Only 180 Requests per Minute                     | Performance issues (payments & trades hold back)                                                                  | No historical Data,</br>Pay 29$/month for 1month historical data</br>60 Requests per Minute</br>Not all REST API Calls available | ID Verification needed,</br>No test environment,</br>Trading Volume and Trade Calls depending on account level (starter, intermediate, pro): When 15 requests are reached, a decay of -0.33/sec is applied and you need to wait |
| **Historical Data**                           | Yes                                                                                                                                                                                                        | Yes                                                                                      | Yes                                                                                                               | No                                                                                                                               | Yes                                                                                                                                                                                                                             |
| **Pricing**                                   | 0.1%, but when using BNB can be lowered to 0.075%                                                                                                                                                          | 1%                                                                                       | 3-5%, when buying with FIAT</br>0.08% when buying wiht Kucoin Token                                               | not found any data                                                                                                               | 0.9% fee for any stablecoins</br>1.5% fee for any other crypto or FX pair                                                                                                                                                       |
| **Rating of Documentation**                   | Very good                                                                                                                                                                                                  | Good                                                                                     | Very good                                                                                                         | Okay                                                                                                                             | Very good                                                                                                                                                                                                                       |
| **Availability of Python Libraries/Wrappers** | Very good and updated.</br>https://github.com/sammchardy/python-binancehttps://github.com/binance/binance-connector-python                                                                                 | Last updated 8 years ago.</br>https://github.com/resy/coinbase_python33                  | Very good and updated.</br>https://github.com/sammchardy/python-kucoinhttps://github.com/Kucoin/kucoin-python-sdk | Not really detailed.</br>https://github.com/rsz44/python-coinmarketcap                                                           | Not updated recently. </br>https://github.com/veox/python3-krakenex                                                                                                                                                             |

</br>

When it came to the decision which API to use, it was quite easy to filter out the ones that weren't suitable. 
CoinBase was the first to drop because it has only five coins and no currently active python library available. 

Coinmarketcap was also not very intriguing because it has limited Endpoints and no historical Data. Paying 29$ a month for 1 month of historical data did'nt seem worth it when others offer it for free. Their python wrapper was also not very detailed.

Kucoin offers many currencies and the most free requests per minute, but reported some performance issues. These performance issues would not be a problem, since they mostly mean a delay of seconds of transaction speed, but in this case money was withheld. This was a little worrying. Their fees are also quite high.

It came down to Kraken vs Binance.
I personally use Kraken, so the ID Verification wouldn't even be a problem, but they do not offer a test/sandbox environment. Their way of working with request limits is also very different to the others and seemed to be a limiting factor.
But the biggest problem with Kraken was that there is no recently updated python wrapper available. 

Binance has one of the biggest markets with the highest liquidity and small fees.
They have a very good documentation and an updated python wrapper with lots of tutorials.
The only thing to keep in mind is the potential ban of my IP when the request limit is reached.

---
</br>

## Binance API
After registration you need to go through a verification process. Typically, this is a call with a person that verifies your identity. Binance just requires photos of your ID Card and your face. This is done quickly. To use the API there is balance needed in your account, so I decided to just send some Bitcoin from one of my wallets to the Binance Wallet. 

After that the API-Keys could be generated. These Keys are needed to connect and verify the Client with the API.

The [*python-binance*](https://python-binance.readthedocs.io/en/latest/index.html) wrapper helps with the Binance API, so there is no need to manually connect with the API via HTTP-Requests.

Acquiring data with the Binance API is fairly easy now. Getting the account balance, the latest price for BTCUSDT and making a test-order are all done in one line of code:

```
from binance import Client
client = Client(API-KEY, API-SECRET,testnet=True)

balance = client.get_asset_balance(asset='BTC')["free"]
btc_price = client.get_symbol_ticker(symbol="BTCUSDT")["price"]
print(f"Account Balance: {balance} BTC")
print(f"Latest BTC Price: {btc_price} USDT")

order = client.create_test_order(
    symbol='BTCUSDT',
    side=Client.SIDE_BUY,
    type=Client.ORDER_TYPE_MARKET,
    quantity=100)
```

---

</br>

## Strategy

Building the strategy for when a trade (buy or sell) should be executed, was a real challenge. There are hundreds of different strategies on different technical indicators, but now the buy or sell signal should be based on the sentiment of tweets on Twitter.

At first, the Idea was to calculate the average of sentiment for a particular time period and if this average reaches a certain threshold, a trade should be executed.

In the left table in the image below you see the Timestamp, Sentiment Score and the corresponding meaning for each tweet.

![60 min Sentiment Average and Amount of Tweets](./img/trading/60min-avg-count.png)

These Tweets get grouped and counted for intervals of 60 min (for example). Then the average sentiment is calculated. As can be seen in the right table. It can be noticed that some timestamps are missing and that is because during that times weren't any tweets (or there were not collected for some reason. Even after debugging, there wasn't any reason found for it).

The sentiment score for single tweets are all very different, but the average will naturally move towards neutral sentiment (0.0).
This shift would have been even more if all the neutral tweets had not been removed beforehand.

It would have been easy to just define the buy signal when the average sentiment is positive and a sell signal when the average sentiment is negative. 
But this would mean a lot of buy signals for the above example and since the database is not quite big enough to see if this average is only positive at the moment or if the calculation just tends to be a little above neutral. The bigger the time intervals, the more tweets and the bigger the shift towards neutral. 
This is why the threshold is set to 0.2, with values above signaling a buy order.

--- 
</br> 

## Define and backtest Strategy #1
![Strategy #1](./img/trading/strategy%20%231.png)

The image above shows the sentiment and bitcoin price from August 5th till August 6th. If the sentiment is above 0.2 and therefore positive or very positive it is marked as a buy signal in the chart (green triangle).





Änderung über Zeit überschreitet best. Wert

general sentiment of a coin and if the current trend matches that sentiment 
(if the general sentiment of a coin is positive, then Whitebird expects the coin price should have gone up).

If the current trend doesn't match the coin sentiment, then Whitebird accordingly opens a long/short position (for eg: if the general sentiment of a coin is negative but there is an upward trend in the coin's price, then Whitebird opens a short position).

Whitebird closes a position if a certain threshold has been met or if the coin sentiment changes over time. (sentiment goes from positive to negative)

Ratio von pos/negativen tweets überschreitet eine linie

weighted average berechnen anstatt nur den average -> aber wie?

tweet enthält keywords, die zu kauf und verkauf signalen führen


average sentiment für den tag berechnen und wenn 

Simple moving average (sma) is the mean of the data points. For example, if you look at the prices for the last 20 days, the prices of each day will be added together and then divided by 20. 
Each datapoint is weighted equally.

The Exponential moving average (ema) on the other hand gives more value to recent data points. 

## keywords:

For Buy: 
- Buy
- Uptrend
- Bullish
- pump
