
# Introduction 

## Social Signal Sentiment-Based Prediction for Cryptocurrency Trading.

This project is supposed to cover two topics:
It will analyse specific signals in social networks and their impact on trading digital assets, specifically cryptocurrency. This research will be used in a real-world test with the development of a bot that automatically trades cryptocurrency while considering the analysis of social signals.

</br>

## Motivation

As being said by Schoen et al. [[1](9_Appendices.md#literature--bibliography)] about social media: 
> “… little is known about their overall potential, limitations and general applicability to different domains.”

Chainsulting, a [blockchain](9_Appendices.md#b)-company from Flensburg is keen on finding out if the idea behind social signals is working and interested in trying out new trading methods. Also, they are open for publishing this project, as it will greatly contribute to a scientific area where not much has been done before. It is obvious, that if an automatic trading bot can increase the revenue this will not likely be published. 
[Natural Language Processing (NLP)](9_Appendices.md#n) is a big part in today's world of big data and their impact is yet to be studied. 

</br>

## Context
This project will find context in the [R&D](9_Appendices.md#abbreviations) Department of Chainsulting, a blockchain-company based in Flensburg.
Contact person will be Yannik Heinze, CEO of Chainsulting ([Email](y.heinze@chainsulting.de)).

> “Chainsulting is a consulting and development company, on the subject of Distributed Ledger Technology (DLT) & Digital Assets. We show ways, opportunities, risks and offer comprehensive solutions. “ [[2](9_Appendices.md#literature--bibliography)]

More about Chainsulting on their [Website](https://chainsulting.de) or [GitHub Profile](https://github.com/chainsulting).


</br>

## Approach

### First Phase: Research

The amount of data social media can offer is just too big to grasp, but it can be used to an advantage in trading. A study from 2013 has already shown that search trends have an impact on the price of Bitcoin:
> "Speculation and trend chasing evidently dominate the BitCoin price dynamics." [[3](9_Appendices.md#literature--bibliography)]

There exists a lot of different social networks (Instagram, Twitter, Facebook, etc.) and after comparing them with respect to their user base, availability of [API’s](9_Appendices.md#a) and other factors, it will be clear which one is best for this project.

To find the right cryptocurrency for this project, the top five Coins based on market capitalisation ([MCap](9_Appendices.md#m)) are compared in relation to their trading volume, user base, API Access, amount of tweets about the [cashtag]((9_Appendices.md#c))($btc, $eth, etc.).

If it finds a real-world use-case the costs of trading need to be considered as well. 
As Garcia and Schweitzer [[4](9_Appendices.md#literature--bibliography)] are saying in their research: “Trading costs can potentially erode the profitability of trading strategies, especially if they require many movements.” 

The last part of research is to find a suitable programming language.

### Second Phase: Development

The development phase starts with the acquisition of data followed by the calculation of [sentiment](9_Appendices.md#s) about the chosen cryptocurrency.
For the backend, a service is needed where the script for data acquisition can run in the background and store all the data in a database.
At last, a strategy for trading is built and executed.

### Third Phase: Testing, Documentation and Evaluation
While testing the strategy, the documentation is written. The last step will be evaluating the results.

</br>

---

</br>

<div style="display: inline;" >
<a href="https://github.com/moerv9/sentiment/blob/main/docs/README.md"><button onclick="" type="button"  style="border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">< Previous Chapter: README</button></a>
<a href="https://github.com/moerv9/sentiment/blob/main/docs/1_Research.md"><button type="button"  style="float:right; border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">Next Chapter: Research ></button></a>
</div>

</br>

