import os
import shutil
import zipfile

def clear_directory(directory):
    shutil.rmtree(directory, ignore_errors=True)
    os.makedirs(directory)
    return directory

def create_zip_file(date):
    zip_file_name = f"data_csv_{date}.zip"
    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    return zipf, zip_file_name

def get_symbol_info_for_date(strike_price, option_type):
    return get_symbol_info('NFO', 'OPTIDX', 'NIFTY', strike_price, option_type).iloc[0]

def create_directory_for_symbol_info(save_directory, symbol_info, strike_price, option_type):
    directory_name = f"{symbol_info.symbol}_{strike_price}_{option_type}"
    directory_path = os.path.join(save_directory, directory_name)
    os.makedirs(directory_path, exist_ok=True)
    return directory_path, directory_name

def get_candle_data_for_interval(symbol_info, interval, date):
    fromdate = f'{date} 09:15'
    todate = f'{date} 15:30'
    return get_candle_data(symbol_info, interval, fromdate, todate)

def save_data_to_csv(data_frame, directory_path, symbol_info, strike_price, interval, option_type):
    file_name = f"{symbol_info.symbol}_{strike_price}_{interval}_{option_type}.csv"
    file_path = os.path.join(directory_path, file_name)
    data_frame.to_csv(file_path, index=False)
    return file_path

def add_files_to_zip(zipf, directory_path, directory_name):
    for filename in os.listdir(directory_path):
       

