import pandas as pd
import matplotlib.pyplot as plt

# Returns CSV file data
class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        data = pd.read_csv(self.file_path)
        return data

class Strategy:
    def generate_signals(self, data):
        # Implement strategy logic (e.g., moving averages)
        pass

class Backtest:
    def __init__(self, data, strategy):
        self.data = data
        self.strategy = strategy
        self.results = []

    def run(self):
        # Execute strategy and track performance
        pass

class PerformanceAnalyzer:
    def analyze(self, results):
        # Calculate metrics and generate reports
        pass

# Plot Data for Stock
def plot_stock_prices(df):
    df['Close/Last'] = df['Close/Last'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Open'] = df['Open'].str.replace('$', '').str.replace(',', '').astype(float)
    df['High'] = df['High'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Low'] = df['Low'].str.replace('$', '').str.replace(',', '').astype(float)
    df['Volume'] = df['Volume'].astype(int)
    
    for i in range(len(df['Close/Last'])):
        print(df['Close/Last'][i])

    df['Date'] = pd.to_datetime(df['Date'])

    plt.figure(figsize=(14, 10))

    plt.plot(df['Date'], df['Close/Last'], label='Close Price', color='black')

    # Adding labels and title
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')
    title = 'Stock Prices'
    plt.title(title)
    plt.xticks(rotation=45)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.2)

    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

data_loader = DataLoader('SPY.csv')
data = data_loader.load_data()
plot_stock_prices(data)
