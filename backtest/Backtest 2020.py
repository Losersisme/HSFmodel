from pandas import *
import pandas as pd
from datetime import *
import time
import numpy as np
from itertools import product
from IPython.display import display

metrics = [ 'PE_RATIO', 'PX_TO_BOOK_RATIO', 'TRAIL_12M_EPS', 'TOT_DEBT_TO_TOT_EQY', 'PX_TO_FREE_CASH_FLOW', 'RETURN_COM_EQY', 'RETURN_ON_ASSET' ]

dfTests = ['peTest','pbTest','epsTest','deTest','fcfTest','roeTest','roaTest']
dfScores = ['peScore','pbScore','epsScore','deScore','fcfScore','roeScore','roaScore']

lvhs_metrics = [ 'PE_RATIO', 'TOT_DEBT_TO_TOT_EQY', 'PX_TO_BOOK_RATIO' ]
hvhs_metrics = [ 'TRAIL_12M_EPS', 'PRICE_TO_FCF', 'RETURN_COM_EQY', 'RETURN_ON_ASSET' ]

pd.options.mode.chained_assignment = None

totalDF = read_csv("Backtest VALUES 2020.csv",index_col='DATE',parse_dates=True)

totalDF = totalDF.sort_index()

totalDF.dropna(axis='index',how='any',inplace=True)

startDate = to_datetime('2015-09-01')
startDate=startDate.toordinal()

totalDF['ordinalTime']=totalDF.index
totalDF['ordinalTime'] = totalDF['ordinalTime'].apply(date.toordinal)
totalDF = totalDF.loc[totalDF['ordinalTime']>=startDate]

datesList = sorted(set(totalDF.index))
sectors = totalDF.GICS_SECTOR_NAME.unique()

totalDF_ranges = pd.read_excel("Backtest VALUES 2020.xlsx", index_col=[0,1])
totalDF_ranges = totalDF_ranges.sort_index()
totalDF_ranges.groupby('GICS_SECTOR_NAME').nunique()

def getNormal(metric, step):
    return range(int(round(np.percentile(totalDF_ranges.loc[(slice(None), sector), metric].dropna(), 34))),                      int(round(np.percentile(totalDF_ranges.loc[(slice(None), sector), metric].dropna(), 68))), step)

def getRanges():
    global peRange, pbRange, epsRange, deRange, fcfRange, roeRange, roaRange
    
    peRange =  getNormal('PE_RATIO', 2)
    pbRange =  getNormal('PX_TO_BOOK_RATIO', 1)
    epsRange =  getNormal('TRAIL_12M_EPS', 2)
    deRange =  getNormal('TOT_DEBT_TO_TOT_EQY', 10)
    fcfRange =  getNormal('TOT_DEBT_TO_TOT_EQY', 5)
    roeRange =  getNormal('RETURN_COM_EQY', 2)
    roaRange =  getNormal('RETURN_ON_ASSET', 2)

now = time.strftime("d%dm%my%Y")
def outputIndPeriod(portfolioDF, date):
        portfolioDF.to_csv("results/"+sector+"IndPortPeriod"+now+".csv", mode='a')
        
def outputIndPort(portSummaryDF, frame):
    portSummaryDF.to_csv("results/"+sector+"_PortfolioAvgsPerPeriod"+now+".csv",                   mode='a',index_label=("T"+str(frame[0])+str(frame[1])+str(frame[2])+str(frame[3])                        +str(frame[4])+str(frame[5])+str(frame[6])))

def outputTotalPort(dfTotalPort, frame):
    dfTotalPort.to_csv("results/"+sector+"TotalPortfolio"+now+".csv", mode='w',index_label=("T"+"Portfolio"))
    
def createIdentifier(frame):
    name = "T"
    for p in frame:
        name+=str(p)
    return name

