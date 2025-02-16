import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../data")
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"./modules")

import plotly.express as px
import pandas as pd
import GetData as gd
import transformations as tf



sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]


stockData = sp500[['Symbol','GICS Sector']].rename(columns={'Symbol':'Ticker','GICS Sector':'Sector'})


AllStockData = gd.getAllStocksHistoricalData(stockData['Ticker'])

for Index,row in stockData.iterrows():
    try:
        previous_close = AllStockData['Close',row.Ticker].iloc[-2] 
        current_close = AllStockData['Close',row.Ticker].iloc[-1]
        percentage_change = ((current_close - previous_close) / previous_close) * 100
        
        previousDayVolume=AllStockData['Volume',row.Ticker].iloc[-1]
    except:
        print('error')

    stockData.at[Index, 'Change'] = percentage_change
    stockData.at[Index, 'Volume'] = previousDayVolume

stockData =  stockData.dropna()



#Segment Growth Calculation
segment_growth = stockData.groupby('Sector')['Change'].mean().reset_index().sort_values(by='Change', ascending=False)




#Calculating Quantiles, upper and lowe bound

quantiles = stockData.groupby(['Sector'])['Change'].quantile([0.25,0.75]).unstack()

quantiles.columns = ['0.25', '0.75']

quantiles['IQR'] = quantiles['0.75'] - quantiles['0.25']


quantiles['lower_bound'] = quantiles['0.25'] - 1.5 * quantiles['IQR']
quantiles['upper_bound'] = quantiles['0.75'] + 1.5 * quantiles['IQR']


# Joining with the main data set

stockData = stockData.join(quantiles,on=['Sector'])

# Calculating Outliers

stockData['Outliers'] = (stockData['Change'] < stockData['lower_bound']) | (stockData['Change'] > stockData['upper_bound'])

outliers = stockData.query('Outliers == True')

print(outliers)

#Plotting Outliers

fig = px.scatter(outliers, x='Volume', y='Change', text='Ticker',color='Sector', title='Outliers')
fig.update_traces(marker=dict(size=12), selector=dict(mode='markers+text'))
fig.show()



#Collecting News related to Outliers
news = gd.getOutlierNews(outliers['Ticker'])
rows=[]
#initiating Dataframe to store news links
news_df = pd.DataFrame(columns=['Stock','News'])

for key, value in news.items(): 
    for my_dict in value:
        for k,value in my_dict.items():
            if isinstance(value, dict):
                rows.append({'Stock':key,'News':value['canonicalUrl']['url']})

news_df = pd.concat([news_df, pd.DataFrame(rows)], ignore_index=True)         
print(news_df)