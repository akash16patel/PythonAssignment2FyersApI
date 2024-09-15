from fyers_apiv3 import fyersModel as FM
import logging as lg
import os
import pandas as pd
import requests as rq
from datetime import datetime
from collections import defaultdict

# Created this class as Wrapper class for FyersAPi
class FyersCodebase:
    def __init__(self,client_id,access_token,logger=None): # in this constructor i assigned client id and accesstoken which helps to get connection with fyers API
        self.client_id=client_id
        self.access_token=access_token
        self.fyers=FM.FyersModel(client_id=self.client_id,is_async=False,token=self.access_token) # here i am setting connection with fyersAPI
        self.logger=logger if logger else lg.getLogger("fyers_logger") # this logger help to monitor any changes API fail or success call response
        self.instrument_url="https://public.fyers.in/sym_details/NSE_FO.csv" # this is instrument.csv link provided by fyers as master symbol format
        self.instruemnt_Path="Dependency_File/all_instrument.csv" # instrument file save path
        self.df=None
        self._load_instruments() # created a load instrument method to load latest instrument  file created in dependencyfile directory
    def _load_instruments(self):
        try:
            response=rq.get(self.instrument_url)
            response.raise_for_status()
            with open(self.instruemnt_Path,'wb') as w:
                w.write(response.content)
            self.df=pd.read_csv("Dependency_File/all_instrument.csv") # It fetch instruments file from folder to make use in option chain
            self.df.columns = ['token', 'symbol_desc', 'tick_size', 'lot_size', 'price_step', 'na_1',
                               'timing', 'expiry_date', 'expiry_epoch', 'trading_symbol', 'min_lot_size',
                               'max_lot_size', 'token_number', 'underlying', 'strike_token', 'strike_price',
                               'option_type', 'underlying_token', 'na_2', 'oi', 'oi_change'] # here i Add headers in the instruments data frame as it is headerless to make use in ATM,OTM,ITM
            self.df.to_csv('Dependency_File/all_instrument_with_header.csv', index=False) # here i saved this for refernce
        except(rq.RequestException,pd.errors.EmptyDataError) as e:
            self.logger.error(f" failed to load instrument data:{e}")
            raise

    def _handle_response(self,response,expected_code=200): # making method to chekc some API response error as fyers API before processding next
        if response.get('code')!=expected_code:
            self.logger.error(f"API call failed to response:{response}")
            raise ValueError("Api call failed")
        return response

    def map_expiry_index(self,expiry_index,unique_expiry):# this method is helper method for assigning index in expiry_Epoch which help to fetch unique expiry for given underlying and script_Type
        if 0<=expiry_index <len(unique_expiry):
            return unique_expiry[expiry_index]
        else:
            raise ValueError("Invalid expiry index provided")
    def get_data_for_single_script(self,exchange,name,call_type): # this method provide last trading price ,ohlc and quote as per input
        data={
            "symbol":f"{exchange}:{name}",
            "ohlcv_flag": "1"

        } #this data set is for ltp
        dataquote={
            "symbols":f"{exchange}:{name}"
        } # this for dataquote
        try:
            if call_type.lower() == "quote":
                response=self.fyers.quote(data=dataquote) # using fyers quote method it will return required data
                self._handle_response(response)
                return response['d']['v']
            else:
                response=self.fyers.depth(data=data) # for ltp and ohlc i used depth method of fyersAPi
                if response['s']=="ok":
                    if call_type.lower()=="ohlc":
                        return{call: response['d'][f'{exchange}:{name}'][call] for call in ('o','h','l','c')} # returning filter data for ohlc as it o:"open",h:"High",l:"Low",c"close we get all value respectively
                    else:
                         return response['d'][f'{exchange}:{name}'][call_type]
        except Exception as e:
            self.logger.error(f"failed to get data for script {name}: {e} ")
            raise

    def place_order(self,order_type,exchange,symbol,transaction_type,quantity,product_type,trigger_price=0): # this method is for placing differt type of order
        try:
            get_order_type=lambda ot:{"limit":1,"market":2,"stoporder":3,"Stoplimit":4}.get(ot) # mapping of ordertype is done as Api get value in integer for order type
            order_type=get_order_type(order_type)
            if transaction_type.upper()=="BUY": # for transction type like buy or sale ,this also accept 1(Buy) or -1(SEll)
                transaction_type=1
            else:
                transaction_type=-1
            if order_type==1:
                trigger_price=float(input("Please enter your Trigger price for limit order: "))

            data={
                "symbol": f"{exchange}:{symbol}",
                "qty": quantity,
                "type": order_type,
                "side": transaction_type,
                "productType": product_type.upper(),
                "limitPrice": trigger_price,
                "stopPrice": 0,
                "validity": "DAY",
                "disclosedQty": 0,
                "offlineOrder": False,
                "orderTag": "tag1"
                                    }
            response=self.fyers.place_order(data=data)# this fyer api call place order in live market through api
            self.logger.info(f"order place with id:{response['id']}")
            return response['id'] # here i am returning only order id as per requiremenmt of task
        except Exception as e:
            self.logger.error(F"faild to place order :{e}")
            raise

    def get_order_details(self): #This method return last order details
        try:
            response=self.fyers.orderbook() # using fyersAPi method ordebook to get all order details
            if response['s'] !="ok":
                return "please check Fyers Api log for details"
            length=len(response['orderBook']) # Calculating length of list of order to return last order ,it use as index to return last order detail

            response=response['orderBook'][length-1] # here i am returning last order data
            status=response['status']
            get_status=lambda st:{1:"Canceled",2:"Traded/Filled",3:"NOt Used Currently",4:"Transit",5:"Rejected",6:"Pending",7:"Expired"}.get(st) # using lambda function mapping status of  order for better readability as staus is in integer like ,1,2,or 3 etc. so i just mapped as per APi Docs.
            status=get_status(status)
            return response['orderDateTime'],response['tradedPrice'],status # returning required data as per task
        except Exception as e:
            self.logger.error(f"Failed to get order details:{e}")
            raise



    def get_atm(self,ltp,underlying,expiry,script_type): # this Method is to get ATM(At-the-money) of Optionchain

       try:
            required_df=self.df[self.df['underlying']==underlying] # here i am filtering data which is fetch from instruments file and added headername in dataframe,based on underlying input by user it just filter the data frame keep all data of only underlying symbol
            expiry=self.map_expiry_index(expiry,sorted(required_df['expiry_epoch'].unique())) # here sorting of expiry_epoch is done as unique expiry we got and also assigning index as 0,1,2 etc for all unique expiry for the given underlying .
            required_df=required_df[(required_df['expiry_epoch']==expiry )&(required_df['option_type']==script_type.upper())] #Now more filter is applied based on expiry and option type ,it gives only data which matching expiry and option for input underlying
            if required_df.empty:
                return "No matching data for the given expiry or script_Type"
            required_df=required_df.sort_values(by='strike_price') # now here i sorted the dataframe based on strike price
            required_df['diff']=abs(required_df['strike_price']-ltp) # here as per ATM i am using difference of strike price and ltp to get more filtered data
            atm=required_df.loc[required_df['diff'].idxmin()] # here making table for required data to return trading symbol of for ATM
            return atm['trading_symbol']
       except Exception as e:
            self.logger.error(f"failed to get atm option:{e}")
            raise






    def get_itm(self,ltp,underlying,expiry,multiplier,script_type): # this Method is to get ITM(In-The-Money) of option chain
        try:
            required_df = self.df[self.df['underlying'] == underlying] # here i am filtering data which is fetch from instruments file and added headername in dataframe,based on underlying input by user it just filter the data frame keep all data of only underlying symbol
            expiry = self.map_expiry_index(expiry, sorted(required_df['expiry_epoch'].unique()))  # here sorting of expiry_epoch is done as unique expiry we got and also assigning index as 0,1,2 etc for all unique expiry for the given underlying .

            required_df = required_df[(required_df['expiry_epoch'] == expiry) & (required_df['option_type'] == script_type.upper())] #Now more filter is applied based on expiry and option type ,it gives only data which matching expiry and option for input underlying
            if required_df.empty:
                return "No matching data for the given expiry and script_Type"
            required_df=required_df.sort_values(by="strike_price") # now here i sorted the dataframe based on strike price

            if script_type.upper()=='CE':
                itm=required_df[required_df['strike_price']<=ltp] # As per definition of ITM here i just filtered the data as per strikeprice and ltp
            else:
                itm=required_df[required_df['strike_price']>=ltp]
            if itm.empty:
                return "No ITM option Found"
            itm_Mul=itm.iloc[-multiplier] if len(itm)>=multiplier else itm.iloc[-1] # here multplier are used to find as depth of the data

            return itm_Mul['trading_symbol']
        except Exception as e:
            self.logger.error(f"faild to get itm option: {e}")

    def get_otm(self,ltp,underlying,expiry,multiplier,script_type):
        try:
            required_df = self.df[self.df['underlying'] == underlying] # here i am filtering data which is fetch from instruments file and added headername in dataframe,based on underlying input by user it just filter the data frame keep all data of only underlying symbol

            expiry = self.map_expiry_index(expiry, sorted(required_df['expiry_epoch'].unique())) # here sorting of expiry_epoch is done as unique expiry we got and also assigning index as 0,1,2 etc for all unique expiry for the given underlying .


            required_df = required_df[(required_df['expiry_epoch'] == expiry) & (required_df['option_type'] == script_type.upper())
                                  ]
            if required_df.empty:
                return "No matching data for the given expiry and script_Type"
            required_df=required_df.sort_values(by='strike_price')
            if script_type.upper()=='CE':
                otm=required_df[required_df['strike_price']>ltp]
            else:
                otm=required_df[required_df['strike_price']<ltp]
            if otm.empty:
                return "No OTM Option Found"
            otm_Mul=otm.iloc[multiplier-1]if len(otm)>=multiplier else otm.iloc[0]


            return otm_Mul['trading_symbol']
        except Exception as e:
            self.logger.error(f"no otm option found {e}")
            raise

    def get_expiries(self,scripname,exchange,expiry_type): # this method gives expires of given scripname as per expiry_type from option chain
        try:
            data={
                "symbol":f"{exchange}:{scripname}",
                "strikecount":2,
                "timestamp": ""} #  request data  as per fyersAPi
            response=self.fyers.optionchain(data=data)
            self._handle_response(response)


            expiry=response['data'] # here i am filtering data where expiry dates are available

            expiry_dates=expiry['expiryData'] # now only expiry list are filtered here
            group_expiry=defaultdict(list) # here i declare a dict for mapping expiry based on same months and year
            for item in expiry_dates: # this loop will filtered the same months and year
                date=datetime.strptime(item['date'],"%d-%m-%Y")
                month_year=date.strftime("%m-%Y")
                group_expiry[month_year].append(item)

            sorted_group_expiry={ge:group_expiry[ge] for ge in sorted(group_expiry)} # here i am sorting our mapped data based on current expiry dates as in increaing order

            month_count={
                "one":1,
                "two":2,
                "three":3,
                "four":4,
                "all":len(sorted_group_expiry)
            }.get(expiry_type,len(sorted_group_expiry)) # now as per user input we filtered the expiry
            filter_expiry=[]
            for i,(month,data) in enumerate(sorted_group_expiry.items()):
                if i< month_count:
                    filter_expiry.extend(data)

            dates=[item['date'] for item  in  filter_expiry ] # returning dates of expiry as per input like ,for one : it return first months data,for two: it return first two months data as on
            return dates
        except Exception as e:
            self.logger.error(f"failed to get expiry dates : {e}")


