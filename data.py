import requests
import pandas as pd
import time
import json
import datetime as dt
import os

def timestamp_to_fomat(timestamp=None, format='%Y-%m-%d %H:%M:%S'):
    # 默认返回当前格式化好的时间
    # 传入时间戳的话，把时间戳转换成格式化好的时间，返回
    if timestamp:
        time_tuple = time.localtime(timestamp)
        res = time.strftime(format, time_tuple)
    else:
        res = time.strftime(format)  # 默认读取当前时间
    return res

def request_data_now():
    '''
    按照现在的时刻获取OHLC数据
    :return: Dataframe with columns: Open High Low Close Volume index: 转换好的时间
    '''
    BASE_URL = "https://api.binance.com"
    # url = BASE_URL + "/api/v1/klines?symbol=BTCUSDT&interval=1m&limit=1000" # 会不一样
    url = BASE_URL + "/api/v1/klines?symbol=ETHUSDT&interval=15m&limit=1000"
    resp = requests.get(url)
    resp = resp.json()
    df = pd.DataFrame(resp)
    df = df.drop(columns=[6, 7, 8, 9, 10, 11])
    df.columns = ["opentime", "Open", "High", "Low", "Close", "Volume"]
    df["Date"] = (df["opentime"] // 1000).map(timestamp_to_fomat)
    df = df.set_index(df["Date"])
    df = df.drop(["opentime"], axis=1)
    df['Open'] = pd.to_numeric(df['Open'])
    df['High'] = pd.to_numeric(df['High'])
    df['Low'] = pd.to_numeric(df['Low'])
    df['Close'] = pd.to_numeric(df['Close'])
    df['Volume'] = pd.to_numeric(df['Volume'])
    return df

def request_data_15min(start_time_list,end_time_list,symbol='ETHUSDT'):
    url = 'https://api.binance.com/api/v3/klines'
    interval = '15m'
    path = '%s_%d%d%d_%d%d%d_%s.csv' % (symbol, start_time_list[0], start_time_list[1], start_time_list[2],
                                        end_time_list[0], end_time_list[1], end_time_list[2], interval)
    if os.path.exists(path):
        print('csv file exists')
        print('loading csv file')
        df = pd.read_csv(path)
        df.set_index('Date',drop=True,inplace=True)
        return df
    else:
        # 创建空的dataframe
        df = pd.DataFrame(columns=
                          ['datetime', 'Open', 'High', 'Low',
                           'Close', 'Volume', 'close_time', 'qav',
                           'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore']
                          )
        real_start_time = int(dt.datetime(start_time_list[0], start_time_list[1], start_time_list[2]).timestamp() * 1000)
        real_end_time = end_time = int(dt.datetime(end_time_list[0], end_time_list[1], end_time_list[2]).timestamp() * 1000)
        i = real_start_time
        j = i + 360000000
        print('start gathering data...')
        while j <= real_end_time:
            start = str(i)
            end = str(j)
            par = {'symbol': symbol, 'interval': interval, 'startTime': start, 'endTime': end}
            data = pd.DataFrame(json.loads(requests.get(url, params=par).text))
            data.columns = ['datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'close_time', 'qav', 'num_trades',
                            'taker_base_vol', 'taker_quote_vol', 'ignore']
            # 计算datetime index：从时间戳到时间
            data.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in data.datetime]
            data = data.astype(float)
            df = df.append(data)
            i = j
            j = i + 360000000
        df.drop_duplicates(inplace=True)
        df.index.name = 'Date'
        df = df.drop(columns=['datetime','close_time','qav','num_trades','taker_base_vol','taker_quote_vol','ignore'])
        print('data gathering finished.')
        df.to_csv(path)
        print('data saved to csv file')
        return df