import bt
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from datetime import date, timedelta
matplotlib.use('MacOSX') #Use 'TkAgg' if not MacOSX

pos = {} #Set Up Core Positions for Each Rebalance Date
pos[pd.to_datetime('2021-11-09')] = dict.fromkeys(['TLT','EMB','IWM','DIA','SPY','QQQ','EEM','VGK','REM','VNQ','BITO','LQD','HYG','IGSB','AAPL','AMZN','FB','GOOGL','MSFT','NVDA','GDX','CPER','GSG'], -1.0) | dict.fromkeys(['IEI','SHY','SHV','BIL','GLD','UUP','FXF','FXY','VXX'], 1.0)
pos[pd.to_datetime('2022-02-24')] = dict.fromkeys(['TLT','EMB','IWM','DIA','SPY','QQQ','EEM','VGK','REM','VNQ','BITO','LQD','HYG','IGSB','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'], -1.0) | dict.fromkeys(['IEI','SHY','SHV','BIL','UUP','FXF','FXY','VXX','GLD'], 1.0)
pos[pd.to_datetime('2022-03-31')] = dict.fromkeys(['TLT','EMB','IWM','DIA','SPY','QQQ','EFA','EEM','VGK','REM','VNQ','SMH','JNK','IJH','BITO','LQD','HYG','IGSB','XLF','EUFN','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'], -0.75) | dict.fromkeys(['BIL','SHV','SHY','IEI','STIP','UUP','FXF','FXY','GLD','SLV'], 0.75)
pos[pd.to_datetime('2022-05-20')] = dict.fromkeys(['TLT','EMB','IWM','DIA','SPY','QQQ','EFA','EEM','VGK','REM','VNQ','SMH','JNK','IJH','BITO','LQD','HYG','IGSB','XLF','EUFN','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'], -0.50) | dict.fromkeys(['BIL','SHV','SHY','IEI','STIP','UUP','FXF','FXY','GLD','SLV'], 0.50)
for k in pos: pos[k].update((x, y*1/len(pos[k])) for x, y in pos[k].items()) #Equal Weight Core Positions                                   
pos[pd.to_datetime('2022-05-20')] = pos[pd.to_datetime('2022-05-20')] | dict.fromkeys(['ES=F','NQ=F','RTY=F'], 0.05) #Add Hedges Where Applicable
pig = pd.DataFrame.from_dict(pos,orient='index').fillna(0.0) 
pig.index.name = 'Date'
prices = bt.get(list(pig), clean_tickers=False, start=pig.first_valid_index(), end=date.today())
for i in range(1,45): #Add Future Data for What If Scenario: Bear Market Rally in Short Positions and Hedges, Longs Flat
    bmr = pd.DataFrame(prices[-1:].values, index=[prices.index[-1] + timedelta(days=1)], columns=prices.columns)
    for c in bmr.columns: bmr[c] = bmr[c]*(1.02-(i%2)*0.03) if pig[c].values[-1]<0 or pig[c].values[-1]==pig['ES=F'].values[-1] else bmr[c]   
    prices = pd.concat([prices, bmr])
report = bt.run(bt.Backtest(bt.Strategy('Pig ETF Proxy (Hedged)', algos=[bt.algos.SelectAll(), bt.algos.WeighTarget(pig), bt.algos.Rebalance()]), prices))
report.display()
report.plot()
plt.title('The Power of the Hedgehog PIG Portfolio\nWhat If Scenario: 24% Bear Market Rally')
plt.show()
