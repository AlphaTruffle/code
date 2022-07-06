# region imports
from AlgorithmImports import *
from datetime import timedelta
import datetime
import numpy as np
import pandas as pd
# endregion

class EightVolSignals(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2015, 1, 1)  # Set Start Date
        self.SetCash(100000)  # Set Strategy Cash
        # 8 Signals Derived from VIX and its forward curve.
        # https://medium.datadriveninvestor.com/how-to-harness-the-power-of-vix-to-protect-your-portfolio-part-3-bbfa12ba7c38
        self.VRatio = self.Contango = self.ContangoRoll = self.VRP = self.FVRP = self.VolMomo = self.VIXMR = self.VIX3MMR = 0.0
        self.Signals = {"VRatio": 0, "Contango": 0, "ContangoRoll": 0, "VRP": 0, "FVRP": 0, "VolMomo": 0, "VIXMR": 0, "VIX3MMR": 0}
        self.RiskOn = 0.0
        self.Allocated = 0.0
        # Data 
        self.spy = self.AddEquity("SPY", Resolution.Hour)
        self.vix = self.AddIndex("VIX", Resolution.Hour)
        self.spx = self.AddIndex("SPX", Resolution.Hour)
        self.cgo = self.AddData(VIXCentralContango, "VX", Resolution.Daily).Symbol
        self.SetBenchmark(SecurityType.Equity, "SPY")
        # Indicators
        self.vixEMA7 = self.EMA("VIX", 7, Resolution.Hour)
        self.vixSMA50 = self.SMA("VIX", 50, Resolution.Hour)
        self.spxLOGR = self.LOGR("SPX", 1, Resolution.Daily)
        self.spxSlowSTD = IndicatorExtensions.Of(StandardDeviation(10), self.spxLOGR)
        self.spxFastSTD = IndicatorExtensions.Of(StandardDeviation(5), self.spxLOGR)
        self.spxSlowHV = self.spxFastHV = 0.0
        # VIX History 
        self.vixWindow = RollingWindow[TradeBar](66)
        self.vixHistory = self.History(self.vix.Symbol, 66, Resolution.Daily)
        for time, row in self.vixHistory.loc[self.vix.Symbol].iterrows():     
            self.vixWindow.Add(TradeBar(time.date(), self.vix.Symbol, row.open, row.high, row.low, row.close, 0.0))
        self.vix3M = self.vixWindow[self.vixWindow.Count-1].Close
        self.vixLast = self.vixWindow[0].Close
        self.contLast = None 
        # Warm Up
        self.SetWarmUp(66)

    def OnData(self, data: Slice):
        if self.IsWarmingUp: return

        if data.ContainsKey("VX.VIXCentralContango"): 
            self.contLast = data["VX.VIXCentralContango"]
        
        if self.Time.hour != 15: return

        if data.ContainsKey("VIX"): 
            self.vixWindow.Add(data["VIX"])    
            self.vix3M = self.vixWindow[self.vixWindow.Count-1].Close
            self.vixLast = data["VIX"].Close
            self.spxSlowHV = float(self.spxSlowSTD.Current.Value * np.sqrt(365))*100
            self.spxFastHV = float(self.spxFastSTD.Current.Value * np.sqrt(365))*100
            # Calculate 8 Signals
            self.VRatio = self.vix3M / self.vixLast #VIX3M/VIX, VRatio > 1 = Risk ON
            self.Contango = self.contLast.Contango_F2_Minus_F1 #VX2/VX1-1, Contanto > -5%, Risk ON
            self.ContangoRoll = (self.contLast.F2 / self.vixLast) - 1 #VX2/VIX-1, Contango Roll > 10%, Risk ON
            self.VRP = self.vixLast - self.spxSlowHV #VIX-HV10(SPX), Volatility Risk Premium (VRP) > 0, Risk ON
            self.FVRP = self.vixEMA7.Current.Value - self.spxFastHV #EMA(VIX,7)-HV5(SPX), FVRP > 0, Risk ON
            self.VolMomo = self.vixSMA50.Current.Value - self.vixLast #SMA(VIX,50)-VIX, Volatility Momentum > 0, Risk ON
            self.VIXMR = 1.0 if self.vixLast > 12 and self.vixLast < 20 else 0.0 #VIX Mean Reversion, VIX > 12 and VIX < 20, Risk ON
            self.VIX3MMR = 1.0 if self.vix3M > 12 and self.vix3M < 20 else 0.0 #VIX3M Mean Reversion, VIX3M > 12 and VIX3M < 20, Risk ON
            # Set Signals Risk On or Risk Off
            if sum(self.Signals.values()) < 4: self.RiskOn = 0.0
            self.Signals["VRatio"] = 1 if self.VRatio > 1 else 0
            self.Signals["Contango"] = 1 if self.Contango > -0.05 else 0
            self.Signals["ContangoRoll"] = 1 if self.ContangoRoll > 0.1 else 0
            self.Signals["VRP"] = 1 if self.VRP > 0 else 0
            self.Signals["FVRP"] = 1 if self.FVRP > 0 else 0
            self.Signals["VolMomo"] = 1 if self.VolMomo > 0 else 0
            self.Signals["VIXMR"] = 1 if self.VIXMR == 1.0 else 0
            self.Signals["VIX3MMR"] = 1 if self.VIX3MMR == 1.0 else 0
            #Set Risk On/Off
            if sum(self.Signals.values()) >= 4: self.RiskOn += 0.5 
            else: self.RiskOn = 0.0
            if self.RiskOn > 1.0: self.RiskOn = 1.0
            # Debug Print Out
            self.Debug(f"{self.Time.date()} Risk:{self.RiskOn} {self.Signals} {data['VIX'].Close:.2f} {round(data['SPX'].Close):.0f}")
            #Trade
            if self.RiskOn == 0.0: 
                if self.Allocated >= 0:
                    self.Allocated = -0.9
                    self.SetHoldings("SPY", self.Allocated)
            elif self.RiskOn == 1.0: 
                if self.Allocated <= 0:
                    self.Allocated = 0.9
                    self.SetHoldings("SPY", self.Allocated)
