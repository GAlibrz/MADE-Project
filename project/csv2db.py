import os
import sqlite3
import pandas as pd
import gc
from kaggle.api.kaggle_api_extended import KaggleApi
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import grangercausalitytests
import numpy as np

stock_start_date = '1998-01-01'
stock_end_date = '2020-07-01'
stock_columns_to_keep = ['Date', 'price']
tempreture_columns_to_keep = ['Area', 'Months','Months Code' , 'Year', 'Value']

def stock_df_date_handler(df, date1, date2):

    df = df[df['Date'] > date1]
    df = df[df['Date'] < date2]
    return df

def stock_df_make_montly(df):

    df['Date'] = pd.to_datetime(df['Date'])
    df['index_Date'] = df['Date']
    df.set_index('index_Date', inplace=True)

    monthly_df = df.resample('M').agg({
    'Date' : 'last',
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
        })

    monthly_df['Date'] = monthly_df['Date'].dt.strftime('%Y-%m')
    return monthly_df

def stock_df_column_handler(df,columns):

    df['price'] = (df['Open'] + df['Close']) / 2
    df = df.filter(items = columns)
    return df

def fill_na_with_row_mean(row):
    numeric_cols = row.drop(labels=['Date'])  # Exclude the 'Date' column
    mean_value = numeric_cols.mean()
    return row.apply(lambda x: mean_value if pd.isna(x) and np.issubdtype(type(x), np.number) else x)



kaggleApi = KaggleApi()
kaggleApi.authenticate()
marketDatasetUrl = 'aayushmishra1512/faang-complete-stock-data'
tempretureDatasetUrl = 'sevgisarac/temperature-change'

currentDirectory = os.path.dirname(__file__)
parentDirectory = os.path.dirname(currentDirectory)
datasetDirectory = os.path.join(parentDirectory, 'data')
kaggleApi.dataset_download_files(marketDatasetUrl, path = datasetDirectory, unzip = True)
kaggleApi.dataset_download_files(tempretureDatasetUrl, path = datasetDirectory, unzip = True)


Amazon_csv_path = os.path.join(datasetDirectory, 'Amazon.csv')
Apple_csv_path = os.path.join(datasetDirectory, 'Apple.csv')
tempreture_csv_path = os.path.join(datasetDirectory, 'FAOSTAT_data_1-10-2022.csv')


try: 
    
    Amazon_df = pd.read_csv(Amazon_csv_path)
    Amazon_df = stock_df_make_montly(Amazon_df)
    Amazon_df = stock_df_date_handler(Amazon_df, stock_start_date, stock_end_date)
    Amazon_df = stock_df_column_handler(Amazon_df, stock_columns_to_keep)

    Apple_df = pd.read_csv(Apple_csv_path)
    Apple_df = stock_df_make_montly(Apple_df)
    Apple_df = stock_df_date_handler(Apple_df, stock_start_date, stock_end_date)
    Apple_df = stock_df_column_handler(Apple_df, stock_columns_to_keep)

    final_stock_df = Amazon_df[['Date', 'price']]
    final_stock_df = final_stock_df.rename(columns = {'price' : 'Amazon_price'})
    final_stock_df['Apple_price'] = Apple_df['price']
    final_stock_df = final_stock_df.reset_index(drop = True)
    #final_stock_df.to_csv('stocks.csv', index=False)

    tempreture_df = pd.read_csv(tempreture_csv_path)
    tempreture_df = tempreture_df.filter(items = tempreture_columns_to_keep)

    tempreture_df = tempreture_df[tempreture_df['Months Code'] < 7013]


    '''
        *****************************************************
    '''

    month_map = {
        'January': '01', 'February': '02', 'March': '03', 'April': '04',
        'May': '05', 'June': '06', 'July': '07', 'August': '08',
        'September': '09', 'October': '10', 'November': '11', 'December': '12'
    }

    # Apply month mapping
    tempreture_df['Month'] = tempreture_df['Months'].map(month_map)



    # Combine 'Year' and 'Month' to create a date column
    tempreture_df['Date'] = pd.to_datetime(tempreture_df['Year'].astype(str) + '-' + tempreture_df['Month'])

    # Filter temperature data to keep relevant columns

    # Aggregate the temperature data by date and area
    tempreture_df = tempreture_df.groupby(['Date', 'Area']).agg({'Value': 'mean'}).reset_index()
    #tempreture_df = tempreture_df.reset_index()
    tempreture_df['Date'] = pd.to_datetime(tempreture_df['Date']).dt.strftime('%Y-%m')
    tempreture_df = tempreture_df[(tempreture_df['Date'] >= '1998-02') & (tempreture_df['Date'] <= '2020-07')]



    '''
        *****************************************************
    '''

    merged_df = pd.merge(final_stock_df, tempreture_df, on='Date', how='inner')

    # Handle missing values
    merged_df.dropna(inplace=True)

    

    '''************************************************************'''

    # Pivot the data frame to have countries as columns and dates as rows
    pivot_df = tempreture_df.pivot(index='Date', columns='Area', values='Value')


    # Compute the correlation matrix
    countries_temp_correlation_matrix = pivot_df.corr()

     #Flatten the correlation matrix to a 1D array
    countries_temp_correlation_values = countries_temp_correlation_matrix.values.flatten()

    # Remove self-correlation values (1s on the diagonal)
    countries_temp_correlation_values = countries_temp_correlation_values[countries_temp_correlation_values != 1]

    # Summary statistics
    #summary_stats = pd.Series(countries_temp_correlation_values).describe()
    #summary_stats

    # Plotting the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(countries_temp_correlation_values, bins=50, color='blue', alpha=0.7)
    plt.title('Histogram of Correlation Coefficients')
    plt.xlabel('Correlation Coefficient')
    plt.ylabel('Frequency')
    plt.grid(True)
    #plt.show()



    '''***************************************'''

    tmp_stock_correlation_matrix = merged_df[['Amazon_price', 'Apple_price', 'Value']].corr()

    # Plotting the correlation
    plt.figure(figsize=(8, 6))
    plt.matshow(tmp_stock_correlation_matrix, fignum=1)
    plt.colorbar()
    plt.xticks(range(len(tmp_stock_correlation_matrix.columns)), tmp_stock_correlation_matrix.columns, rotation=45)
    plt.yticks(range(len(tmp_stock_correlation_matrix.columns)), tmp_stock_correlation_matrix.columns)
    #plt.show()

    '''*************************************************'''

    data_for_granger = merged_df[['Amazon_price', 'Apple_price', 'Value']]

    # Perform Granger causality test for Amazon price and temperature
    max_lag = 12
    granger_test_result = grangercausalitytests(data_for_granger[['Amazon_price', 'Value']], max_lag, verbose=False)


# Display the results for each lag
   # for lag, results in granger_test_result.items():
    #    print(f"Lag {lag}:")
     #   for test, result in results[0].items():
            
      #      print(f"  {test} - F-statistic: {result[0]:.4f}, p-value: {result[1]:.4f}")
    '''*************************************************************'''

    os.makedirs(os.path.dirname("../data/stocks_temp.db"), exist_ok = True)
    connection = sqlite3.connect("../data/stocks_temp.db")
    final_stock_df.to_sql('stocks', connection, if_exists = "replace", index = False)
    pivot_df.to_sql('tempreture', connection, if_exists = "replace", index = False)
    #merged_df.to_sql
    
    connection.close()
    print("Done.")

except Exception as e:

    print(f"Error: {e}")

