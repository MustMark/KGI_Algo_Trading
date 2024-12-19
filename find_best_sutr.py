import pandas as pd
from datetime import *
import csv

ans = []
def check_winrate(dfs):
    count_win = 0
    count_lose = 0
    result = 0
    last_Sig = "sell"
    price = dfs["Close"]
    eq = 0
    for index, row in dfs.iterrows():
        if row["Buy_Signal"]:
            last_Sig = "buy"
            price = row["Close"]
            eq = 1_000_000 // price
        elif row["Sell_Signal"]:
            if last_Sig == "buy":
                result = result + eq * (row["Close"] - price)
                if row["Close"] > price:
                    count_win += 1
                else:
                    count_lose += 1
            last_Sig = "sell"
    if count_win + count_lose == 0:
        winrate = 0
    else:
        winrate = 100 * count_win / (count_win + count_lose)
    # print(f"{count_win}\t{count_lose}\t{winrate:.2f}\t{result:.2f}")
    return count_win, count_lose, result


df = pd.read_csv(
    "~/Desktop/Daily_Ticks17.csv"
)
# just for sell and buy
df = df[(df["Flag"] == "Sell") | (df["Flag"] == "Buy")]
# convert to datetime
df["TradeDateTime"] = pd.to_datetime(df["TradeDateTime"])

# Clean Data
unique_sharecodes = list(df["ShareCode"].unique())
eq_df = {}
for uniq in unique_sharecodes:
    eq_df[uniq] = df[df["ShareCode"] == uniq]

    eq_df[uniq] = (
        eq_df[uniq]
        .resample("5min", on="TradeDateTime")
        .agg(
            {
                "LastPrice": ["first", "max", "min", "last"],  # Open, High, Low, Close
                "Volume": "sum",
                "Value": "sum",
            }
        )
        .dropna()
    )
    eq_df[uniq].columns = ["Open", "High", "Low", "Close", "Volume", "Value"]
    eq_df[uniq].reset_index(inplace=True)


for EMA_FAST in range(2,10):
    for EMA_SLOW in range(10,25):
        for SIGNAL_PERIOD in range(2,10):
            print(EMA_FAST, EMA_SLOW, SIGNAL_PERIOD)
            for uniq in unique_sharecodes:
                eq_df[uniq]['EMA_Fast'] = eq_df[uniq]['Close'].ewm(span=EMA_FAST, adjust=False).mean()
                eq_df[uniq]['EMA_Slow'] = eq_df[uniq]['Close'].ewm(span=EMA_SLOW, adjust=False).mean()
                eq_df[uniq]['MACD_Line'] = eq_df[uniq]['EMA_Fast'] - eq_df[uniq]['EMA_Slow']
                eq_df[uniq]['Signal_Line'] = eq_df[uniq]['MACD_Line'].ewm(span=SIGNAL_PERIOD, adjust=False).mean()
                eq_df[uniq]['Histogram'] = eq_df[uniq]['MACD_Line'] - eq_df[uniq]['Signal_Line']

                # Generate Buy/Sell Signals
                eq_df[uniq]['Buy_Signal'] = (eq_df[uniq]['Histogram'] < 0) & (eq_df[uniq]['Histogram'].shift(1) >= 0)
                eq_df[uniq]['Sell_Signal'] = (eq_df[uniq]['Histogram'] > 0) & (eq_df[uniq]['Histogram'].shift(1) <= 0)
                
            result = 0
            count_win = 0
            count_lose = 0
            for uniq in unique_sharecodes:
                # print(uniq, end="\t")
                w,l,r = check_winrate(eq_df[uniq])
                count_win += w
                count_lose += l
                result += r
            # print(f"result: {result}")
            # print(f"count_win: {count_win}")
            # print(f"count_lose: {count_lose}")
            wr = 0 if (count_win+count_lose)==0 else 100*count_win/(count_win+count_lose)
            
            ans.append({
                "fast": EMA_FAST,
                "slow": EMA_SLOW,
                "signal": SIGNAL_PERIOD,
                "win": count_win,
                "lose": count_lose,
                "result": result,
                "winrate": wr
            })

ans = sorted(ans, key=lambda t: t["winrate"], reverse=True)
with open('sutr_winrate2.csv', 'w', newline='') as csvfile:
    fieldnames = ['fast', 'slow', 'signal', 'win', 'lose', 'result', 'winrate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ans)

ans = sorted(ans, key=lambda t: t["result"], reverse=True)
with open('sutr_result2.csv', 'w', newline='') as csvfile:
    fieldnames = ['fast', 'slow', 'signal', 'win', 'lose', 'result', 'winrate']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(ans)