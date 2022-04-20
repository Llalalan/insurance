import pandas as pd
import numpy as np

def cal_portfolio(df, initial_cash,macd, signal):
    price_data = df.iloc[180:]
    porfolio = pd.DataFrame(index=macd.index,
                            columns=['Cash', 'ETH', 'ETH_Price', 'ETH_Value', 'Total','ETH_IN','ETH_OUT'])
    porfolio['Cash'][0] = initial_cash
    porfolio['ETH'][0] = 0
    porfolio['ETH_Price'][0] = price_data['Close'][0]
    # minima做多，maxima卖出：eth加一，cash减
    # maxima做空，minima买入：eth减一，cash加
    for i in range(1, len(macd)):
        if signal[i] == 'not signal':
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH_IN'][i] = porfolio['ETH_IN'][i - 1]
            porfolio['ETH_OUT'][i] = porfolio['ETH_OUT'][i - 1]
        elif signal[i] == 'minima':
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH_IN'][i] = porfolio['ETH_Price'][i]
            porfolio['ETH_OUT'][i] = porfolio['ETH_OUT'][i - 1]
            # 起始,做多
            if porfolio['ETH'][i - 1] == 0:
                quantity_unround = porfolio['Cash'][i - 1] / porfolio['ETH_Price'][i]
                quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
                quantity = float(quantity_str)
                porfolio['ETH'][i] = quantity
                porfolio['Cash'][i] = porfolio['Cash'][i - 1] - porfolio['ETH_Price'][i] * quantity
            # 开始后低点平做空仓，并且买入更多
            else:
                # 平仓
                porfolio['ETH'][i] = 0
                porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH'][i - 1] * porfolio['ETH_Price'][i]
                quantity_unround = porfolio['Cash'][i] / porfolio['ETH_Price'][i]
                quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
                quantity = float(quantity_str)
                porfolio['ETH'][i] = quantity
                porfolio['Cash'][i] = porfolio['Cash'][i] - porfolio['ETH_Price'][i] * quantity
        elif signal[i] == 'maxima':
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH_OUT'][i] = porfolio['ETH_Price'][i]
            porfolio['ETH_IN'][i] = porfolio['ETH_IN'][i - 1]
            # 起始
            if porfolio['ETH'][i - 1] == 0:
                quantity_unround = porfolio['Cash'][i - 1] / porfolio['ETH_Price'][i]
                quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
                quantity = float(quantity_str)
                porfolio['ETH'][i] = -quantity
                porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH_Price'][i] * quantity
            # 高点平做多仓，并且做空
            else:
                porfolio['ETH'][i] = 0
                porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH'][i - 1] * porfolio['ETH_Price'][i]
                quantity_unround = porfolio['Cash'][i] / porfolio['ETH_Price'][i]
                quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
                quantity = float(quantity_str)
                porfolio['ETH'][i] = -quantity
                porfolio['Cash'][i] = porfolio['Cash'][i] + porfolio['ETH_Price'][i] * quantity
        else:
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH_IN'][i] = porfolio['ETH_IN'][i - 1]
            porfolio['ETH_OUT'][i] = porfolio['ETH_OUT'][i - 1]

    porfolio['ETH_Value'] = porfolio['ETH_Price'] * porfolio['ETH']
    porfolio['Total'] = porfolio['Cash'] + porfolio['ETH_Value']
    return porfolio

def cal_portfolio_short(df,initial_cash,macd,signal):
    price_data = df.iloc[180:]
    porfolio = pd.DataFrame(index=macd.index,
                            columns=['Cash', 'ETH', 'ETH_Price', 'ETH_Value', 'Total'])
    porfolio['Cash'][0] = initial_cash
    porfolio['ETH'][0] = 0
    porfolio['ETH_Price'][0] = price_data['Close'][0]
    for i in range(1, len(macd)):
        if signal[i] == 'not signal':
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
        elif signal[i] == 'maxima':
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            quantity_unround = porfolio['Cash'][i - 1] / porfolio['ETH_Price'][i]
            quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
            quantity = float(quantity_str)
            porfolio['ETH'][i] = -quantity
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH_Price'][i] * quantity
        elif (signal[i] == 'minima') and (porfolio['ETH'][i - 1] < 0):
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH'][i] = 0
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] - porfolio['ETH_Price'][i] * quantity
        else:
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
    porfolio['ETH_Value'] = porfolio['ETH_Price'] * porfolio['ETH']
    porfolio['Total'] = porfolio['Cash'] + porfolio['ETH_Value']
    return porfolio


def cal_portfolio_long(df,initial_cash,macd,signal):
    price_data = df.iloc[180:]
    porfolio = pd.DataFrame(index=macd.index,
                            columns=['Cash', 'ETH', 'ETH_Price', 'ETH_Value', 'Total'])
    porfolio['Cash'][0] = initial_cash
    porfolio['ETH'][0] = 0
    porfolio['ETH_Price'][0] = price_data['Close'][0]
    for i in range(1, len(macd)):
        if signal[i] == 'not signal':
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
        elif (signal[i] == 'minima'):
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            quantity_unround = porfolio['Cash'][i - 1] / porfolio['ETH_Price'][i]
            quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
            quantity = float(quantity_str)
            porfolio['ETH'][i] = quantity
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] - porfolio['ETH_Price'][i] * quantity
        elif signal[i] == 'maxima' and (porfolio['ETH'][i - 1] > 0):
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH'][i] = 0
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH_Price'][i] * quantity
        else:
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
    porfolio['ETH_Value'] = porfolio['ETH_Price'] * porfolio['ETH']
    porfolio['Total'] = porfolio['Cash'] + porfolio['ETH_Value']
    return porfolio


