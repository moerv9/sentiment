# Table of Contents
<!-- - Abstract (Task, Approach and achieved goals in a few words) -->
- Introduction

- [Research](Research.md)
    - [Coin Comparison](./Research.md#coin-comparison)
    - [Social Media Relevance](./Research.md#social-media-relevance)
    - [Focusing on Bitcoin](./Research.md#focus-on-bitcoin)
- Concept
- Development
        - [Data Acquisition](Data%20Acquisition.md)
        - [Backend with Heroku](./Backend%20with%20Heroku.md)
        - [Sentiment](Sentiment.md)
        - Trading with Kucoin API
        - Visualise Data
    - Challenges
    - Insights
- Results
    - (Placement in the scientific/financial context)
    - Conclusion

    - Outlook
- Technical Overview
    - Installation 
    - Tools / Libraries
        - (Reason for choosing those tools?(Robert?))
    - Code Examples
- Appendices
    - Class Diagram
    - Example of Usage (video/bilder)


# Abstract
#TODO Put Task, Approach and achieved goals in a few words here 
# Abbreviations

# Get Started

## Development Environment 
</br>

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
