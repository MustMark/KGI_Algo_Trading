import pandas as pd
import numpy as np
import os
# from datetime import *
from datetime import datetime, timedelta, date, time

runtime_start = datetime.now()

################################################################ TEAM ################################################################

team_name = '041_BID' 

################################################################ FILE ################################################################
output_dir = os.path.expanduser("~/Desktop/competition_api")

if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created main directory: {output_dir}")

def load_previous(file_type, teamName):
    output_dir = os.path.expanduser("~/Desktop/competition_api")
    folder_path = os.path.join(output_dir, "Previous", file_type)
    file_path = os.path.join(folder_path, f"{teamName}_{file_type}.csv")
    
    if os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path)
            print(f"Loaded '{file_type}' data for team {teamName}.")
            return data
        except Exception as e:
            print(f"Error loading file: {e}")
            return None
    else:
        print(f"File not found: {file_path}")
        return None

def save_output(data, file_type, teamName):
    folder_path = output_dir + f"/Result/{file_type}"
    file_path = folder_path + f"/{teamName}_{file_type}.csv"

    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)
        print(f"Directory created: '{folder_path}'")

    # Save CSV
    data.to_csv(file_path, index=False)
    print(f"{file_type} saved at {file_path}")

################################################################ FILE FUNCTION ################################################################

# dictionary สำหรับ portfolio
portfolio_data = {
    'Table Name': [],
    'File Name': [],
    'Stock name': [],
    'Start Vol': [],
    'Actual Vol': [],
    'Avg Cost': [],
    'Market Price': [],
    'Amount Cost': [],
    'Market Value': [],
    'Unrealized P/L': [],
    '% Unrealized P/L': [],
    'Realized P/L': []
}

# dictionary สำหรับ statement
statement_data = {
    'Table Name': [],
    'File Name': [],
    'Stock Name': [],
    'Date': [],
    'Time': [],
    'Side': [],
    'Volume': [],
    'Actual Vol': [],
    'Price': [],
    'Amount Cost': [],
    'End Line Available': [],
    'Portfolio value' : [],
    'NAV' : []
}

# dictionary สำหรับ summary
summary_data = {
    'Table Name': [],
    'File Name': [],
    'trading_day': [],  
    'NAV': [],
    'Portfolio value': [],
    'End Line available': [],
    'Start Line available' : [],
    'Number of wins': [], 
    'Number of matched trades': [],
    'Number of transactions:': [],
    'Net Amount': [],
    'Unrealized P/L': [],
    '% Unrealized P/L':[],
    'Realized P/L': [],
    'Maximum value': [],
    'Minimum value': [],
    'Win rate': [],
    'Calmar Ratio': [],
    'Relative Drawdown': [],
    'Maximum Drawdown': [],
    '%Return': []
}

def add_stock_to_portfolio(stock_name, start_vol, actual_vol, avg_cost, realized_PL):

    stock_data = df[df['ShareCode'] == stock_name]
    if stock_data.empty:
        print(f"No data found for stock: {stock_name}")
        return False

    market_price = stock_data.iloc[-1]['LastPrice'] if not stock_data.empty else 0

    amount_cost = actual_vol * avg_cost
    market_value = actual_vol * market_price
    unrealized_PL = market_value - amount_cost
    percentage_unrealized_PL = (unrealized_PL / amount_cost * 100) if amount_cost != 0 else 0

    portfolio_data['Table Name'].append('Portfolio_file')
    portfolio_data['File Name'].append(team_name)
    portfolio_data['Stock name'].append(stock_name)
    portfolio_data['Start Vol'].append(start_vol)
    portfolio_data['Actual Vol'].append(actual_vol)
    portfolio_data['Avg Cost'].append(round(avg_cost, 4))
    portfolio_data['Market Price'].append(round(market_price, 4))
    portfolio_data['Amount Cost'].append(round(amount_cost, 4))
    portfolio_data['Market Value'].append(round(market_value, 4))
    portfolio_data['Unrealized P/L'].append(round(unrealized_PL, 4))
    portfolio_data['% Unrealized P/L'].append(round(percentage_unrealized_PL, 4))
    portfolio_data['Realized P/L'].append(round(realized_PL, 4))

    return True

