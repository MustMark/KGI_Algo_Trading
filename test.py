import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

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

    date, time = datetime.split()
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

time_now = datetime.strptime("00:00:00", "%H:%M:%S").time()
trading_day = 0
portfolio = {}
count_sell = 0
count_win = 0
last_end_line_available = 0
initial_investment = 10000000 

file_path = '~/Desktop/Daily_Ticks.csv' 
df = pd.read_csv(file_path)

# Load file
prev_portfolio_df = load_previous("portfolio", team_name)
prev_summary_df = load_previous("summary", team_name)

if prev_portfolio_df is not None:
    for index, row in prev_portfolio_df.iterrows():
        stock_name = row.iloc[2]
        volume = int(row.iloc[4])
        price = float(row.iloc[5]) 
        realized_PL = float(row.iloc[11]) 
        
        # เพิ่มข้อมูลลงใน portfolio
        portfolio[stock_name] = {
            'volume': volume,
            'price': price,
            'realized_PL': realized_PL
        }

if prev_summary_df is not None:

    trading_day = prev_summary_df['trading_day'].iloc[0]
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

def is_valid_transaction(stock_name, volume, price, transaction_type):

    global time_now

    # กรองข้อมูลที่ตรงกับ stock_name
    filtered_df = df[df['ShareCode'] == stock_name]
    
    # กรองประเภทธุรกรรม (Buy หรือ Sell)
    filtered_df = filtered_df[filtered_df['Flag'] == transaction_type]
    
    # ตรวจสอบว่ามีราคาและจำนวนที่ตรงกันหรือไม่
    filtered_df['TradeTime'] = pd.to_datetime(filtered_df['TradeDateTime']).dt.time

    # กรองข้อมูลที่เวลามากกว่าเวลาในการซื้อ
    filtered_df = filtered_df[filtered_df['TradeTime'] > time_now]

    match = filtered_df[(filtered_df['LastPrice'] == price) & (filtered_df['Volume'] == volume)]

    if not match.empty:
        # Return TradeDateTime ของแถวที่ตรงกับเงื่อนไข
        return match['TradeDateTime'].iloc[0]
    else:
        return None  # ถ้าไม่มีข้อมูลที่ตรงกันให้คืนค่า None

# ฟังก์ชันซื้อหุ้น
def buy_stock(stock_name, volume, price, initial_balance):
    # ตรวจสอบการทำธุรกรรมก่อนซื้อ
    match_time = is_valid_transaction(stock_name, volume, price, "Sell")
    if match_time:
        # ตรวจสอบยอดเงินคงเหลือ
        if initial_balance >= volume * price:
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

            global time_now

            time_now = datetime.strptime(match_time, "%Y-%m-%d %H:%M:%S").time()
            
            market_value = 0

            for stock_in_portfolio in portfolio:
                current_time = time_now
                last_price = None

                while last_price is None:
                    filtered_df = df[(df['ShareCode'] == stock_in_portfolio) & 
                                    (pd.to_datetime(df['TradeDateTime']).dt.time == current_time)]
                    
                    if not filtered_df.empty:
                        last_price = filtered_df.iloc[0]['LastPrice']
                    else:
                        # ลด current_time ลงทีละ 1 วินาที
                        current_time = (datetime.combine(datetime(1, 1, 1), current_time) - timedelta(seconds=1)).time()
                
                if last_price is not None:
                    market_value += portfolio[stock_in_portfolio]['volume'] * last_price

            update_statement(stock_name, match_time, "Buy", volume, portfolio[stock_name]['volume'], price, initial_balance, market_value)
            print(f"Bought {volume} shares of {stock_name} at {price} THB.")
            print(f"Remaining balance: {initial_balance} THB.")
        else:
            print("Not enough balance to buy stock.")
    else:
        print(f"Buy {stock_name} failed. Invalid transaction.")
    
    return initial_balance

