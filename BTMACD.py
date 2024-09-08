import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

def calculate_macd(data, short_span=12, long_span=26, signal_span=9):
    data['EMA12'] = data['Close'].ewm(span=short_span, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=long_span, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_span, adjust=False).mean()
    return data

def find_crossovers(data):
    crossovers = []
    for i in range(1, len(data)):
        if data['MACD'].iloc[i-1] < data['Signal_Line'].iloc[i-1] and data['MACD'].iloc[i] > data['Signal_Line'].iloc[i]:
            crossovers.append(data.index[i])
        elif data['MACD'].iloc[i-1] > data['Signal_Line'].iloc[i-1] and data['MACD'].iloc[i] < data['Signal_Line'].iloc[i]:
            crossovers.append(data.index[i])
    return crossovers

def backtest_macd(stock_symbol, period='1mo'):
    data_5min = yf.download(stock_symbol, period=period, interval='5m')
    data_15min = yf.download(stock_symbol, period=period, interval='15m')

    if data_5min.empty or data_15min.empty:
        print(f"No data available for {stock_symbol} in the given period.")
        return pd.DataFrame()

    data_5min = calculate_macd(data_5min)
    data_15min = calculate_macd(data_15min)

    crossovers_5min = find_crossovers(data_5min)
    crossovers_15min = find_crossovers(data_15min)

    results = []
    for time_5min in crossovers_5min:
        for time_15min in crossovers_15min:
            time_gap = (time_15min - time_5min).total_seconds() / 60  # Gap in minutes
            results.append({
                '5min Time': time_5min,
                '15min Time': time_15min,
                'Gap (minutes)': time_gap
            })

    return pd.DataFrame(results)

if __name__ == '__main__':
    stock_symbol = '^GSPC'  # S&P 500 Index

    results_df = backtest_macd(stock_symbol, period='1mo')
    print(results_df)

    # Optionally save results to a CSV file
    if not results_df.empty:
        results_df.to_csv('SPX_MACD_Backtest_Results.csv', index=False)
        
        # Plot results if needed
        plt.figure(figsize=(14, 7))
        plt.plot(results_df['5min Time'], results_df['Gap (minutes)'], label='Gap between 5min and 15min crossovers')
        plt.title('Gap between 5min and 15min MACD Crossovers for SPX')
        plt.xlabel('5min Crossover Time')
        plt.ylabel('Gap (minutes)')
        plt.legend()
        plt.show()