def update_statement(stock_name, datetime ,side, volume, actual_vol,price, initial_balance, market_value):

    date = datetime.date()
    time = datetime.time()
    amount_cost = volume * price
    nav = initial_balance + market_value

    statement_data['Table Name'].append('Statement_file')
    statement_data['File Name'].append(team_name)
    statement_data['Stock Name'].append(stock_name)
    statement_data['Date'].append(date)
    statement_data['Time'].append(time)
    statement_data['Side'].append(side)
    statement_data['Volume'].append(volume)
    statement_data['Actual Vol'].append(actual_vol)
    statement_data['Price'].append(round(price, 4))
    statement_data['Amount Cost'].append(round(amount_cost, 4))
    statement_data['End Line Available'].append(round(initial_balance, 4))
    statement_data['Portfolio value'].append(round(market_value, 4))
    statement_data['NAV'].append(round(nav, 4))

################################################################ START ################################################################

# time_now = datetime.strptime("00:00:00", "%H:%M:%S").time()
trading_day = 0
start_portfolio = {} #สำหรับ วันที่ 2 เป็นต้นไป
portfolio = {}
transaction_q = []
count_sell = 0
count_win = 0
previous_transactions = 0
last_end_line_available = 0
initial_investment = 10000000 

# prepare dataframe
file_path = '~/Desktop/Daily_Ticks.csv' 
df = pd.read_csv(file_path)
df = df[(df['Flag'] == 'Sell') | (df['Flag'] == 'Buy') | (df['Flag'] == 'ATC')]
df['TradeDateTime'] = pd.to_datetime(df['TradeDateTime'])
df["TradeTime"] = df['TradeDateTime'].dt.time

unique_sharecodes = list(df['ShareCode'].unique())
itr = {uniq: 0 for uniq in unique_sharecodes}
money_per_turn = 500_000
time_now = datetime.combine(date.today(), time(10, 00))

timeframe = 1
MaFast_period = 1  # Fast moving average period
MaSlow_period = 17  # Slow moving average period
Signal_period = 6   # Signal line period

unique_df =  {}
for uniq in unique_sharecodes:
    unique_df[uniq] = df[df['ShareCode'] == uniq]

############################################################### Load file ################################################################ 
prev_portfolio_df = load_previous("portfolio", team_name)
prev_summary_df = load_previous("summary", team_name)

if prev_portfolio_df is not None:
    for index, row in prev_portfolio_df.iterrows():
        stock_name = row.iloc[2]
        volume = int(row.iloc[4])
        price = float(row.iloc[5]) 
        realized_PL = float(row.iloc[11]) 
        
        # เพิ่มข้อมูลลงใน portfolio
        start_portfolio[stock_name] = {
            'volume': volume
        }
        portfolio[stock_name] = {
            'volume': volume,
            'price': price,
            'realized_PL': realized_PL
        }

if prev_summary_df is not None:

    trading_day = prev_summary_df['trading_day'].iloc[0]
    count_win = prev_summary_df['Number of wins'].iloc[0]
    count_sell = prev_summary_df['Number of matched trades'].iloc[0]
    previous_transactions = prev_summary_df['Number of transactions:'].iloc[0]
    if 'End Line available' in prev_summary_df.columns:

        # ดึงค่าคอลัมน์ 'End Line available' ทั้งหมด   
        initial_balance_series = prev_summary_df['End Line available']
        
        # ตรวจสอบว่าคอลัมน์ไม่ว่างเปล่า
        if not initial_balance_series.empty:
            # เข้าถึงค่าแรกของคอลัมน์
            first_value = initial_balance_series.iloc[0]
            # ลบเครื่องหมายคั่นหลักพันและแปลงเป็น float
            try:
                initial_balance = float(str(first_value).replace(',', '').strip())
                Start_Line_available = initial_balance
                print("End Line available column loaded successfully.")
                print(f"Initial balance (first value): {initial_balance}")
            except ValueError:
                print(f"Error converting '{first_value}' to a float.")
                initial_balance = initial_investment  # ใช้ค่าตั้งต้นในกรณีเกิดข้อผิดพลาด
        else:
            print("'End Line available' column is empty.")
            initial_balance = initial_investment  # ใช้ค่าตั้งต้นหากคอลัมน์ว่าง
    else:
        print("'End Line available' column not found in the file.")
        initial_balance = initial_investment  # ใช้ค่าตั้งต้นหากไม่มีคอลัมน์
