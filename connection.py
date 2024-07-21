from binance.client import Client
import time
from binance.exceptions import BinanceAPIException, BinanceOrderException
from dotenv import load_dotenv
import os
from math import floor
load_dotenv()

client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_API_SECRET"))

def buy_sol_in_usdt(quantity):
    try:
        # Get the current price of SOL/USDT
        ticker = client.get_symbol_ticker(symbol="SOLUSDT")
        current_price = float(ticker['price'])

        # Calculate the quantity of SOL to buy
        sol_quantity = quantity / current_price

        # Round down the quantity to the appropriate decimal places
        # You may need to adjust this based on Binance's requirements for SOL
        sol_quantity = round(sol_quantity, 2)

        # Place the market order
        order = client.create_order(
            symbol='SOLUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quoteOrderQty=quantity  # This specifies we want to spend 100 USDT
        )

        return f"Order placed successfully: {order}"

    except BinanceAPIException as e:
        print(f"An API Exception occurred: {e}")
    except BinanceOrderException as e:
        print(f"An Order Exception occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def sell_sol_for_usdt(quantity):
    try:

        ticker = client.get_symbol_ticker(symbol="SOLUSDT")
        current_price = float(ticker['price'])

        # Calculate the quantity of SOL to buy
        sol_quantity = quantity / current_price
        sol_quantity = round(sol_quantity, 3)

        # Place the market order to sell SOL
        order = client.create_order(
            symbol='SOLUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=sol_quantity  # This specifies the amount of SOL to sell
        )

        return f"Order placed successfully: {order}"

    except BinanceAPIException as e:
        print(f"An API Exception occurred: {e}")
    except BinanceOrderException as e:
        print(f"An Order Exception occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def buy_sol_with_all_usdt():
    try:
        # Get account balance
        account = client.get_account()
        usdt_balance = float(next(asset['free'] for asset in account['balances'] if asset['asset'] == 'USDT'))
        print(usdt_balance)
        if usdt_balance == 0:
            return "USDT balance is 0"
        # Place order using all available USDT
        order = client.create_order(
            symbol='SOLUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quoteOrderQty=usdt_balance
        )

        return f"Bought SOL with {usdt_balance} USDT. Order details: {order}"

    except BinanceAPIException as e:
        return f"An API Exception occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

def sell_all_sol():
    try:
        # Get account balance
        account = client.get_account()
        sol_balance = float(next(asset['free'] for asset in account['balances'] if asset['asset'] == 'SOL'))
        # Round down to ensure we don't exceed available balance
        sol_balance = floor(sol_balance * 1000)  # Adjust decimal places as needed
        print(sol_balance)
        sol_balance = sol_balance/1000
        if sol_balance == 0:
            return "SOL balance is 0"
        # Place order to sell all available SOL
        order = client.create_order(
            symbol='SOLUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=sol_balance
        )

        return f"Sold {sol_balance} SOL. Order details: {order}"

    except BinanceAPIException as e:
        return f"An API Exception occurred: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Test the connection by fetching the server time
if __name__=="__main__":
    try:
        account_info = client.get_account()
        balances = account_info['balances']
        
        sol_balance = next((asset['free'] for asset in account_info['balances'] if asset['asset'] == 'SOL'), 0)
        print(f"Your SOL balance is: {sol_balance}")
        print(buy_sol_in_usdt(10))
        print(sell_all_sol())

    except Exception as e:
        print(f"Connection error: {e}")