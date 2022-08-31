# Social Signal Sentiment-Based Prediction for Cryptocurrency Trading

## Abstract

This project is keen on exploring the connection between the sentiment on a social-media platform about a cryptocurrency and the correlating price.

The approach has been to sample the sentiment from previously collected real-time tweets from Twitter. Afterwards, signals have been derived from these sentiment scores and a trading strategy was built. The system was designed to work in the background, store data in a Postgres database and trade on its own. It does this with the help of Heroku and a Scheduler, that checks every hour, if a trade should be made or not.

Insights of this project, like tweets, sentiment and trade metrics have been visualised with streamlit.

</br>

---

</br>

## Live-Demo
The whole system is explained in the following video:


[![explaining the whole system ](https://img.youtube.com/vi/f8ggft3yqsk/hqdefault.jpg)](https://youtu.be/f8ggft3yqsk)

</br>


Further explanation about the visualisation (snapshot from 24th August, 2022):



[![visualisation Video ](https://img.youtube.com/vi/bHvFifWAr1A/hqdefault.jpg)](https://youtu.be/bHvFifWAr1A)

</br>

(The videos are also found inside the [GitHub Repo](./videos/).)

</br>

---

</br>

## Documentation
</br>

### Table of Contents

- [Abstract](#abstract)

- [Introduction](0_Introduction.md)

- [Research](./1_Research.md)
  - [Coin Comparison](./1_Research.md#coin-comparison)
  - [Social Media Relevance](./1_Research.md#social-media-relevance)
  - [Focusing on Bitcoin](./1_Research.md#focus-on-bitcoin)


- [Concept](./2_Concept.md)
    - [Development Environment](./2_Concept.md#development-environment) 


- [Data Acquisition](./3_Data%20Acquisition.md)

- [Backend](./4_Backend.md)
- [Sentiment](./5_Sentiment.md)
- [Trading](./6_Trading.md)
- [Visualisation](./7_Visualisation.md)


- [Conclusion](./8_Conclusion.md)

- [Appendices](9_Appendices.md)


</br>

 

<div style="display: inline;" >
<a href="https://github.com/moerv9/sentiment/blob/main/docs/0_Introduction.md"><button type="button"  style=" border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;     margin:0 auto;
    display:block;">First Chapter: Introduction ></button></a>
</div>

</br>
</br>

(A PDF file containing all chapters is [here](./pdf/CryptoSentimentAnalysisByMarvinOttersberg.pdf). Unfortunately, the conversion from Markdown to PDF resulted in some faulty format. Better read here.)