else:
    initial_balance = initial_investment  # ใช้ค่าตั้งต้นหากไฟล์ไม่โหลด
    Start_Line_available = initial_investment
    print(f"Initial balance = initial_investment: {initial_investment:,}")

################################################################ BUY - SELL FUNCTION ################################################################

def cal_market_value(match_time: datetime, typ):
    market_value = 0
    for stock_in_portfolio in portfolio:
        current_time = match_time.time()
        last_price = None

        filtered_df = unique_df[stock_in_portfolio]
        filtered_df = filtered_df[filtered_df['Flag'] == typ].copy()

        if not filtered_df.empty:
            # Filter rows with 'TradeTime' less than or equal to current_time
            valid_rows = filtered_df[filtered_df['TradeTime'] <= current_time]
            
            if not valid_rows.empty:
                closest_row = valid_rows.iloc[-1]
                last_price = closest_row['LastPrice']
        
        # หากพบราคา (last_price) จะคำนวณมูลค่าตลาด
        if last_price is not None:
            market_value += portfolio[stock_in_portfolio]['volume'] * last_price
    return market_value

def filter_dataframe(stock_name, price, transaction_type):

    global time_now
    time_least = (time_now + timedelta(minutes=timeframe)).time()
    time_max = (time_now + timedelta(minutes=2*timeframe)).time()
    
    filtered_df = unique_df[stock_name]
    filtered_df = filtered_df[(filtered_df['Flag'] == transaction_type) & (filtered_df['TradeTime'] >= time_least) & (filtered_df['TradeTime'] < time_max)]

    # กรองข้อมูลที่มี TradeTime มากกว่า time_now_plus_5min
    # filtered_df = filtered_df[(filtered_df['TradeTime'] >= time_least) & (filtered_df['TradeTime'] < time_max)]

    if transaction_type == "Sell":
        filtered_df = filtered_df[filtered_df['LastPrice'] <= price]
    else:
        filtered_df = filtered_df[filtered_df['LastPrice'] >= price]
    return filtered_df

# ฟังก์ชันซื้อหุ้น
def buy_stock(stock_name, volume, price, initial_balance, match_time: datetime):
    
    if initial_balance < volume * price:
        # print("Not enough balance to buy stock.")
        return initial_balance
    
    initial_balance -= volume * price
    if stock_name in portfolio:
        portfolio[stock_name]['price'] = ((portfolio[stock_name]['volume'] * portfolio[stock_name]['price']) + (volume * price)) / (portfolio[stock_name]['volume'] + volume)
        portfolio[stock_name]['volume'] += volume
    else:
        portfolio[stock_name] = {
            'volume': volume,
            'price': price,
            'realized_PL' : 0
        }

    market_value = 0

    market_value = cal_market_value(match_time, "Sell")

    update_statement(stock_name, match_time, "Buy", volume, portfolio[stock_name]['volume'], price, initial_balance, market_value)
    # print(f"Bought {volume} shares of {stock_name} at {price} THB.")
    # print(f"Remaining balance: {initial_balance} THB.")
    return initial_balance
        # pass

