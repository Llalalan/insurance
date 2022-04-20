import copy

import requests
import pandas as pd
import time
import numpy as np
import data
import portfolio
import datetime as dt


def cal_macd(df,feature='Close'):
    '''
    :param df: Dataframe containing OHLCV data
    :param feature: str column name used to calculate macd
    :return: Series macd result
    '''
    k = df[feature].ewm(span=12, adjust=False, min_periods=12).mean()
    d = df[feature].ewm(span=26, adjust=False, min_periods=26).mean()
    macd_aa = k - d
    macd_s = macd_aa.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd_aa - macd_s
    return macd_h

def cal_macd_close_target(df,ema12=None,ema26=None,dea=None):
    '''
    Use binance data to calculate the target macd
    :param df: Dataframe of source data
    :param ema12: ema12 value obtained from binance
    :param ema26: ema26 value obtained from binance
    :param dea: dea value obtained from binance
    :return: Series of target macd
    '''
    macd_test = copy.deepcopy(df)
    macd_test['ema12'] = None
    macd_test['ema26'] = None
    macd_test['diff'] = None
    macd_test['dea'] = None
    macd_test['macd'] = None
    macd_test['ema12'][0] = ema12
    macd_test['ema26'][0] = ema26
    macd_test['dea'][0] = dea
    for i in range(1, len(macd_test)):
        macd_test['ema12'].iloc[i] = macd_test['ema12'].iloc[i - 1] * 11 / 13 + macd_test['Close'].iloc[i] * 2 / 13
        macd_test['ema26'].iloc[i] = macd_test['ema26'].iloc[i - 1] * 25 / 27 + macd_test['Close'].iloc[i] * 2 / 27
        macd_test['diff'].iloc[i] = macd_test['ema12'].iloc[i] - macd_test['ema26'].iloc[i]
        macd_test['dea'].iloc[i] = macd_test['dea'].iloc[i - 1] * 8 / 10 + macd_test['diff'].iloc[i] * 2 / 10
        macd_test['macd'].iloc[i] = macd_test['diff'].iloc[i] - macd_test['dea'].iloc[i]
    return macd_test['macd']

def cal_signal(macd):
    '''
    calculate macd signal
    :param macd: Series of macd values in a specific time
    :return: signal generated in a specific time
    '''
    if (macd[-2] - macd[-1] > 0) and (macd[-3] - macd[-2] < 0):
        return 'maxima'
    elif (macd[-2] - macd[-1] < 0) and (macd[-2] - macd[-3] < 0):
        return 'minima'
    elif np.abs((macd[-1] - macd[-2]) / macd[-2]) > 4:
        print(np.abs((macd[-1] - macd[-2]) / macd[-2]))
        return 'change too much'
    else:
        return 'not signal'





# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 拉数据
    start_time_list = [2021,9,1]
    end_time_list = [2022,3,1]
    # df = data.request_data_now()
    df = data.request_data_15min(start_time_list,end_time_list)
    df['hlmid'] = (df['High'] + df['Low'])/2
    df['ocmid'] = (df['Open'] + df['Close'])/2
    df['ma'] = df['Close'].rolling(6).mean()
    print(df.iloc[0])
    # 用close计算macd
    macd = cal_macd(df,'Close')
    # 用close检查macd，结果为200后基本一样
    # macd_close_target = cal_macd_close_target(df,ema12=3527.38,ema26=3517.13,dea=10.18)
    # print(macd.index[180])
    # print('target',macd_close_target[180])
    # print('result',macd[180])
    # 取时间间隔
    # 用high-low mid计算macd
    macd_hlmid = cal_macd(df,'Close')
    # 计算信号
    macd_hlmid = macd_hlmid.iloc[180:]
    signal = pd.Series(data=None,index=macd_hlmid.index,dtype=object)
    for i in range(2,len(macd_hlmid)):
        signal[i] = cal_signal(macd_hlmid[i-2:i+1])
    initial_cash=3000
    result_df = pd.DataFrame()
    insurance_list = np.linspace(1,100,100)
    ratio_list = np.linspace(0,0.1,50)
    for insurance_ratio in ratio_list:
        insurance_result = []
        for insurance_times in insurance_list:
            porfolio = portfolio.cal_portfolio_long_with_insurance(df,initial_cash,macd_hlmid,signal,insurance_times,insurance_ratio)
            print(insurance_times,':',porfolio['Total'][-1])
            insurance_result.append(porfolio['Total'][-1])
        result_df[str(insurance_ratio)] = insurance_result
    result_df.to_csv('insurance_strategy_result.csv')

