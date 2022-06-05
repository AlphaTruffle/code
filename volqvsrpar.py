import matplotlib
import bt
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
from datetime import date
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.colheader_justify', 'center')
pd.set_option('display.precision', 3)
matplotlib.use('MacOSX')

shorts, longs, hedges, cashpct, hedgepct, ew, pigs  = [],[],[],[],[],[],[]

## 2021-11-09
shorts.append({'FB','MSFT','REM', 'GOOGL','QQQ','AMZN','GSG','DIA','GDX','SPY','LQD','HYG','IGSB','TLT','AAPL','EMB','IWM','NVDA','VGK','EEM','VNQ','CPER','BITO'})
longs.append({'IEI','SHY','SHV','BIL','GLD','UUP','FXF','FXY','VXX'})
hedges.append({})
cashpct.append(0.0)
hedgepct.append(0.0)

## 2022-02-24
shorts.append({'TLT','EMB','IWM','DIA','SPY','QQQ','EEM','VGK','REM','VNQ','BITO','LQD','HYG','IGSB','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'})
longs.append({'IEI','SHY','SHV','BIL','UUP','FXF','FXY','VXX','GLD'})
hedges.append({})
cashpct.append(0.0)
hedgepct.append(0.0)

## 2022-03-31
shorts.append({'TLT','EMB','IWM','DIA','SPY','QQQ','EFA','EEM','VGK','REM','VNQ','SMH','JNK','IJH','BITO','LQD','HYG','IGSB','XLF','EUFN','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'})
longs.append({'BIL','SHV','SHY','IEI','STIP','UUP','FXF','FXY','GLD','SLV'})
hedges.append({})
cashpct.append(0.25)
hedgepct.append(0.0)

## 2022-05-20
shorts.append({'TLT','EMB','IWM','DIA','SPY','QQQ','EFA','EEM','VGK','REM','VNQ','SMH','JNK','IJH','BITO','LQD','HYG','IGSB','XLF','EUFN','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'})
longs.append({'BIL','SHV','SHY','IEI','STIP','UUP','FXF','FXY','GLD','SLV'})
hedges.append({'ES=F','RTY=F','NQ=F'})
cashpct.append(0.35)
hedgepct.append(0.15)

## Build DataFrame
for i,v in enumerate(shorts):
    s, l, h = {},{},{}
    for key in shorts[i]: s[key] = (1-(cashpct[i]+hedgepct[i]))/(len(shorts[i])+len(longs[i])) * -1
    for key in longs[i]:  l[key] = (1-(cashpct[i]+hedgepct[i]))/(len(shorts[i])+len(longs[i]))
    for key in hedges[i]: h[key] = hedgepct[i]/len(hedges[i])
    pigs.append(s|l|h)    
pig_positions = pd.DataFrame(pigs, index=['2021-11-09',
                                          '2022-02-24',
                                          '2022-03-31',
                                          '2022-05-20'])
pig_positions.index.name = "Date"
pig_positions.index = pd.to_datetime(pig_positions.index)
pig_positions = pig_positions.fillna(0.0)
pig_prices  = bt.get(list(pig_positions), clean_tickers=False, start='2021-11-09')
pig_weights = pig_prices.copy()
rebal_dates = list(pig_positions.index.values)
rebal_dates.append(date.today())
for ticker in list(pig_weights):
    for i,v in enumerate(rebal_dates):
        if i < len(rebal_dates)-1:
            pig_weights[ticker][rebal_dates[i]:(rebal_dates[i+1]-pd.to_timedelta(1,unit='days'))] = pig_positions[ticker][rebal_dates[i]]

print(pig_weights)
print(pig_positions)
        
pig_strategy = bt.Strategy('Pig Portfolio', 
 algos = [
 bt.algos.SelectAll(),
 bt.algos.WeighTarget(pig_weights),
 bt.algos.Rebalance(),
 ]
)

rpar_prices = bt.get(['RPAR'], clean_tickers=False, start='2021-11-09')
rpar_strategy = bt.Strategy('RPAR ETF', 
 algos = [
 bt.algos.RunOnce(),    
 bt.algos.SelectAll(),
 bt.algos.WeighEqually(),
 bt.algos.Rebalance(),
 ]
)

pig_bt = bt.Backtest(pig_strategy,pig_prices)
rpar_bt = bt.Backtest(rpar_strategy,rpar_prices)
report = bt.run(pig_bt,rpar_bt)
report.display()
report.plot()
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100.0))
plt.title('Pig Portfolio (No Wifey 3x, Intras, Or Options) vs. Risk Parity ETF')
plt.show()

