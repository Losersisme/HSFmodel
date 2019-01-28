#Import Libraries:
from pandas import *
import pandas as pd
from datetime import *
import time
import numpy as np
from itertools import product

st = time.time()

#Define risk-free rates
TBill3Mth = (2.34/100)
Libor3Mth = (2.62/100)

pd.options.mode.chained_assignment = None #allow chained assignment

#Import main data into spyx DF
spyx = read_csv("Backtest VALUES.csv",index_col='DATE',parse_dates=True)

#Fix FCF to be P/FCF and Adjust Beta
#spyx['PRICE_TO_FCF']=spyx['CUR_MKT_CAP']/spyx['CF_FREE_CASH_FLOW']
#spyx['ADJUSTED_BETA']=((0.67)*spyx['BETA_RAW_OVERRIDABLE']+(0.33)*1.0)

#Choose sector
sector = 'Financials'

#new DF based on sector
spyx_Sector = spyx.loc[spyx['GICS_SECTOR_NAME']==sector]

#drop rows without a date
spyx_Sector.dropna(axis='index',how='any',inplace=True)

#Define starting date to begin df with
startDate = to_datetime('2014-03-28')
startDate=startDate.toordinal()

#Cut spyx_Sector based on DateTime range
spyx_Sector['ordinalTime']=spyx_Sector.index
spyx_Sector['ordinalTime'] = spyx_Sector['ordinalTime'].apply(date.toordinal)
spyx_Sector = spyx_Sector.loc[spyx_Sector['ordinalTime']>=startDate]

#define ranges for cartesian product
# Financials
peRange =  range(11, 19, 2)
pbRange =  range(1, 2)
epsRange =  range(2, 5, 2)
deRange =  range(29, 121, 10)
fcfRange =  range(6, 18, 5)
roeRange =  range(6, 14, 2)
roaRange =  range(1, 3, 2)

#Create set of dates
datesList = sorted(set(spyx_Sector.index))

#Create new Output DF for portfolios for dates
dfPort = pd.DataFrame([],index=datesList)
dfPort['return']=None
dfPort['beta']=None
dfPort['tBill3Mth']=TBill3Mth
dfPort['treynor']=None
dfPort['peTest']=None
dfPort['pbTest']=None
dfPort['epsTest']=None
dfPort['deTest']=None
dfPort['fcfTest']=None
dfPort['roeTest']=None
dfPort['roaTest']=None
dfPort['maxHSFScore']=None

#Function to output every indivdual portfolio inside each period
def outputIndPeriod(df, date):
        df.to_csv(sector+"IndPortPeriod"+time.strftime("d%dm%my%Y")+".csv", mode='a')

#Function to loop through every date and output an individual portfolio
def calulatePortLoop(dateList, params):
    for date in datesList:
        df = spyx_Sector.loc[spyx_Sector.index==date]
        df['peTest']=params[0]
        df['pbTest']=params[1]
        df['epsTest']=params[2]
        df['deTest']=params[3]
        df['fcfTest']=params[4]
        df['roeTest']=params[5]
        df['roaTest']=params[6]
        df['peScore']=df['PE_RATIO']<params[0]
        df['pbScore']=df['PX_TO_BOOK_RATIO']<params[1]
        df['epsScore']=df['TRAIL_12M_EPS']>params[2]
        df['deScore']=df['TOT_DEBT_TO_TOT_EQY']<params[3]
        df['fcfScore']=df['PRICE_TO_FCF']>params[4]
        df['roeScore']=df['RETURN_COM_EQY']>params[5]
        df['roaScore']=df['RETURN_ON_ASSET']>params[6]
        df['betaScore']=1/(df['ADJUSTED_BETA']*1000)
        df['hsfScore']=df['peScore'].astype(int)+df['pbScore'].astype(int)+df['epsScore'].astype(int)+\
            df['deScore'].astype(int)+df['fcfScore'].astype(int)+df['roeScore'].astype(int)+df['roaScore'].astype(int)
        df['betaScore']
        df['ind']="T"+df['peTest'].map(str)+df['pbTest'].map(str)+df['epsTest'].map(str)+df['deTest'].map(str)+\
            df['fcfTest'].map(str)+df['roeTest'].map(str)+df['roaTest'].map(str)
        df.sort_values(by='hsfScore',ascending=False,inplace=True)
        df=df.iloc[0:5]
        outputIndPeriod(df,date)
        dfPort.loc[dfPort.index==date,'peTest'] = df.ix[0,'peTest']
        dfPort.loc[dfPort.index==date,'pbTest'] = df.ix[0,'pbTest']
        dfPort.loc[dfPort.index==date,'epsTest'] = df.ix[0,'epsTest']
        dfPort.loc[dfPort.index==date,'deTest'] = df.ix[0,'deTest']
        dfPort.loc[dfPort.index==date,'fcfTest'] = df.ix[0,'fcfTest']
        dfPort.loc[dfPort.index==date,'roeTest'] = df.ix[0,'roeTest']
        dfPort.loc[dfPort.index==date,'roaTest'] = df.ix[0,'roaTest']
        dfPort.loc[dfPort.index==date,'maxHSFScore'] = df['hsfScore'].max()
        dfPort.loc[dfPort.index==date,'return'] = (df['RETURN'].mean())
        dfPort.loc[dfPort.index==date,'beta'] = (df['ADJUSTED_BETA'].mean())
    dfPort['treynor']=(dfPort['return']-TBill3Mth)/dfPort['beta']
    dfPort['ind']="T"+dfPort['peTest'].map(str)+dfPort['pbTest'].map(str)+dfPort['epsTest'].map(str)+dfPort['deTest'].map(str)+\
        dfPort['fcfTest'].map(str)+dfPort['roeTest'].map(str)+dfPort['roaTest'].map(str)
    return dfPort

