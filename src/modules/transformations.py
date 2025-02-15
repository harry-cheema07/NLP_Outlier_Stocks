def changePerStock(stockData,AllStockData):
    for Index,row in stockData.iterrows():
        try:
            previous_close = AllStockData['Close',row.Ticker].iloc[-2] 
            current_close = AllStockData['Close',row.Ticker].iloc[-1]
            percentage_change = ((current_close - previous_close) / previous_close) * 100
            
            previousDayVolume=AllStockData['Volume',row.Ticker].iloc[-1]

            stockData.at[Index, 'Change'] = percentage_change
            stockData.at[Index, 'Volume'] = previousDayVolume
            stockData =  stockData.dropna()
        except:
            print('error')

        
        return stockData
    
def changePerSegment(stockData):
    segment_growth=stockData.groupby('Sector')['Change'].mean().reset_index().sort_values(by='Change', ascending=False)
    return segment_growth


def upperLowerBound(stockData):
    quantiles = stockData.groupby(['Sector'])['Change'].quantile([0.25,0.75]).unstack()

    quantiles.columns = ['0.25', '0.75']

    quantiles['IQR'] = quantiles['0.75'] - quantiles['0.25']


    quantiles['lower_bound'] = quantiles['0.25'] - 1.5 * quantiles['IQR']
    quantiles['upper_bound'] = quantiles['0.75'] + 1.5 * quantiles['IQR']

    return quantiles

def outliers(stockData):
    stockData['Outliers'] = (stockData['Change'] < stockData['lower_bound']) | (stockData['Change'] > stockData['upper_bound'])
    outliers=stockData.query('Outliers == True')
    return outliers