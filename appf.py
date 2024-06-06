import pandas as pd
import ta, time 
from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit
from datetime import timedelta



def  calculate_indicators(df):
    
    # Calculate SMA's
    df['sma_12'] = ta.trend.sma_indicator(df['close'], window=12, fillna=False)
    df['sma_24'] = ta.trend.sma_indicator(df['close'], window=24, fillna=False)
    df['sma_50'] = ta.trend.sma_indicator(df['close'], window=50, fillna=False)
    df['sma_200'] = ta.trend.sma_indicator(df['close'], window=200, fillna=False)

    # Calculate RSI
    df['rsi'] = ta.momentum.rsi(df['close'], window=14, fillna=False)

    # Calculate MACD
    
    #Slow moving average: 26 days. Fast moving average: 12 days. Signal line: 9-day moving #average of the difference between fast and slow.

    df['macd_histogram'] = macd_data = ta.trend.macd_diff(df['close'], window_slow=26, window_fast=12, window_sign=9, fillna=False)
    df['macd_fast'] = ta.trend.macd_signal(df['close'], window_slow=26, window_fast=12, window_sign=9, fillna=False)
    df['macd_slow'] = ta.trend.macd(df['close'], window_slow=26, window_fast=12, fillna=False)

    return df


app = Flask(__name__)
socketio = SocketIO(app)





# Sample DataFrame
df = pd.read_csv('RHEL.csv')
df.drop(df.columns[0], axis=1, inplace=True)
df.columns = df.columns.str.lower()
df = df.drop('adj close', axis=1)


df['date'] = pd.to_datetime(df['date'], utc=True)
df['date'] = df['date'] + timedelta(hours=5, minutes=30)  # Specify UTC as the timezone
df['time'] = df['date'].astype(int) // 10**9

df = calculate_indicators(df)
current_index = 0

dfx = df.head(1)  # Selecting the earliest row








def sidex(df):
    

    if df.iloc[-1]['close'] <= df.iloc[-2]['open']:
        return "Sell"
    elif df.iloc[-1]['close'] >= df.iloc[-2]['open']:
        return "Buy"

x = 0  # Global variable to track position status
entry_price = 0  # Global variable to store entry price
pct_change = 0
side = 0

def signalx(df):
    global x, entry_price, pct_change, side
    if x == 1:
        # pct_change = abs((df.iloc[-1]['close'] - entry_price) / entry_price * 100)
        pct_change = (df.iloc[-1]['close'] - entry_price) / entry_price * 100

        
        if side == 1:
            if pct_change <= -0.3:
                x = 0  # Close the position
                entry_price = 0
                return None  # No new signal as position is closed
    
        if side == 2:
            if pct_change >= 0.3 :
                x = 0  # Close the position
                entry_price = 0
                return None  # No new signal as position is closed
    
    # Check for new signals only if position is closed (x == 0)
    if x == 0:  
        if df.iloc[-1]['close'] <= df.iloc[-2]['open']:
            df.loc[df.index[-1], 'signal'] = '1'
            # df['signal'] = '1'
            x = 1
            side = 1
            entry_price = df.iloc[-1]['close']
            return "Sell"
        elif df.iloc[-1]['close'] >= df.iloc[-2]['open']:
            df.loc[df.index[-1], 'signal'] = '1'
            # df['signal'] = '2'
            x = 1
            side = 2
            entry_price = df.iloc[-1]['close']
            return "Buy"




def order(side, signal,df):
    print(f"{side}")
    print(f"{signal}")
    print(f"Close:{df.iloc[-1]['close']} ::: Open:{df.iloc[-2]['open']}")
    print(f"%CloseFromEntry:{pct_change}")
    print("#######################################################################")


def get_kline(n):
    # Sample implementation of kline returning consecutive rows
    new_data_df = df.head(n) 
    return new_data_df  

def kline(index):
    # Sample implementation of kline returning consecutive rows
    new_data = df.iloc[index]  # Get the row corresponding to the current index
    return pd.DataFrame([new_data])  # Convert the row to a DataFrame

    
def  range():
    global current_index, dfx

    new_df = kline(current_index+1) 
    dfx = pd.concat([dfx, new_df])
    # dfx = dfx.fillna(0)

    print(dfx)   

    side = sidex(dfx)
    signal = signalx(dfx)
    order(side, signal,df=dfx)
    dfx = dfx.fillna(0)

    # Convert Timestamp to string before emitting
    dfx['date'] = dfx['date'].astype(str)

    # current_index = current_index + 1

    # return  dfx[-1].to_dict() #dict of series latest 
    # return dfx.iloc[current_index].to_dict()
    data_for_index = dfx.iloc[current_index].to_dict()
    current_index += 1
    
    return data_for_index

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def emit_new_data():
    global current_index, df
    if current_index >= len(df):
        return
    
    data = range()
    socketio.emit('new_data', data, broadcast=True)
    time.sleep(1)
    socketio.start_background_task(emit_new_data)


@app.route('/')
def index():
   
    return render_template("index.html")

if __name__ == '__main__':
    # socketio.start_background_task(emit_new_data)
    from pytz import timezone

    from apscheduler.schedulers.background import BackgroundScheduler
    sched = BackgroundScheduler(daemon=True)
    ## sched.add_job(emit_new_data, 'interval', seconds=5)
    
    # Define the cron schedule to run every day at 3:00 PM IST from Monday to Friday
    # scheduler.add_job(emit_new_data_daily, 'cron', day_of_week='mon-fri', hour=15, minute=0, second=0, timezone=timezone('Asia/Kolkata'))
    # Define the cron schedule to run every day at 12:19 PM IST from Monday to Friday
    sched.add_job(emit_new_data, 'cron',  hour=15, minute=4, second=0, timezone=timezone('Asia/Kolkata'))


    sched.start()
    socketio.run(app, debug=False, port=5001)
