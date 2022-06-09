import bt
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from datetime import date, timedelta
matplotlib.use('MacOSX') #On Windows, matplotlib.use('TkAgg') or whatever you like, sirs.

startdate = '2022-01-01'
sf_bt = bt.Backtest(data=bt.get(['SPY','TLT'], clean_tickers=False, start=startdate, end=date.today()-timedelta(days=1)),strategy=bt.Strategy('60/40 SPY/TLT Buy & Hold', algos=[bt.algos.RunOnce(),bt.algos.SelectAll(),bt.algos.WeighSpecified(SPY=0.6,TLT=0.4),bt.algos.Rebalance()]))
sfm_bt = bt.Backtest(data=bt.get(['SPY','TLT'], clean_tickers=False, start=startdate, end=date.today()-timedelta(days=1)),strategy=bt.Strategy('60/40 SPY/TLT Monthly Rebal', algos=[bt.algos.RunMonthly(),bt.algos.SelectAll(),bt.algos.WeighSpecified(SPY=0.6,TLT=0.4),bt.algos.Rebalance()]))
sfq_bt = bt.Backtest(data=bt.get(['SPY','TLT'], clean_tickers=False, start=startdate, end=date.today()-timedelta(days=1)),strategy=bt.Strategy('60/40 SPY/TLT Quarterly Rebal', algos=[bt.algos.RunQuarterly(),bt.algos.SelectAll(),bt.algos.WeighSpecified(SPY=0.6,TLT=0.4),bt.algos.Rebalance()]))
report = bt.run(sf_bt,sfm_bt,sfq_bt)
report.display()
report.plot()
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=100.0))
plt.title('SPY/TLT Buy & Hold vs Monthly vs Quarterly')
plt.show()