# ฟังก์ชันขายหุ้น
def sell_stock(stock_name, volume, price, initial_balance, match_time: datetime):
    # ตรวจสอบว่ามีหุ้นในพอร์ตหรือไม่ และจำนวนพอขาย
    if stock_name in portfolio:
        global count_sell
        global count_win

        money_received = volume * price
        
        # เพิ่มเงินเข้าไปในยอดคงเหลือ
        initial_balance += money_received
        
        count_sell += 1     

        if price > portfolio[stock_name]['price']:
            count_win += 1

        # อัพเดตข้อมูลในพอร์ตชั่วคราว (ลดจำนวนหุ้นในพอร์ต)
        new_actual_volume = portfolio[stock_name]['volume'] - volume
        if new_actual_volume == 0:
            del portfolio[stock_name]  # ลบหุ้นออกจากพอร์ตถ้าขายหมด
        else:
            portfolio[stock_name]['volume'] = new_actual_volume
            portfolio[stock_name]['realized_PL'] += money_received - (portfolio[stock_name]['price'] * volume)
        
        market_value = cal_market_value(match_time, "Buy")
        
        if stock_name not in portfolio:
            actual_vol = 0
        else:
            actual_vol = portfolio[stock_name]['volume']
        update_statement(stock_name, match_time, "Sell", volume, actual_vol, price, initial_balance, market_value)
        # print(f"Sold {volume} shares of {stock_name} at {price} THB.")
        # print(f"New balance: {initial_balance} THB.")
    else:
        # print(f"{stock_name} not in portfolio.")
        pass
    return initial_balance