def cal_portfolio_long(df,initial_cash,macd,signal):
    price_data = df.iloc[180:]
    porfolio = pd.DataFrame(index=macd.index,
                            columns=['Cash', 'ETH', 'ETH_Price', 'ETH_Value', 'Total'])
    porfolio['Cash'][0] = initial_cash
    porfolio['ETH'][0] = 0
    porfolio['ETH_Price'][0] = price_data['Close'][0]
    for i in range(1, len(macd)):
        if signal[i] == 'not signal':
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
        elif (signal[i] == 'minima'):
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            quantity_unround = porfolio['Cash'][i - 1] / porfolio['ETH_Price'][i]
            quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
            quantity = float(quantity_str)
            porfolio['ETH'][i] = quantity
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] - porfolio['ETH_Price'][i] * quantity
        elif signal[i] == 'maxima' and (porfolio['ETH'][i - 1] > 0):
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH'][i] = 0
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH_Price'][i] * quantity
        else:
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
    porfolio['ETH_Value'] = porfolio['ETH_Price'] * porfolio['ETH']
    porfolio['Total'] = porfolio['Cash'] + porfolio['ETH_Value']
    return porfolio

def cal_portfolio_long_with_insurance(df,initial_cash,macd,signal,insurance_times=100,insurance_ratio=0.015):
    price_data = df.iloc[180:]
    porfolio = pd.DataFrame(index=macd.index,
                            columns=['Cash', 'ETH', 'ETH_Price', 'ETH_Value', 'Insurance','Insurance_qty','Total'])
    porfolio['Cash'][0] = initial_cash
    porfolio['ETH'][0] = 0
    porfolio['ETH_Price'][0] = price_data['Close'][0]
    porfolio['Insurance'][0] = 0
    porfolio['Insurance_qty'][0] = 0
    for i in range(1, len(macd)):
        if signal[i] == 'not signal':
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['Insurance_qty'][i] = porfolio['Insurance_qty'][i-1]
            if porfolio['Insurance_qty'][i] != 0:
                porfolio['Insurance'][i] = porfolio['Insurance'][i-1] - \
                    porfolio['Insurance_qty'][i-1] * (porfolio['ETH_Price'][i] - porfolio['ETH_Price'][i-1])
                if porfolio['Insurance'][i] <= 0:
                    porfolio['Insurance'][i] = 0
                    porfolio['Insurance_qty'][i] = 0
            else:
                porfolio['Insurance'][i] = porfolio['Insurance'][i-1]
        elif signal[i] == 'minima':
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['Insurance'][i] = porfolio['Cash'][i - 1]*insurance_ratio
            insurance_quantity_unround = porfolio['Insurance'][i]*insurance_times/porfolio['ETH_Price'][i]
            insurance_quantity_str = str(insurance_quantity_unround).split('.')[0] + '.' + str(insurance_quantity_unround).split('.')[1][:2]
            insurance_quantity = float(insurance_quantity_str)
            porfolio['Insurance_qty'][i] = insurance_quantity
            quantity_unround = porfolio['Cash'][i - 1]*(1-insurance_ratio)/ porfolio['ETH_Price'][i]
            quantity_str = str(quantity_unround).split('.')[0] + '.' + str(quantity_unround).split('.')[1][:2]
            quantity = float(quantity_str)
            porfolio['ETH'][i] = quantity
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] - porfolio['ETH_Price'][i] * quantity - porfolio['Insurance'][i]
        elif (signal[i] == 'maxima') and (porfolio['ETH'][i - 1] > 0):
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['ETH'][i] = 0
            porfolio['Insurance'][i] = porfolio['Insurance'][i - 1] - \
                                       porfolio['Insurance_qty'][i - 1] * (
                                                   porfolio['ETH_Price'][i] - porfolio['ETH_Price'][i - 1])
            porfolio['Cash'][i] = porfolio['Cash'][i - 1] + porfolio['ETH_Price'][i] * quantity + porfolio['Insurance'][i]
            porfolio['Insurance_qty'][i] = 0
            porfolio['Insurance'][i] = 0
        else:
            porfolio['Cash'][i] = porfolio['Cash'][i - 1]
            porfolio['ETH'][i] = porfolio['ETH'][i - 1]
            porfolio['ETH_Price'][i] = price_data['Close'][i]
            porfolio['Insurance_qty'][i] = porfolio['Insurance_qty'][i-1]
            if porfolio['Insurance_qty'][i] != 0:
                porfolio['Insurance'][i] = porfolio['Insurance'][i-1] - \
                    porfolio['Insurance_qty'][i-1] * (porfolio['ETH_Price'][i] - porfolio['ETH_Price'][i-1])
                if porfolio['Insurance'][i] <= 0:
                    porfolio['Insurance'][i] = 0
                    porfolio['Insurance_qty'][i] = 0
            else:
                porfolio['Insurance'][i] = porfolio['Insurance'][i-1]
    porfolio['ETH_Value'] = porfolio['ETH_Price'] * porfolio['ETH']
    porfolio['Total'] = porfolio['Cash'] + porfolio['ETH_Value'] + porfolio['Insurance']
    return porfolio