# Social Signal Sentiment-Based Prediction for Cryptocurrency Trading

## Table of Contents

- Readme
    - Abstract
    - [Code-Editor](#code-editor)
    - [Folder-Structure](#folder-structure)

- [Introduction](0_Introduction.md)

- [Research](./1_Research.md)
  - [Coin Comparison](./1_Research.md#coin-comparison)
  - [Social Media Relevance](./1_Research.md#social-media-relevance)
  - [Focusing on Bitcoin](./1_Research.md#focus-on-bitcoin)

- [Concept](./2_Concept.md)

- Development
  - [Data Acquisition](./3_Data%20Acquisition.md)
  - [Backend](./4_Backend.md)
  - [Sentiment](./5_Sentiment.md)
  - [Trading](./6_Trading.md)
  - [Visualisation](./7_Visualisation.md)

- [Results](./8_Results.md)

- [Appendices](9_Appendices.md)
  - Class Diagram
  - Example of Usage (video/bilder)

</br>

---

</br>

## Abstract

## TODO Put Task, Approach and achieved goals in a few words here

</br>

---

</br>

## Continue with the Documentation

<div style="display: inline;" >
<a href="https://github.com/moerv9/sentiment/blob/main/docs/0_Introduction.md"><button type="button"  style="float:right; border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">Next Chapter: Introduction ></button></a>
</div>

</br>
</br>

---

</br>
</br>

## Development

</br>



### Code Editor

The code editor used was Visual Studio Code with their tremendous amount of extensions.
Particular helpful extensions were the [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) Notebook, the [TabNine](https://marketplace.visualstudio.com/items?itemName=TabNine.tabnine-vscode) AI supported Autocomplete and the [LTeX](https://marketplace.visualstudio.com/items?itemName=valentjn.vscode-ltex) LanguageTool that checked grammar and spell Markdown files. This way it was possible to directly write the documentation inside VSCode.

### Environment Setup

To ensure version control for used python libraries the package and environment management system [Conda](https://docs.conda.io/en/latest/) was used.

With conda environments it is possible to work with defined python and package versions.

Setting up an environment is easy:

1. Install conda with `pip install conda`
2. Create the environment with `conda create --name myenv`
3. See if environment was created `conda env list`
4. Activate environment with `conda activate myenv`

To create an environment from an existing `requirements.txt` file add this to the second step:

`conda create --name myenv --file requirements.txt`


The following packages were used:

- pandas
- matplotlib
- sentiment
- streamlit
- wordcloud
- numpy
- openpyxl
- regex==2022.3.2
- pyOpenSSL
- demoji
- python-dateutil
- python-dotenv
- tweepy
- SQLAlchemy
- vaderSentiment
- psycopg2-binary
- streamlit_autorefresh
- boto
- schedule
- postgres
- python-binance
- python-kucoin

Export to requirements.txt or requirements.yml with

- `conda env export > environment.yml`

- `pip freeze > requirements.txt`

</br>

---

</br>

### Local Development

#### **Tweepy Stream and local Export**

1. Activate the conda environment with required packages (see above)
2. Get your own API-Keys from Twitter API and Kucoin Sandbox and add them to .env-file
3. Set up a Postgres Database and add DB_URL to .env
4. Edit runner.py : 
    - Uncomment line 48 for local export
    - Either add the keywords for the coins in the last line:   </br>
Runner(['btc','ada','eth'])) </br>
    </br> or Uncomment lines 66 - 72  

5. run script via terminal: </br>
        `python3 runner.py -k "btc,eth,ada" -i 5`

#### **Streamlit**

    1. cd streamlit
    2. streamlit run 01_💬_Tweet-Sentiment.py
    3. open http://localhost:8501

</br>

---

</br>

### Folder-Structure

</br>

| **main - Folder** |                            |
|-------------------|------------------------------------------|
| config.py         | File to get the Environment-Variabes     |
| Procfile          | A Heroku file for starting the processes |
| docs              | Contains the ordered Documentation       |

</br>


| **sentiment - Folder** |   |
|------------------------|---|
| filter.py              | Functions to filter the tweets by checking for blacklisted words, duplicates and unnecessary symbols  |
| keywords.py            | Class to build a keyword list for coins  |
| listener.py            | Class to listen and filter tweets     |
| runner.py              | Main Class. Called in [Procfile](../Procfile) and starts Listener with Keywords  |
| trade.py               | Functions for Trading. Called every hour in Heroku Scheduler.    |
| Logs-Folder            | All Logs (Heroku, Tweepy, Excel, Json)

</br>

| **sentiment/database - Folder**           |                                                                           |
|-------------|---------------------------------------------------------------------------|
| database.py | SQL-Alchemy Connection with Heroku database                               |
| exporter.py | Export Local Tweets to Json/Excel                                         |
| Trade.py    | Trade Class to declare the Format and Type of each Column in the Database |
| Tweet.py    | Tweet Class to declare Format and Type of each Column in the Database     |

</br>

| **streamlit - Folder**      |   |
|-------------------------|---|
| 01_💬_Tweet-Sentiment.py | Main File to visualise all the data from tweets, sentiment and trades with Streamlit  |
| financial_data.py       | Functions to get the data from Heroku Database, get prices from Binance and for building Signals  |
| streamlit_data.py       | Functions to edit the data from the databases: Splitting the Dataframe, calculate average and convert to signals.  |
| visualise.py            | Functions to visualise the price chart and words.   |






