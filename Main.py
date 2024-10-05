import pandas as pd
import matplotlib.pyplot as plt

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        try:
            data = pd.read_csv(self.file_path)
            data['Close/Last'] = data['Close/Last'].str.replace('$', '').str.replace(',', '').astype(float)
            data['Open'] = data['Open'].str.replace('$', '').str.replace(',', '').astype(float)
            data['High'] = data['High'].str.replace('$', '').str.replace(',', '').astype(float)
            data['Low'] = data['Low'].str.replace('$', '').str.replace(',', '').astype(float)
            data['Volume'] = data['Volume'].astype(int)
            data['Date'] = pd.to_datetime(data['Date'])
            data.set_index('Date', inplace=True)
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

class Strategy:
    def __init__(self):
        self.signals_df = pd.DataFrame(columns=['timestamp', 'percentage change'])

    def generate_percentage_change(self, data):
        if 'Close/Last' not in data.columns:
            raise ValueError("Data must contain a 'Close/Last' column.")
        self.signals_df = self.signals_df._append({'timestamp': data.index[0], 'percentage change': 0}, ignore_index=True)

        for i in range(1, len(data['Close/Last'])):
            previous_price = data['Close/Last'].iloc[i-1]
            current_price = data['Close/Last'].iloc[i]

            percentage_change = ((current_price - previous_price) / previous_price) * 100 if previous_price != 0 else 0

            self.signals_df = self.signals_df._append({
                'timestamp': data.index[i],
                'percentage change': percentage_change
            }, ignore_index=True)

        return self.signals_df

    def calculate_rsi(self, window=14):
        if len(self.signals_df) < window:
            raise ValueError("Not enough data points to calculate RSI.")
        
        # Calculate gains and losses
        self.signals_df['gain'] = self.signals_df['percentage change'].where(self.signals_df['percentage change'] > 0, 0)
        self.signals_df['loss'] = -self.signals_df['percentage change'].where(self.signals_df['percentage change'] < 0, 0)

        # Calculate rolling averages
        avg_gain = self.signals_df['gain'].rolling(window=window, min_periods=1).mean()
        avg_loss = self.signals_df['loss'].rolling(window=window, min_periods=1).mean()

        # Avoid division by zero errors by setting avg_loss to a very small value if it's zero
        avg_loss = avg_loss.replace(0, 1e-10)
        
        # Relative Strength (RS)
        rs = avg_gain / avg_loss

        # Relative Strength Index (RSI)
        self.signals_df['RSI'] = 100 - (100 / (1 + rs))
        return self.signals_df



class Backtest:
    def __init__(self, data, strategy, initial_balance):
        self.data = data
        self.strategy = strategy
        self.balance = initial_balance
        self.results = []
        self.position = None 
        self.shares = 0
        self.net_worth_history = []

    def run(self):
        # Check if lengths of signals_df and data are compatible
        if len(self.strategy.signals_df) != len(self.data['Close/Last']):
            raise ValueError("The length of signals_df and data must be the same.")

        print("Timestamp, Buy/Sell, RSI Value, Current Price, Total Shares Owned, Current Balance, Net Portfolio")
        
        for i in range(len(self.strategy.signals_df) - 1, -1, -1):
            rsi_value = self.strategy.signals_df['RSI'].iloc[i]
            current_price = self.data['Close/Last'].iloc[i]

            # Calculate the current balance based on shares held
            net_worth = self.balance + (self.shares * current_price)
            self.net_worth_history.append(round(net_worth, 2))  # Store current balance


            if rsi_value < 20 and self.position is None and self.balance >= current_price:
                # Buy signal
                self.position = 'buy'
                self.shares = int(self.balance / current_price)
                self.balance -= self.shares * current_price
                self.balance = round(self.balance, 2)
                self.results.append((self.strategy.signals_df['timestamp'].iloc[i], 'Buy', round(rsi_value, 2), current_price, self.shares, self.balance, round(net_worth, 2)))

            elif rsi_value > 85 and self.position == 'buy':
                # Sell signal
                self.position = None
                self.balance += self.shares * current_price
                self.balance = round(self.balance, 2)
                self.shares = 0
                self.results.append((self.strategy.signals_df['timestamp'].iloc[i], 'Sell', round(rsi_value, 2), current_price, self.shares, self.balance, round(net_worth, 2)))
        return self.results


    def plot_portfolio(self):
        
        if len(self.net_worth_history) > len(self.strategy.signals_df['timestamp']):
            self.net_worth_history = self.net_worth_history[:-1]  # Remove the last element

        plotItem = self.net_worth_history
        plotItem.reverse()

        plt.figure(figsize=(14, 8))
        plt.plot(self.strategy.signals_df['timestamp'], plotItem, label='Portfolio Balance', color='Black')
        plt.xlabel('Date')
        plt.ylabel('Balance (USD)')
        plt.title('Portfolio Balance Over Time')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()




def plot_stock_prices(df):
    plt.figure(figsize=(14, 10))
    plt.plot(df.index, df['Close/Last'], label='Close Price', color='black')
    plt.xlabel('Date')
    plt.ylabel('Close Price (USD)')
    plt.title('Stock Prices')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Main execution
data_loader = DataLoader('SPY.csv')
data = data_loader.load_data()

if data is not None:  # Check if data loaded successfully
    strategy = Strategy()
    strategy.generate_percentage_change(data)  # Generate percentage changes
    strategy.calculate_rsi(window=14)  # Calculate RSI

    backtest = Backtest(data, strategy, 10000)
    results = backtest.run()
    backtest.plot_portfolio()

    # Print results
    for result in results:
        print(result)

    #plot_stock_prices(data)  # Plot the stock prices
else:
    print("Data loading failed.")