# ฟังก์ชันขายหุ้น
def sell_stock(stock_name, volume, price, initial_balance):
    # ตรวจสอบว่ามีหุ้นในพอร์ตหรือไม่ และจำนวนพอขาย
    if stock_name in portfolio:
        actual_volume = portfolio[stock_name]['volume']
        
        if actual_volume >= volume:
            match_time = is_valid_transaction(stock_name, volume, price, "Buy")
            if match_time:
                # คำนวณเงินที่ได้จากการขาย
                money_received = volume * price
                
                # เพิ่มเงินเข้าไปในยอดคงเหลือ
                initial_balance += money_received
                
                # อัพเดตข้อมูลในพอร์ตชั่วคราว (ลดจำนวนหุ้นในพอร์ต)
                new_actual_volume = actual_volume - volume
                if new_actual_volume == 0:
                    del portfolio[stock_name]  # ลบหุ้นออกจากพอร์ตถ้าขายหมด
                else:
                    portfolio[stock_name]['volume'] = new_actual_volume
                    portfolio[stock_name]['realized_PL'] += money_received - (portfolio[stock_name]['price'] * volume)
            
                global time_now
                global count_sell
                global count_win
                
                time_now = datetime.strptime(match_time, "%Y-%m-%d %H:%M:%S").time()
        
                count_sell += 1     

                if money_received > 0:
                    count_win += 1
                
                market_value = 0

                for stock_in_portfolio in portfolio:
                    current_time = time_now
                    last_price = None

                    while last_price is None:
                        filtered_df = df[(df['ShareCode'] == stock_in_portfolio) & 
                                        (pd.to_datetime(df['TradeDateTime']).dt.time == current_time)]
                        
                        if not filtered_df.empty:
                            last_price = filtered_df.iloc[0]['LastPrice']
                        else:
                            # ลด current_time ลงทีละ 1 วินาที
                            current_time = (datetime.combine(datetime(1, 1, 1), current_time) - timedelta(seconds=1)).time()
                    
                    if last_price is not None:
                        market_value += portfolio[stock_in_portfolio]['volume'] * last_price

                update_statement(stock_name, match_time, "Sell", volume, portfolio[stock_name]['volume'], price, initial_balance, market_value)
                print(f"Sold {volume} shares of {stock_name} at {price} THB.")
                print(f"New balance: {initial_balance} THB.")
            else:
                print(f"Sell {stock_name} failed.")
        else:
            print("Not enough shares in portfolio to sell.")
    else:
        print(f"{stock_name} not in portfolio.")
    
    return initial_balance

################################################################ BUY - SELL ################################################################

# TEST CASE
initial_balance = buy_stock("ADVANC", 100, 295.0, initial_balance)
print(portfolio)
initial_balance = buy_stock("ADVANC", 2700, 294.0, initial_balance)
print(portfolio)
initial_balance = buy_stock("AOT", 100, 61.5, initial_balance)
print(portfolio)
initial_balance = buy_stock("EA", 100, 5.5, initial_balance)
print(portfolio)
initial_balance = sell_stock("ADVANC", 100, 289.0, initial_balance)
print(portfolio)

################################################################################################################################

for stock_name in portfolio:

    total_volume = portfolio[stock_name]['volume']
    total_price = portfolio[stock_name]['price']
    total_realized_PL = portfolio[stock_name]['realized_PL']

    add_stock_to_portfolio(stock_name, 0, total_volume, total_price, total_realized_PL)

portfolio_df = pd.DataFrame(portfolio_data)
statement_df = pd.DataFrame(statement_data)

last_end_line_available = statement_df['End Line Available'].iloc[-1]

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
    'Number of transactions:': [len(statement_df)],
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
################################################## End Ex Create and Save ##############################################################################

save_output(portfolio_df, "portfolio", team_name)
save_output(statement_df, "statement", team_name)
save_output(summary_df, "summary", team_name)