import time
import yfinance as yf
import requests_cache
import pandas as pd
import requests
from bs4 import BeautifulSoup


session = requests_cache.CachedSession('yfinance.cache')
session.headers['User-agent'] = 'my-program/1.0'


def getData(ticker):
    tickInfo = yf.Ticker(ticker,session=session)
    hist = tickInfo.history(period="1mo")
    print(hist)
    return hist

def getClosePrice(ticker,start_date,end_date):
    getInfo = yf.download(ticker,start_date,end_date,session=session)
    return getInfo["Close"]

def getSMA(ticker,movingAverage:int,start_date,end_date):
    getInfo = yf.download(ticker,start_date,end_date,session=session)
    getInfo["SMA"] = getInfo["Close"].rolling(window=movingAverage).mean()
    return getInfo["SMA"]

def getVolume(ticker,start_date,end_date):
    getInfo = yf.download(ticker,start_date,end_date,session=session)
    return getInfo["Volume"]

def getRSI(ticker,start_date,end_date,window):
    getInfo = yf.download(ticker,start_date,end_date,session=session)
    delta = getInfo['Close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()

    gains[gains < 0] = 0
    loss[loss > 0] = 0
    #In following variables we are calculating average gain and average loss
    gain_ewm = gains.ewm(com=window - 1, adjust=False).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=False).mean())

    RS = gain_ewm / loss_ewm
    getInfo["RSI"] = 100 - 100 / (1 + RS)

    return getInfo["RSI"]

def getBalanceSheet(ticker):
    tickInfo = yf.Ticker(ticker,session=session)
    financial_data = tickInfo.balance_sheet
    return financial_data

def getFinancial(ticker):
    tickInfo = yf.Ticker(ticker,session=session)
    financial_data = tickInfo.financials
    return financial_data

def IncomeDebtData(ticker):
    netIncomeData = getFinancial(ticker).loc['Net Income']
    netIncomeData = netIncomeData.reset_index()
    netIncomeData.columns = ['date','NetIncome']
    print(netIncomeData)
    latestDateNetIncome = netIncomeData.index.max()
    netIncome =  netIncomeData.loc[latestDateNetIncome,'NetIncome']
    
    print(getBalanceSheet(ticker))
    netDebtData = getBalanceSheet(ticker).loc['Net Debt']
    netDebtData = netDebtData.reset_index()
    netDebtData.columns = ['date','NetDebt']
    latestDateNetDebt = netDebtData.index.max()
    netDebt =  netDebtData.loc[latestDateNetDebt,'NetDebt']

    data = [(latestDateNetIncome,netIncome,latestDateNetDebt,netDebt)]

    return pd.DataFrame(data,columns=['Net_Income_Date','Net_Income','Net_Debt_Date','Net_Debt'])


def getPercentageChange(ticker):
    time.sleep(0.2)
    stock = yf.Ticker(ticker)
    history = stock.history(period='5d')
    if history.empty == False:
        previous_close = history['Close'].iloc[-2] 
        current_close = history['Close'].iloc[-1] 
        percentage_change = ((current_close - previous_close) / previous_close) * 100
        return percentage_change
    

def getPreviousVolume(ticker):
    time.sleep(0.2)
    stock = yf.Ticker(ticker)
    history = stock.history(period='5d')
    previousDayVolume=history['Volume'].iloc[-1]  
    return previousDayVolume


def getAllStocksHistoricalData(tickers):
    all_stocks = yf.Tickers(" ".join(tickers))
    data = all_stocks.history(period="5d")
    return data

def getOutlierNews(tickers):
    all_stocks = yf.Tickers(" ".join(tickers))
    return all_stocks.news()

def getNewsDetails(url):
    response=requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    headline = soup.findAll('div', class_='cover-title')
    article_content = soup.findAll('p', class_='yf-1pe5jgt')
    #combining headline and article content together
    fulldataset=headline + article_content
    return fulldataset

