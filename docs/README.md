
# Table of Contents
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

- Appendices
    - Class Diagram
    - Example of Usage (video/bilder)

</br>

---

</br>

# Abstract
#TODO Put Task, Approach and achieved goals in a few words here 

</br>

---

</br>

# Continue with the Documentation

<div style="display: inline;" >
https://github.com/moerv9/sentiment/blob/main/docs/0_Introduction.md
<a href="https://github.com/moerv9/sentiment/blob/main/docs/0_Introduction.md"><button type="button"  style="float:right; border: 2px white solid; background-color: transparent; color:white; border-radius: 8px; padding: 10px;">Next Chapter: Introduction ></button></a>
</div>

</br>
</br>

---

</br>
</br>

# Technical 

## Development Environment 


The code editor used was Visual Studio Code with their tremendous amount of extensions. 
Particular helpful extensions were the [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) Notebook, the [TabNine](https://marketplace.visualstudio.com/items?itemName=TabNine.tabnine-vscode) AI supported Autocomplete and the [LTeX](https://marketplace.visualstudio.com/items?itemName=valentjn.vscode-ltex) LanguageTool that checked grammar and spell Markdown files. This way it was possible to directly write the documentation inside VSCode.

To ensure version control for used python libraries the package and environment management system [Conda](https://docs.conda.io/en/latest/) was used.

With conda environments it is possible to work with defined python and package versions.

Setting up an environment is easy:

1. Install conda with `pip install conda`
2. Create the environment with `conda create --name myenv` 
3. See if environment was created `conda env list`
4. Activate environment with `conda activate myenv`

To create an environment from an existing `requirements.txt` file add this to the second step:

`conda create --name myenv --file requirements.txt`

Export to requirements.txt or requirements.yml with
- `conda env export > environment.yml`

- `pip freeze > requirements.txt`


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
- textblob
- demoji
- python-dateutil
- python-dotenv
- tweepy
- SQLAlchemy
- vaderSentiment
- psycopg2-binary
- subprocess.run
- streamlit_autorefresh
- boto
- schedule
- PyGithub
- postgres
- multidict
- python-binance
- python-kucoin

