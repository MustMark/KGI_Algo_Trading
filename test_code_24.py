import pandas as pd
import numpy as np

# Load and process data
file_path = '~/Desktop/Daily_Ticks.csv'
df = pd.read_csv(file_path)
df = df[(df['Flag'] == 'Sell') | (df['Flag'] == 'Buy') | (df['Flag'] == 'ATC')]
df['TradeDateTime'] = pd.to_datetime(df['TradeDateTime'])
df['TradeTime'] = df['TradeDateTime'].dt.time

unique_sharecodes = list(df['ShareCode'].unique())
timeframe = 1
MaFast_period = 1  # Fast moving average period
MaSlow_period = 17  # Slow moving average period
Signal_period = 6   # Signal line period
money_per_turn = 200_000
initial_balance = 10_000_000
time_now = pd.Timestamp.combine(pd.Timestamp.today(), pd.Timestamp.min.time()).replace(hour=10)
portfolio = {}
transaction_q = []
count_sell = 0
count_win = 0

# Indicators calculation
def calculate_indicators(data):
    data['SMA_Fast'] = data['Close'].rolling(window=MaFast_period).mean()
    data['SMA_Slow'] = data['Close'].rolling(window=MaSlow_period).mean()
    data['Buffer1'] = data['SMA_Fast'] - data['SMA_Slow']
    data['Buffer2'] = data['Buffer1'].rolling(window=Signal_period).mean()
    data['RSI'] = calculate_rsi(data['Close'])
    data['Middle_Band'] = data['Close'].rolling(window=20).mean()
    data['Upper_Band'] = data['Middle_Band'] + 2 * data['Close'].rolling(window=20).std()
    data['Lower_Band'] = data['Middle_Band'] - 2 * data['Close'].rolling(window=20).std()
    return data

def calculate_rsi(close, window=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Generate buy and sell signals
def generate_signals(data):
    data['Buy_Signal'] = (
        (data['Buffer1'] < data['Buffer2']) &
        (data['Buffer1'].shift(1) >= data['Buffer2'].shift(1)) &
        ((data['RSI'] < 45) | (data['Close'] < data['Lower_Band']))
    )
    data['Sell_Signal'] = (
        (data['Buffer1'] > data['Buffer2']) &
        (data['Buffer1'].shift(1) <= data['Buffer2'].shift(1)) &
        ((data['RSI'] > 55) | (data['Close'] > data['Upper_Band']))
    )
    return data

def execute_trade(signals, initial_balance):
    global count_sell, count_win
    buy_price = None
    total_profit = 0

    for i in range(len(signals)):
        if signals['Buy_Signal'].iloc[i] and buy_price is None:
            buy_price = signals['Close'].iloc[i]
        elif signals['Sell_Signal'].iloc[i] and buy_price is not None:
            sell_price = signals['Close'].iloc[i]
            profit = sell_price - buy_price
            total_profit += profit
            count_sell += 1
            if profit > 0:
                count_win += 1
            buy_price = None

    return total_profit, initial_balance + total_profit

# Resample data and process each share code
results = {}
for uniq in unique_sharecodes:
    resampled = df[df['ShareCode'] == uniq].resample(f'{timeframe}min', on='TradeDateTime').agg({
        'LastPrice': ['first', 'max', 'min', 'last'],
        'Volume': 'sum',
        'Value': 'sum'
    }).dropna()
    resampled.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Value']
    resampled.reset_index(inplace=True)

    resampled = calculate_indicators(resampled)
    resampled = generate_signals(resampled)

    profit, final_balance = execute_trade(resampled, initial_balance)
    results[uniq] = {'Profit': profit, 'Final Balance': final_balance}

# Display results
for share, result in results.items():
    print(f"{share}: Profit = {result['Profit']:.2f}, Final Balance = {result['Final Balance']:.2f}")

print(f"Win rate: {count_win / count_sell * 100:.2f}%" if count_sell > 0 else "No trades executed.")