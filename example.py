from FyersCodebase import *
import logging

#Initialize logger
logger = lg.getLogger("fyers_logger")
# getting Access token from access.txt which is in Dependency file:
with open('Dependency_File/access.txt', 'r') as access:
    access_token = access.read()
#Intialize Fyerscodebase instance with client id and access_token
broker = FyersCodebase(client_id="FK9E8YPI2C-100", access_token=access_token, logger=logger)
#Get Last trading price for the given script with their type(Eg. "EQ") and also from desire exchange(Eg."NSE","BSE")
# you can also get "ohlc" and quote if you make change in calltype as string (Eg."ohlc","quote"), make change in print as per call type
# Purpose: Fetches the last traded price (LTP) of the specified script (NIFTY 50) on the National Stock Exchange (NSE).
# Method Explanation:
# exchange='NSE' specifies the exchange (NSE in this case,other options are NFO,BSE,CDS,MCX).
# name='SBIN-EQ' specifies the scrip name, this is a trading symbol .
# call_type='ltp' fetches the last traded price.(you call also fetch ohlc,quotes data by passing args as "ohlc","quote")

ltp = broker.get_data_for_single_script(exchange="NSE", name="SBIN-EQ", call_type="ltp")
print(f"LTP  is {ltp}")
# Place order: parameters option provided by fyers API-->
# ordertype
# {1 => Limit Order 2 => Market Order 3 => Stop Order (SL-M) 4 => Stoplimit Order (SL-L)},producttype {"INTRADAY","CNC","CO","BO","MARGIN","ALL". Eg: ["INTRADAY","CNC"]},transcation type(side){"BUY","SELL"},
# for limit order you need to give trigger price it will ask when you change order type ("limit")
# it gives order id wheater is successfully place or not.
order_id = broker.place_order(order_type="market", exchange="NSE", symbol="SBIN-EQ", transaction_type="BUY", quantity=1,
                              product_type="CNC")
print(f"order_id = {order_id}")
#this give most recent order  place  details no need any arguments to pass
excuted_time, excuted_price, order_status = broker.get_order_details()
print(f"executed time={excuted_time},executed price={excuted_price},order status={order_status}")
#From here we making calls releated to option chain
# for ATM(At-the-money) based on last trading price (ltp)

# Purpose: Fetches the At-The-Money (ATM) option strike price based on the last traded price (ltp) for the NIFTY 50 index.
# This is typically used to identify the option contract closest to the current market price.
# ltp: The last traded price of NIFTY 50.
# underlying='NIFTY': The underlying NIFTY(GEt this symbol from all_instrument file from Dependecy_FILe folder .
# expiry=0: Current expiry (next expiry can be set with expiry=1). other options(0,1,2)
# script_type='CE' or 'PE':
atm = broker.get_atm(ltp=ltp, underlying="SBIN", expiry=0, script_type="CE")
print(f"ATM Option Chain =={atm}")
# Purpose: Fetches the In-The-Money (ITM) option strike prices based on the ltp for the SBIN(CHEck from underlying of from all instrument files from dependecy folder).
# The multiplier=5 indicates how far deep into the ITM options we want to go.
# multiplier=5: Fetches the 5th In-The-Money option.
# script_type='CE' or 'PE'
# returns a trading symbol of that strike
itm = broker.get_itm(ltp=ltp, underlying='SBIN', expiry=0, multiplier=5, script_type='CE')
print(f"ITM option chain=={itm}")
# Purpose: Fetches Out-of-The-Money (OTM) option strike prices based on the ltp for the NIFTY 50 index. Similar to ITM, the multiplier=5 fetches the 5th OTM strike.
# Key Parameters:
# multiplier=5: Fetches the 5th Out-of-The-Money option.
# script_type='CE' or 'PE':
# returns a trading symbol of that strike
otm = broker.get_otm(ltp=ltp, underlying='SBIN', expiry=0, multiplier=5, script_type="CE")
print(f"OTM option chain=={otm}")
# This will give you expiry dates for option chain
# in this you may change expiry_Type like eg.("one": it gives one months expiry dates ,"two" It gives two months expiry dates include first ,"all" : gives all expiry dates
expiry = broker.get_expiries(scripname='NIFTY50-INDEX', exchange='NSE', expiry_type='one')
print(f"expiry= {expiry}")
