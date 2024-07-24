import numpy as np
import pandas as pd
from signal_definition import *
from aws_keys_retrieval import load_secrets
from binance.client import Client

def backtest(data):
    data['returns'] = data['close'].pct_change()
    data['strategy_returns'] = np.where(data['transformed_signal']== -1, 0, data['returns'].shift(-1))
    return data.dropna()

def calculate_metrics(data):
    total_return = (data['strategy_returns'] + 1).cumprod().iloc[-1] - 1
    sharpe_ratio = data['strategy_returns'].mean() / data['strategy_returns'].std() * np.sqrt(252)
    max_drawdown = (data['strategy_returns'] + 1).cumprod().div((data['strategy_returns'] + 1).cumprod().cummax()).min() - 1
    return {'Total Return': total_return, 'Sharpe Ratio': sharpe_ratio, 'Max Drawdown': max_drawdown}


load_secrets()

client = Client(os.environ.get("BINANCE_API_KEY"), os.environ.get("BINANCE_API_SECRET"))
account_info = client.get_account()
symbol = 'SOLUSDT'
interval = Client.KLINE_INTERVAL_1HOUR
start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d') 

data = get_historical_data(symbol, interval, start_date)
no_light_data = pd.read_csv('trading bot/SOLUSD2024H.csv')
no_light_data['date'] = no_light_data['timestamp'].astype('datetime64[s]')
#data = no_light_data.set_index('date')
print(data)
#data = data[data.index < '2024-01-17']
#data = data['2024-01-15' < data.index]

data = derivative_signal(data)
data = transform_signals(data)
print(data)
data = backtest(data)
metrics = calculate_metrics(data)
print(data)
print(metrics)
