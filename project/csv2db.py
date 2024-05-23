import os
import sqlite3
import pandas as pd

from kaggle.api.kaggle_api_extended import KaggleApi


kaggleApi = KaggleApi()
kaggleApi.authenticate()
datasetUrl = 'aayushmishra1512/faang-complete-stock-data'

currentDirectory = os.path.dirname(__file__)
parentDirectory = os.path.dirname(currentDirectory)
datasetDirectory = os.path.join(parentDirectory, 'data')
kaggleApi.dataset_download_files(datasetUrl, path = datasetDirectory, unzip = True)

Amazon_csv_path = os.path.join(datasetDirectory, 'Amazon.csv')
Apple_csv_path = os.path.join(datasetDirectory, 'Apple.csv')
Facebook_csv_path = os.path.join(datasetDirectory, 'Facebook.csv')
Google_csv_path = os.path.join(datasetDirectory, 'Google.csv')
Netflix_csv_path = os.path.join(datasetDirectory, 'Netflix.csv')


try: 
    Amazon_df = pd.read_csv(Amazon_csv_path)
    Apple_df = pd.read_csv(Apple_csv_path)
    Facebook_df = pd.read_csv(Facebook_csv_path)
    Google_df = pd.read_csv(Google_csv_path)
    Netflix_df = pd.read_csv(Netflix_csv_path)

    os.makedirs(os.path.dirname("../data/stocks.db"), exist_ok=True)
    connection = sqlite3.connect("../data/stocks.db")

    Amazon_df.to_sql("Amazon", connection, if_exists="replace", index=False)
    Apple_df.to_sql("Apple", connection, if_exists="replace", index=False)
    Facebook_df.to_sql("Facebook", connection, if_exists="replace", index=False)
    Google_df.to_sql("Google", connection, if_exists="replace", index=False)
    Netflix_df.to_sql("Netflix", connection, if_exists="replace", index=False)


    connection.close()
    print("Done.")

except:
    print("OOps")
