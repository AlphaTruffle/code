import bt
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from datetime import date, timedelta
matplotlib.use('MacOSX')

#### VOLQ PIG PORTFOLIO ####
pig_shorts, pig_longs, pig_hedges, pig_cashpct, pig_hedgepct, pig_rebaldates, pig_positions  = [],[],[],[],[],[],[]

pig_rebaldates.append('2021-11-09') ## 09 Nov 2021: Initial Pig Portfolio.
pig_shorts.append({'FB','MSFT','REM', 'GOOGL','QQQ','AMZN','GSG','DIA','GDX','SPY','LQD','HYG','IGSB','TLT','AAPL','EMB','IWM','NVDA','VGK','EEM','VNQ','CPER','BITO'})
pig_longs.append({'IEI','SHY','SHV','BIL','GLD','UUP','FXF','FXY','VXX'})
pig_hedges.append({})
pig_cashpct.append(0.0)
pig_hedgepct.append(0.0)

pig_rebaldates.append('2022-02-24') ## 24 May 2022: Risk Management Exited Commodity Shorts.
pig_shorts.append({'TLT','EMB','IWM','DIA','SPY','QQQ','EEM','VGK','REM','VNQ','BITO','LQD','HYG','IGSB','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'})
pig_longs.append({'IEI','SHY','SHV','BIL','UUP','FXF','FXY','VXX','GLD'})
pig_hedges.append({})
pig_cashpct.append(0.0)
pig_hedgepct.append(0.0)

pig_rebaldates.append('2022-03-31') ## 31 Mar 2022: Quarterly Rebalance. Added Semiconductor, US & EU Financials, JNK Shorts. Added SLV Long. Went to 25% Cash.
pig_shorts.append({'TLT','EMB','IWM','DIA','SPY','QQQ','EFA','EEM','VGK','REM','VNQ','SMH','JNK','IJH','BITO','LQD','HYG','IGSB','XLF','EUFN','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'})
pig_longs.append({'BIL','SHV','SHY','IEI','STIP','UUP','FXF','FXY','GLD','SLV'})
pig_hedges.append({})
pig_cashpct.append(0.25)
pig_hedgepct.append(0.0)

pig_rebaldates.append('2022-05-20') ## 20 May 2022: Hedged Pig. Added Dirty Beta Hedge, 5% ES=F, 5% RTY-F, 5% NQ=F. Went to 35% Cash.
pig_shorts.append({'TLT','EMB','IWM','DIA','SPY','QQQ','EFA','EEM','VGK','REM','VNQ','SMH','JNK','IJH','BITO','LQD','HYG','IGSB','XLF','EUFN','AAPL','AMZN','FB','GOOGL','MSFT','NVDA'})
pig_longs.append({'BIL','SHV','SHY','IEI','STIP','UUP','FXF','FXY','GLD','SLV'})
pig_hedges.append({'ES=F','RTY=F','NQ=F'})
pig_cashpct.append(0.35)
pig_hedgepct.append(0.15)

for i,v in enumerate(pig_rebaldates): ## Equal Weight Longs and Shorts based on Core % Invested (100%-Cash%-Hedge%). Equal Weight Hedge positions based on Hedge%.
    s, l, h = {},{},{}
    for key in pig_shorts[i]: s[key] = (1-(pig_cashpct[i]+pig_hedgepct[i]))/(len(pig_shorts[i])+len(pig_longs[i])) * -1 
    for key in pig_longs[i]:  l[key] = (1-(pig_cashpct[i]+pig_hedgepct[i]))/(len(pig_shorts[i])+len(pig_longs[i]))
    for key in pig_hedges[i]: h[key] = pig_hedgepct[i]/len(pig_hedges[i])
    pig_positions.append(s|l|h)
pig_weights = pd.DataFrame(pig_positions, index=pig_rebaldates)
pig_weights = pig_weights.fillna(0.0)
pig_weights.index = pd.to_datetime(pig_weights.index)
pig_weights.index.name = "Date"

pig_prices  = bt.get(list(pig_weights), clean_tickers=False, start='2021-11-09', end=date.today()-timedelta(days=1))
pig_strategy = bt.Strategy('Pig Portfolio', 
 algos = [
 bt.algos.SelectAll(),
 bt.algos.WeighTarget(pig_weights),
 bt.algos.Rebalance(),
 ]
)
pig_bt = bt.Backtest(pig_strategy,pig_prices)
#### END VOLQ PIG PORTFOLIO ####

#### RPAR ETF ####
rpar_prices = bt.get(['RPAR'], clean_tickers=False, start='2021-11-09', end=date.today()-timedelta(days=1))
rpar_strategy = bt.Strategy('RPAR ETF', 
 algos = [  
 bt.algos.SelectAll(),
 bt.algos.WeighEqually(),
 bt.algos.Rebalance(),
 ]
)
rpar_bt = bt.Backtest(rpar_strategy,rpar_prices)
#### END RPAR ETF ####

#### SHOW REPORT ####
report = bt.run(pig_bt,rpar_bt)
report.display()
report.display_monthly_returns()
report.plot()
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100.0))
plt.title('Pig Portfolio (No Wifey 3x, Intras, Or Options) vs. Risk Parity ETF')
plt.show()
#### END SHOW REPORT ####
