import pandas as pd
import numpy as np
import os
from datetime import datetime
from datetime import time

################################################################################################################################

team_name = '041_BID' 

################################################################################################################################

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

statements = []

file_path = '~/Desktop/Daily_Ticks.csv' 
df = pd.read_csv(file_path)

initial_investment = 10000000 

# Load the summary file
prev_summary_df = load_previous("summary", team_name)

if prev_summary_df is not None:
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

################################################################################################################################

################################################################################################################################

# dictionary สำหรับ portfolio
portfolio_data = {
    'Table Name': [],
    'File Name': [],
    'Stock name': [],
    'Start Vol': [],
    'Actual Vol': [],
    'Avg Cost': [],
    'Market Price': [],
    'Market Value': [],
    'Amount Cost': [],
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
    'Price': [],
    'Amount Cost': [],
    'End Line Available': []
}

# dictionary สำหรับ summary
summary_data = {
    'Table Name': [],
    'File Name': [],
    'trading_day': [],  
    'NAV': [],
    'Portfolio value': [],
    'End Line available': [],
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
################################################################################################################################
# แปลงข้อมูลเป็น DataFrame

################################################## Ex Create and Save ##############################################################################
# ตัวอย่างการสร้างไฟล์ และสร้างข้อมูล


def add_stock_to_portfolio(stock_name, start_vol, actual_vol, avg_cost, market_price, market_value, amount_cost, unrealized_PL, percentage_unrealized_PL, realized_PL):
    portfolio_data['Table Name'].append('Portfolio_file')
    portfolio_data['File Name'].append(team_name)
    portfolio_data['Stock name'].append(stock_name)
    portfolio_data['Start Vol'].append(start_vol)
    portfolio_data['Actual Vol'].append(actual_vol)
    portfolio_data['Avg Cost'].append(avg_cost)
    portfolio_data['Market Price'].append(market_price)
    portfolio_data['Market Value'].append(market_value)
    portfolio_data['Amount Cost'].append(amount_cost)
    portfolio_data['Unrealized P/L'].append(unrealized_PL)
    portfolio_data['% Unrealized P/L'].append(percentage_unrealized_PL)
    portfolio_data['Realized P/L'].append(realized_PL)

add_stock_to_portfolio("AOT", 0, 0, 0, 61.5, 0, 0, 0, 0, 0)
add_stock_to_portfolio("MARK", 0, 0, 0, 5.5, 0, 0, 0, 0, 0)

portfolio_df = pd.DataFrame(portfolio_data)

statement_data['Table Name'].append('Statement_file')
statement_data['File Name'].append(team_name)
statement_data['Stock Name'].append('AOT')
statement_data['Date'].append('2024-11-21')
statement_data['Time'].append('09:56:23 AM')
statement_data['Side'].append('Buy')
statement_data['Volume'].append('100')
statement_data['Price'].append('60.75')
statement_data['Amount Cost'].append('6075')
statement_data['End Line Available'].append(initial_balance)

statement_df = pd.DataFrame(statement_data)

last_end_line_available = 1
count_win = 1
count_sell = 1

summary_data = {
    'Table Name': ['Sum_file'],
    'File Name': [team_name],
    'trading_day': [1],  
    'NAV': [portfolio_df['Market Value'].sum() + last_end_line_available],
    'Portfolio value': [portfolio_df['Market Value'].sum()],
    'End Line available': [last_end_line_available],  # Use the correct End Line Available
    'Start Line available':[Start_Line_available],
    'Number of wins': [count_win], 
    'Number of matched trades': [count_sell], #นับ sell เพราะ เทรดbuy sellด้วย volume เท่ากัน
    'Number of transactions:': [len(statement_df)],
    'Net Amount': [statement_df['Amount Cost'].sum()],
    'Unrealized P/L': [portfolio_df['Unrealized P/L'].sum()],
    '% Unrealized P/L': [(portfolio_df['Unrealized P/L'].sum() / initial_investment * 100) if initial_investment else 0],
    'Realized P/L': [portfolio_df['Realized P/L'].sum()],
    'Maximum value': [statement_df['End Line Available'].max()],
    'Minimum value': [statement_df['End Line Available'].min()],
    'Win rate': [(count_win * 100)/ count_sell],
    'Calmar Ratio': [((portfolio_df['Market Value'].sum() + last_end_line_available - initial_investment) / initial_investment * 100) / \
                    ((portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000)],
    'Relative Drawdown': [(portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000 / statement_df['End Line Available'].max() * 100],
    'Maximum Drawdown': [(portfolio_df['Market Value'].sum() + last_end_line_available - 10_000_000) / 10_000_000],
    '%Return': [((portfolio_df['Market Value'].sum() + last_end_line_available - initial_investment) / initial_investment * 100)]
}

summary_df = pd.DataFrame(summary_data)
################################################## End Ex Create and Save ##############################################################################

save_output(portfolio_df, "portfolio", team_name)
save_output(statement_df, "statement", team_name)
save_output(summary_df, "summary", team_name)