#Create new Output DF for total portfolios
dfTotalPort = pd.DataFrame([])
dfTotalPort['ind']=list(product(peRange,pbRange,epsRange,deRange,fcfRange,roeRange,roaRange))
dfTotalPort['meanReturn']=None
dfTotalPort['meanBeta']=None
dfTotalPort['tBill3Mth']=TBill3Mth
dfTotalPort['totalTreynor']=None
dfTotalPort['peTest']=None
dfTotalPort['pbTest']=None
dfTotalPort['epsTest']=None
dfTotalPort['deTest']=None
dfTotalPort['fcfTest']=None
dfTotalPort['roeTest']=None
dfTotalPort['roaTest']=None

#output each portfolio with dates
def outputIndPort(dfPort,params):
    dfPort.to_csv(sector+"IndividualPortfolios"+time.strftime("d%dm%my%Yh")+".csv", \
                  mode='a',index_label=("T"+str(params[0])+str(params[1])+str(params[2])+str(params[3])\
                        +str(params[4])+str(params[5])+str(params[6])))

#Output total portfolio with parameters
def outputTotalPort(dfTotalPort,params):
    dfTotalPort.to_csv(sector+"TotalPortfolio"+time.strftime("d%dm%my%Yh")+".csv", mode='w',index_label=("T"+"Portfolio"))

for params in product(peRange, pbRange, epsRange, deRange, fcfRange, roeRange, roaRange):
    calulatePortLoop(datesList, params)
    dfTotalPort.loc[dfTotalPort['ind']==params,'meanReturn'] = dfPort['return'].mean()
    dfTotalPort.loc[dfTotalPort['ind']==params,'meanBeta'] = dfPort['beta'].mean()
    dfTotalPort.loc[dfTotalPort['ind']==params,'peTest'] = params[0]
    dfTotalPort.loc[dfTotalPort['ind']==params,'pbTest'] = params[1]
    dfTotalPort.loc[dfTotalPort['ind']==params,'epsTest'] = params[2]
    dfTotalPort.loc[dfTotalPort['ind']==params,'deTest'] = params[3]
    dfTotalPort.loc[dfTotalPort['ind']==params,'fcfTest'] = params[4]
    dfTotalPort.loc[dfTotalPort['ind']==params,'roeTest'] = params[5]
    dfTotalPort.loc[dfTotalPort['ind']==params,'roaTest'] = params[6]
    #print(dfPort)
    outputIndPort(dfPort,params)
dfTotalPort['totalTreynor']=(dfTotalPort['meanReturn']-dfTotalPort['tBill3Mth'])/dfTotalPort['meanBeta']
dfTotalPort.sort_values('totalTreynor',ascending=False, inplace=True)
dfTotalPort.set_index("T"+dfTotalPort['peTest'].map(str) + dfTotalPort['pbTest'].map(str) +\
                      dfTotalPort['epsTest'].map(str) + dfTotalPort['deTest'].map(str) +\
                      dfTotalPort['fcfTest'].map(str) + dfTotalPort['roeTest'].map(str) +\
                      dfTotalPort['roaTest'].map(str), inplace = True)
outputTotalPort(dfTotalPort,params)

print('Runtime: ', time.time() - st,)