def calculatePortLoop(dateList, frame, identity):
    
    for date in datesList:
        
        portfolioDF = sectorDF.loc[sectorDF.index==date]
        
        for x in range(7):
            portfolioDF[dfTests[x]] = frame[x]
        
        for x in range(7):
            if metrics[x] in lvhs_metrics:
                portfolioDF[dfScores[x]] = portfolioDF[metrics[x]] < frame[x]
            else:
                portfolioDF[dfScores[x]] = portfolioDF[metrics[x]] > frame[x]
        
        portfolioDF['betaScore']=1/(portfolioDF['ADJUSTED_BETA']*1000)
        portfolioDF['hsfScore'] = None
        for x in range(7):
            portfolioDF['hsfScore']=portfolioDF['hsfScore']+portfolioDF[dfScores[x]].astype(int)
            
        portfolioDF['ind'] = identity
        
        portfolioDF.sort_values(by='hsfScore',ascending=False,inplace=True)
        portfolioDF=portfolioDF.iloc[0:5]
        
        if iperiods:
            outputIndPeriod(portfolioDF, date)
        
        for t in dfTests:
            portSummaryDF.loc[portSummaryDF.index==date, t] = portfolioDF.ix[0, t]
        
        portSummaryDF.loc[portSummaryDF.index==date,'maxHSFScore'] = portfolioDF['hsfScore'].max()
        portSummaryDF.loc[portSummaryDF.index==date,'return'] = (portfolioDF['RETURN'].mean())
        portSummaryDF.loc[portSummaryDF.index==date,'beta'] = (portfolioDF['ADJUSTED_BETA'].mean()+0.0000001)

    portSummaryDF['treynor']=(portSummaryDF['return']-TBill3Mth)/portSummaryDF['beta']
    portSummaryDF['ind'] = identity

    return portSummaryDF

def prod():
    
    for frame in product(peRange, pbRange, epsRange, deRange, fcfRange, roeRange, roaRange):
        identifier = createIdentifier(frame)
        calculatePortLoop(datesList, frame, identifier)
        dfTotalPort.loc[dfTotalPort['ind']==frame,'meanReturn'] = portSummaryDF['return'].mean()
        dfTotalPort.loc[dfTotalPort['ind']==frame,'meanBeta'] = portSummaryDF['beta'].mean()
        for x in range(7):
            dfTotalPort.loc[dfTotalPort['ind']==frame, dfTests[x]] = frame[x]
        
        if iports:
            outputIndPort(portSummaryDF, frame)
        
    dfTotalPort['totalTreynor']=(dfTotalPort['meanReturn']-dfTotalPort['tBill3Mth'])/dfTotalPort['meanBeta']
    dfTotalPort.sort_values('totalTreynor',ascending=False, inplace=True)
    dfTotalPort.set_index("T"+dfTotalPort['peTest'].map(str) + dfTotalPort['pbTest'].map(str) +                      dfTotalPort['epsTest'].map(str) + dfTotalPort['deTest'].map(str) +                      dfTotalPort['fcfTest'].map(str) + dfTotalPort['roeTest'].map(str) +                      dfTotalPort['roaTest'].map(str), inplace = True)
    
    outputTotalPort(dfTotalPort, frame)

def runSingleSector(sectorChosen, tbill, libor, IndPortfolios, IndPeriods):

    global sector
    sector = sectorChosen
    
    getRanges()

    global sectorDF
    sectorDF = totalDF.loc[totalDF['GICS_SECTOR_NAME']==sector]
    
    global TBill3Mth
    TBill3Mth = tbill/100
    global Libor3Mth
    Libor3Mth = libor/100
    
    global iports
    iports = IndPortfolios
    global iperiods
    iperiods = IndPeriods
    
    global portSummaryDF
    portSummaryDF = pd.DataFrame([],index=datesList)
    portSummaryDF['return']=None
    portSummaryDF['beta']=None
    portSummaryDF['tBill3Mth']=TBill3Mth
    portSummaryDF['treynor']=None
    for x in range(7):
            portSummaryDF[dfTests[x]] = None
    portSummaryDF['maxHSFScore']=None

    global dfTotalPort
    dfTotalPort = pd.DataFrame([])
    dfTotalPort['ind']=list(product(peRange,pbRange,epsRange,deRange,fcfRange,roeRange,roaRange))
    dfTotalPort['meanReturn']=None
    dfTotalPort['meanBeta']=None
    dfTotalPort['tBill3Mth']=TBill3Mth
    dfTotalPort['totalTreynor']=None
    for x in range(7):
            dfTotalPort[dfTests[x]] = None

    prod()

start = time.time()

The two lines below would allow us to run all sectors at once
for s in sectors:
    runSingleSector(s, 0.09, 0.23, False, False)

stop = time.time()

print('Time: ', stop - start)  