# ฟังก์ชันสร้างการซื้อหุ้น
def create_buy_stock(stock_name, volume, price):
    # ซื้อไม่ได้ถ้าเงินน้อย
    global initial_balance
    if initial_balance < volume * price:
        # print("Not enough balance to buy stock.")
        return 
    
    # ตรวจสอบการทำธุรกรรมก่อนซื้อ
    filtered_df = filter_dataframe(stock_name, price, "Sell")
    if not filtered_df.empty:
        canbuy_vol = 0
        total_cost = 0
        for idx, row in filtered_df.iterrows():
            if canbuy_vol + row["Volume"] <= volume:
                canbuy_vol += row["Volume"]
                total_cost += (row["Volume"]*row["LastPrice"])
                transaction_q.append({"type": "Buy", "series": row, "vol": row["Volume"]})
            else:
                exist_vol = 100*((volume - canbuy_vol)//100)
                if exist_vol >= 100:
                    canbuy_vol = volume
                    total_cost = (exist_vol*row["LastPrice"])
                    transaction_q.append({"type": "Buy", "series": row, "vol": exist_vol})
                break
    else:
        # print(f"Buy {stock_name} failed. Invalid transaction.")
        pass

# ฟังก์ชันสร้างการขายหุ้น
def create_sell_stock(stock_name, price):
    # ตรวจสอบการทำธุรกรรมก่อนซื้อ
    if stock_name in portfolio:
        filtered_df = filter_dataframe(stock_name, price, "Buy")
        if not filtered_df.empty:
            volume = portfolio[stock_name]['volume']
            cansell_vol = 0
            total_cost = 0
            for idx, row in filtered_df.iterrows():
                if cansell_vol + row["Volume"] <= volume:
                    cansell_vol += row["Volume"]
                    total_cost += (row["Volume"]*row["LastPrice"])
                    transaction_q.append({"type": "Sell", "series": row, "vol": row["Volume"]})
                else:
                    exist_vol = volume - cansell_vol
                    if exist_vol >= 100:
                        cansell_vol = volume
                        total_cost = (exist_vol*row["LastPrice"])
                        transaction_q.append({"type": "Sell", "series": row, "vol": exist_vol})
                    break
        else:
            # print(f"Buy {stock_name} failed. Invalid transaction.")
            pass
    else:
        # print(f"{stock_name} not in portfolio.")
        pass

# ฟังชันก์รันคิวซื้อขาย
def running_buy_sell(transaction_q, initial_balance):
    transaction_q = sorted(transaction_q, key=lambda t: t["series"]["TradeDateTime"])
    while transaction_q:
        top = transaction_q.pop(0)
        series = top["series"]
        if top["type"] == "Sell":
            # sell_stock(stock_name, volume, price, initial_balance, match_time: datetime)
            initial_balance = sell_stock(series["ShareCode"], top["vol"], series["LastPrice"], initial_balance, series["TradeDateTime"])
        elif top["type"] == "Buy":
            initial_balance = buy_stock(series["ShareCode"], top["vol"], series["LastPrice"], initial_balance, series["TradeDateTime"])

    return initial_balance

################################################################ BUY - SELL ################################################################

# TEST CASE
# Clean Data and Generate Buy Sell Signal

def calculate_atr(df, period=3):
    df['H-L'] = df['High'] - df['Low']
    df['H-C'] = abs(df['High'] - df['Close'].shift(1))
    df['L-C'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['H-L', 'H-C', 'L-C']].max(axis=1)
    df['ATR'] = df['TR'].rolling(window=period).mean()
    return df

eq_df = {}
for uniq in unique_sharecodes:
    eq_df[uniq] = unique_df[uniq].resample(f'{timeframe}min', on='TradeDateTime').agg({
        'LastPrice': ['first', 'max', 'min', 'last'],  # Open, High, Low, Close
        'Volume': 'sum',
        'Value': 'sum'
    }).dropna()
    eq_df[uniq].columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Value']
    eq_df[uniq].reset_index(inplace=True)

    smaFast = eq_df[uniq]['Close'].rolling(window=MaFast_period).mean()
    smaSlow = eq_df[uniq]['Close'].rolling(window=MaSlow_period).mean()

    buffer1 = smaFast - smaSlow
    buffer2 = buffer1.rolling(window=Signal_period).mean()

    eq_df[uniq]['Buy_Signal'] = (buffer1 < buffer2) & (buffer1.shift(1) >= buffer2.shift(1))
    eq_df[uniq]['Sell_Signal'] = (buffer1 > buffer2) & (buffer1.shift(1) <= buffer2.shift(1))
    
    eq_df[uniq] = calculate_atr(eq_df[uniq])

# ตั้ง Stop Loss และ Take Profit ตาม ATR
atr_multiplier = 1.1

# buy sell from signal
is_finished = True
while True:
    for uniq in unique_sharecodes:
        if itr[uniq] < len(eq_df[uniq]):
            is_finished = False
            series = eq_df[uniq].iloc[itr[uniq]]
            trade_dt = datetime.time(series["TradeDateTime"])

            if trade_dt == time_now.time():
                
                price = series['Close']

                buy_price = price
                # ตั้ง Stop Loss และ Take Profit

                stop_loss_price = buy_price - (atr_multiplier * eq_df[uniq].iloc[-1]['ATR'])
                take_profit_price = buy_price + (atr_multiplier * eq_df[uniq].iloc[-1]['ATR'])
                # stop_loss_price = buy_price * (1 - stop_loss_percentage)
                # take_profit_price = buy_price * (1 + take_profit_percentage)
                # ตรวจสอบการทำกำไรหรือขาดทุน
                if uniq in portfolio:
                    if portfolio[uniq]['price'] >= take_profit_price:
                        # ทำการขายเมื่อได้กำไร
                        create_sell_stock(uniq, price)
                    elif portfolio[uniq]['price'] <= stop_loss_price:
                        # ขายเมื่อถึง Stop Loss
                        create_sell_stock(uniq, price)
                    else:
                        if series["Buy_Signal"] == True and time_now.time() < time(16, 15):
                        # ถ้ามีสัญญาณซื้อ และเวลาอยู่ภายในช่วงที่อนุญาต
                            if initial_balance >= money_per_turn:
                                vol = (money_per_turn * 100) // (price * 100)  # ใช้หุ้น 100 หุ้น
                            else:
                                vol = (initial_balance * 100) // (price * 100)  # ใช้หุ้น 100 หุ้น

                            if vol >= 100:
                                create_buy_stock(uniq, vol, price)

                        elif series["Sell_Signal"] == True:
                            # ถ้ามีสัญญาณขาย
                            create_sell_stock(uniq, price)
                else:
                    if series["Buy_Signal"] == True and time_now.time() < time(16, 15):
                        # ถ้ามีสัญญาณซื้อ และเวลาอยู่ภายในช่วงที่อนุญาต
                        if initial_balance >= money_per_turn:
                            vol = (money_per_turn * 100) // (price * 100)  # ใช้หุ้น 100 หุ้น
                        else:
                            vol = (initial_balance * 100) // (price * 100)  # ใช้หุ้น 100 หุ้น

                        if vol >= 100:
                            create_buy_stock(uniq, vol, price)

                    elif series["Sell_Signal"] == True:
                        # ถ้ามีสัญญาณขาย
                        create_sell_stock(uniq, price)

            if trade_dt <= time_now.time():
                itr[uniq] += 1

    if is_finished:
        break

    if time_now.time() == time(12, 30):
        time_now += timedelta(hours=1)

    initial_balance = running_buy_sell(transaction_q, initial_balance)
    transaction_q = []
    is_finished = True
    print(f"Time : {time_now.time()}, Win_rate : {round((count_win * 100) / count_sell, 4) if count_sell != 0 else 0}")
    time_now += timedelta(minutes=timeframe)

################################################## End ##############################################################################

for stock_name in portfolio:

    actual_vol = 0 
    total_volume = portfolio[stock_name]['volume']
    total_price = portfolio[stock_name]['price']
    total_realized_PL = portfolio[stock_name]['realized_PL']

    if stock_name in start_portfolio:
        actual_vol = start_portfolio[stock_name]['volume']

    add_stock_to_portfolio(stock_name, actual_vol, total_volume, total_price, total_realized_PL)

portfolio_df = pd.DataFrame(portfolio_data)
statement_df = pd.DataFrame(statement_data)

try:
    last_end_line_available = statement_df['End Line Available'].iloc[-1]
except (IndexError, KeyError, AttributeError) as e:
    last_end_line_available = initial_balance

summary_data = {
    'Table Name': ['Sum_file'],
    'File Name': [team_name],
    'trading_day': [trading_day + 1],  
    'NAV': [round(portfolio_df['Market Value'].sum() + last_end_line_available, 4)],
    'Portfolio value': [round(portfolio_df['Market Value'].sum(), 4)],
    'End Line available': [round(last_end_line_available, 4)],  # Use the correct End Line Available
    'Start Line available': [round(Start_Line_available, 4)],
    'Number of wins': [count_win], 
    'Number of matched trades': [count_sell], #นับ sell เพราะ เทรดbuy sellด้วย volume เท่ากัน
    'Number of transactions:': [previous_transactions + len(statement_df)],
    'Net Amount': [round(statement_df['Amount Cost'].sum(), 4)],
    'Unrealized P/L': [round(portfolio_df['Unrealized P/L'].sum(), 4)],
    '% Unrealized P/L': [round((portfolio_df['Unrealized P/L'].sum() / initial_investment * 100) if initial_investment else 0, 4)],
    'Realized P/L': [round(portfolio_df['Realized P/L'].sum(), 4)],
    'Maximum value': [round(statement_df['End Line Available'].max(), 4)],
    'Minimum value': [round(statement_df['End Line Available'].min(), 4)],
    'Win rate' : [round((count_win * 100) / count_sell, 4) if count_sell != 0 else 0],
    'Calmar Ratio': [round(((portfolio_df['Market Value'].sum() + last_end_line_available - initial_investment) / initial_investment * 100) / \
                    ((portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000), 4)],
    'Relative Drawdown': [round((portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000 / statement_df['End Line Available'].max() * 100, 4)],
    'Maximum Drawdown': [round((statement_df['End Line Available'].max() - statement_df['End Line Available'].min()) / statement_df['End Line Available'].max(), 4)],
    '%Return': [round((portfolio_df['Market Value'].sum() + last_end_line_available - initial_investment) / initial_investment * 100, 4)]
}

summary_df = pd.DataFrame(summary_data)
print()
print(f"[Day {summary_data['trading_day'][0]}] %Return : {summary_data['%Return'][0]}, Win_rate : {summary_data['Win rate'][0]}")

################################################## Save ##############################################################################

print()
save_output(portfolio_df, "portfolio", team_name)
save_output(statement_df, "statement", team_name)
save_output(summary_df, "summary", team_name)

print()
runtime_end = datetime.now()
print(f"Run_time : {(runtime_end - runtime_start).total_seconds():.4f} seconds")