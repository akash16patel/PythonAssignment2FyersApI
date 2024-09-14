from fyers_apiv3 import fyersModel as FM
import logging as lg
import os
import pandas as pd
import requests as rq
from datetime import datetime
from collections import defaultdict


class FyersCodebase:
    def __init__(self,client_id,access_token,logger=None):
        self.client_id=client_id
        self.access_token=access_token
        self.fyers=FM.FyersModel(client_id=self.client_id,is_async=False,token=self.access_token)
        self.logger=logger if logger else lg.getLogger("fyers_logger")
        self.instrument_url="https://public.fyers.in/sym_details/NSE_FO.csv"
        self.instruemnt_Path="Dependency_File/all_instrument.csv"
        self.df=None
        self._load_instruments()
    def _load_instruments(self):
        try:
            response=rq.get(self.instrument_url)
            response.raise_for_status()
            with open(self.instruemnt_Path,'wb') as w:
                w.write(response.content)
            self.df=pd.read_csv("Dependency_File/all_instrument.csv")
            self.df.columns = ['token', 'symbol_desc', 'tick_size', 'lot_size', 'price_step', 'na_1',
                               'timing', 'expiry_date', 'expiry_epoch', 'trading_symbol', 'min_lot_size',
                               'max_lot_size', 'token_number', 'underlying', 'strike_token', 'strike_price',
                               'option_type', 'underlying_token', 'na_2', 'oi', 'oi_change']
            self.df.to_csv('Dependency_File/all_instrument_with_header.csv', index=False)
        except(rq.RequestException,pd.errors.EmptyDataError) as e:
            self.logger.error(f" failed to load instrument data:{e}")
            raise

    def _handle_response(self,response,expected_code=200):
        if response.get('code')!=expected_code:
            self.logger.error(f"API call failed to response:{response}")
            raise ValueError("Api call failed")
        return response

    def map_expiry_index(self,expiry_index,unique_expiry):
        if 0<=expiry_index <len(unique_expiry):
            return unique_expiry[expiry_index]
        else:
            raise ValueError("Invalid expiry index provided")
    def get_data_for_single_script(self,exchange,name,call_type):
        data={
            "symbol":f"{exchange}:{name}",
            "ohlcv_flag": "1"

        }
        dataquote={
            "symbols":f"{exchange}:{name}"
        }
        try:
            if call_type.lower() == "quote":
                response=self.fyers.quote(data=dataquote)
                self._handle_response(response)
                return response['d']['v']
            else:
                response=self.fyers.depth(data=data)
                if response['s']=="ok":
                    if call_type.lower()=="ohlc":
                        return{call: response['d'][f'{exchange}:{name}'][call] for call in ('o','h','l','c')}
                    else:
                         return response['d'][f'{exchange}:{name}'][call_type]
        except Exception as e:
            self.logger.error(f"failed to get data for script {name}: {e} ")
            raise

    def place_order(self,order_type,exchange,symbol,transaction_type,quantity,product_type,trigger_price=0):
        try:
            get_order_type=lambda ot:{"limit":1,"market":2,"stoporder":3,"Stoplimit":4}.get(ot)
            order_type=get_order_type(order_type)
            if transaction_type.upper()=="BUY":
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
            response=self.fyers.place_order(data=data)
            self.logger.info(f"order place with id:{response['id']}")
            return response['id']
        except Exception as e:
            self.logger.error(F"faild to place order :{e}")
            raise

    def get_order_details(self):
        try:
            response=self.fyers.orderbook()
            if response['s'] !="ok":
                return "please check Fyers Api log for details"
            length=len(response['orderBook'])

            response=response['orderBook'][length-1]
            status=response['status']
            get_status=lambda st:{1:"Canceled",2:"Traded/Filled",3:"NOt Used Currently",4:"Transit",5:"Rejected",6:"Pending",7:"Expired"}.get(st)
            status=get_status(status)
            return response['orderDateTime'],response['tradedPrice'],status
        except Exception as e:
            self.logger.error(f"Failed to get order details:{e}")
            raise



    def get_atm(self,ltp,underlying,expiry,script_type):

       try:
            required_df=self.df[self.df['underlying']==underlying]
            expiry=self.map_expiry_index(expiry,sorted(required_df['expiry_epoch'].unique()))
            required_df=required_df[(required_df['expiry_epoch']==expiry )&(required_df['option_type']==script_type.upper())]
            if required_df.empty:
                return "No matching data for the given expiry or script_Type"
            required_df=required_df.sort_values(by='strike_price')
            required_df['diff']=abs(required_df['strike_price']-ltp)
            atm=required_df.loc[required_df['diff'].idxmin()]
            return atm['trading_symbol']
       except Exception as e:
            self.logger.error(f"failed to get atm option:{e}")
            raise






    def get_itm(self,ltp,underlying,expiry,multiplier,script_type):
        try:
            required_df = self.df[self.df['underlying'] == underlying]
            expiry = self.map_expiry_index(expiry, sorted(required_df['expiry_epoch'].unique()))

            required_df = required_df[(required_df['expiry_epoch'] == expiry) & (required_df['option_type'] == script_type.upper())]
            if required_df.empty:
                return "No matching data for the given expiry and script_Type"
            required_df=required_df.sort_values(by="strike_price")

            if script_type.upper()=='CE':
                itm=required_df[required_df['strike_price']<=ltp]
            else:
                itm=required_df[required_df['strike_price']>=ltp]
            if itm.empty:
                return "No ITM option Found"
            itm_Mul=itm.iloc[-multiplier] if len(itm)>=multiplier else itm.iloc[-1]

            return itm_Mul['trading_symbol']
        except Exception as e:
            self.logger.error(f"faild to get itm option: {e}")

    def get_otm(self,ltp,underlying,expiry,multiplier,script_type):
        try:
            required_df = self.df[self.df['underlying'] == underlying]
            expiry = self.map_expiry_index(expiry, sorted(required_df['expiry_epoch'].unique()))

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

    def get_expiries(self,scripname,exchange,expiry_type):
        try:
            data={
                "symbol":f"{exchange}:{scripname}",
                "strikecount":2,
                "timestamp": ""}
            response=self.fyers.optionchain(data=data)
            self._handle_response(response)


            expiry=response['data']

            expiry_dates=expiry['expiryData']
            group_expiry=defaultdict(list)
            for item in expiry_dates:
                date=datetime.strptime(item['date'],"%d-%m-%Y")
                month_year=date.strftime("%m-%Y")
                group_expiry[month_year].append(item)

            sorted_group_expiry={ge:group_expiry[ge] for ge in sorted(group_expiry)}

            month_count={
                "one":1,
                "two":2,
                "three":3,
                "four":4,
                "all":len(sorted_group_expiry)
            }.get(expiry_type,len(sorted_group_expiry))
            filter_expiry=[]
            for i,(month,data) in enumerate(sorted_group_expiry.items()):
                if i< month_count:
                    filter_expiry.extend(data)

            dates=[item['date'] for item  in  filter_expiry ]
            return dates
        except Exception as e:
            self.logger.error(f"failed to get expiry dates : {e}")


