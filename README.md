# PythonAssignment2FyersApI
This Python project is an API wrapper of the Fyers API that allows users to easily perform operations such as pulling market data, trading, and working with options. The code is well structured and follows the concepts of OOP and also uses exception handling, logging, etc., which makes the code highly maintainable and extensible.
## Features
Retrieve the full quote symbol, or Last Traded Price (LTP), of a particular stock.
Get Order Id
Enter various types of orders- Market order- Limit order.
Get At-The-Money (ATM), In-The-Money (ITM), and Out-of-The-Money (OTM) options.
Obtain the expiry dates for option’s chains.
## Setup:
 ### Fyers API Credentials:
  Hence  need your client id and consequently the access token from the fyersAPI. In addition, I save one file with a name access. txt” within a directory called Dependency_File and save  access token on that file.
  ## In project folder i implemented the 2 file name "get_connect.py",and "gererate_token.py" and also i have mention some step in this file for how to get auth code and and accesstoken ,for now i have refresh token which is valid for 15 days so to first run generate_token.py to get access token and next just run example.py where i have given some data for call.
  ## Install Required Depencies from requirement.txt 
  ## i have implemented Logger so if any issue check my fyersAPI.log and fyersrequest.log 
  ## i am providing some snap shot to get clear understanding 
      ![image](https://github.com/user-attachments/assets/26313bc4-3494-428a-ba5e-a0c0f43c587d)

      
### Method Implimented:
In fyersApi Wrapper class Name FyersCodebase:
#### get_data_for_single_script(exchange="NSE", name="SBIN-EQ", call_type="ltp") will return last trading price:
      #Get Last trading price for the given script with their type(Eg. "EQ") and also from desire exchange(Eg."NSE","BSE")
      # you can also get "ohlc" and quote if you make change in calltype as string (Eg."ohlc","quote"), make change in print as per call type
      # Purpose: Fetches the last traded price (LTP) of the specified script (NIFTY 50) on the National Stock Exchange (NSE).
      # Method Explanation:
      # exchange='NSE' specifies the exchange (NSE in this case,other options are NFO,BSE,CDS,MCX).
      # name='SBIN-EQ' specifies the scrip name, this is a trading symbol .
      # call_type='ltp' fetches the last traded price.(you call also fetch ohlc,quotes data by passing args as "ohlc","quote")
####  place_order(order_type="market", exchange="NSE", symbol="SBIN-EQ", transaction_type="BUY", quantity=1,product_type="CNC")      
      # ordertype
      # {1 => Limit Order 2 => Market Order 3 => Stop Order (SL-M) 4 => Stoplimit Order (SL-L)},producttype {"INTRADAY","CNC","CO","BO","MARGIN","ALL". Eg: ["INTRADAY","CNC"]},transcation type(side){"BUY","SELL"},
      # for limit order you need to give trigger price it will ask when you change order type ("limit")
      # it gives order id wheater is successfully place or not.
#### get_order_details()
    #this give most recent order  place  details no need any arguments to pass
#### get_atm(ltp=ltp, underlying="SBIN", expiry=0, script_type="CE")
    # Purpose: Fetches the In-The-Money (ITM) option strike prices based on the ltp for the SBIN(CHEck from underlying of from all instrument files from dependecy folder).
    # The multiplier=5 indicates how far deep into the ITM options we want to go.
    # multiplier=5: Fetches the 5th In-The-Money option.
    # script_type='CE' or 'PE'
    # returns a trading symbol of that strike
#### get_itm(ltp=ltp, underlying='SBIN', expiry=0, multiplier=5, script_type='CE')
    # Purpose: Fetches the In-The-Money (ITM) option strike prices based on the ltp for the SBIN(CHEck from underlying of from all instrument files from dependecy folder).
    # The multiplier=5 indicates how far deep into the ITM options we want to go.
    # multiplier=5: Fetches the 5th In-The-Money option.
    # script_type='CE' or 'PE'
    # returns a trading symbol of that strike
#### get_otm(ltp=ltp, underlying='SBIN', expiry=0, multiplier=5, script_type="CE")
    # Purpose: Fetches Out-of-The-Money (OTM) option strike prices based on the ltp for the NIFTY 50 index. Similar to ITM, the multiplier=5 fetches the 5th OTM strike.
    # Key Parameters:
    # multiplier=5: Fetches the 5th Out-of-The-Money option.
    # script_type='CE' or 'PE':
    # returns a trading symbol of that strike
#### get_expiries(scripname='NIFTY50-INDEX', exchange='NSE', expiry_type='one')
    # This will give you expiry dates for option chain
    # in this you may change expiry_Type like eg.("one": it gives one months expiry dates ,"two" It gives two months expiry dates include first ,"all" : gives all expiry dates


 ### FyersCodebase Class: Overview and Documentation

The `FyersCodebase` class is designed to interact with Fyers API for executing various trading-related operations, such as fetching instrument data, placing orders, getting option chain data, and retrieving current market details for individual scripts (stocks). Here's a detailed breakdown of its functionality, divided into key sections:

---

#### Initialization (`__init__` method)
The `__init__` method sets up the initial state of the class by initializing client credentials, configuring the logger, and loading instruments. 
- **client_id**: Your Fyers client ID for API authentication.
- **access_token**: The access token for authorized API calls.
- **logger**: Logger for capturing error logs and debug information. If not provided, it defaults to a simple logger setup.
- **instrument_url**: URL pointing to the instrument details CSV for Fyers' NSE FO market.
- **instrument_Path**: File path for saving the instrument data.
- **df**: Pandas DataFrame for holding the instrument data after it’s loaded.

---

#### `_load_instruments` Method
This private method downloads the instrument data from the provided URL and loads it into a DataFrame (`df`). It also saves this data to a CSV file for further use. 
- Downloads the CSV from Fyers' instrument URL.
- Renames columns and stores the file locally.

**Error Handling**: 
- If the data fails to download or is malformed, an error is logged and raised using the logger.

---

#### `_handle_response` Method
This utility method checks if an API call response returns the expected status code (usually 200). 
- If the response code does not match the expected code, it logs an error and raises a `ValueError`.

---

#### `map_expiry_index` Method
Maps an expiry index to the corresponding expiry date in a list of unique expiries.
- The expiry date is retrieved based on the index, ensuring valid access within the list’s bounds.
- Raises `ValueError` if the expiry index is invalid.

---

#### `get_data_for_single_script` Method
Fetches data for a specific script (stock or derivative) from Fyers based on the call type:
- **exchange**: Market exchange (e.g., NSE, BSE).
- **name**: The trading symbol or name of the stock or derivative.
- **call_type**: The type of data required (e.g., **quote** for real-time price data or **ohlc** for open-high-low-close data).

Based on the `call_type` provided:
- If **quote**: It fetches the latest quote.
- If **ohlc**: Returns open-high-low-close data for the script.
- Other call types can return more specific data (e.g., depth of market).

---

#### `place_order` Method
This method places an order on the exchange.
- **order_type**: Specifies the type of order (limit, market, stop order, or stop-limit).
- **exchange**: Exchange where the order is placed.
- **symbol**: The trading symbol for the order.
- **transaction_type**: Indicates buy or sell.
- **quantity**: Quantity of the stock or derivative.
- **product_type**: Product type (e.g., intraday or delivery).
- **trigger_price**: The trigger price for limit or stop orders.

Order type is mapped to a predefined set of types, and based on the input, an API call to place an order is made.

**Error Handling**:
- Logs any errors encountered during order placement.

---

#### `get_order_details` Method
Retrieves the details of the most recent order from the order book.
- Uses the Fyers API's `orderbook` method to fetch all orders, and returns details of the most recent one.
- It also provides a human-readable order status such as **Canceled**, **Traded**, **Pending**, etc.

**Error Handling**: 
- Logs any errors encountered during fetching order details.

---

#### `get_atm` Method (At-the-Money Option)
This method finds the At-the-Money (ATM) option for an underlying asset based on the Last Traded Price (LTP).
- **ltp**: The last traded price of the underlying asset.
- **underlying**: The underlying asset symbol.
- **expiry**: Index of the expiry date (retrieved using `map_expiry_index`).
- **script_type**: Call (CE) or Put (PE) option.

The method filters the instrument data to match the given underlying asset, expiry, and script type, and identifies the strike price closest to the LTP as the ATM option.

---

#### `get_itm` Method (In-the-Money Option)
The `get_itm` method fetches the In-the-Money (ITM) option based on the following:
- **ltp**: The last traded price of the underlying asset.
- **underlying**: The underlying asset symbol.
- **expiry**: Index of the expiry date (retrieved using `map_expiry_index`).
- **multiplier**: The number of steps In-the-Money (multiplier).
- **script_type**: Call (CE) or Put (PE) option.

It returns the ITM option that is either below (for Call) or above (for Put) the last traded price.

---

#### `get_otm` Method (Out-of-the-Money Option)
The `get_otm` method fetches the Out-of-the-Money (OTM) option:
- **ltp**: The last traded price of the underlying asset.
- **underlying**: The underlying asset symbol.
- **expiry**: Index of the expiry date.
- **multiplier**: Steps out of the money.
- **script_type**: Call (CE) or Put (PE) option.

It returns the OTM option that is either above (for Call) or below (for Put) the last traded price.

---

#### `get_expiries` Method
Fetches all available expiry dates for a given option symbol and filters them based on the user's expiry preference.
- **scripname**: The name of the option's underlying asset.
- **exchange**: Exchange where the options are traded.
- **expiry_type**: Filter based on time (e.g., one month, two months, etc.).

The method groups expiries by month-year combinations and returns the expiry dates based on the filter provided.

---


