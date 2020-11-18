from ska.log_transactions import transaction
import logging
import json
import functools

def identify_with_id(name:str,arg_name:str):
    def wrapper(func):
        @functools.wraps(func)
        def wrap(obj,*args,**kwargs):
            if args: argin = args[0]
            elif kwargs: argin = kwargs[arg_name]
            else: raise ValueError("no arguments provided for wrapping with transaction ids")
            try: parameters = json.loads(argin)
            except Exception:
                logging.warning('unable to use transaction id as not able to parse input arguments into a dictionary')
                return func(obj,argin)
            with transaction(name, parameters,logger=obj.logger) as transaction_id:
                obj.transaction_id = transaction_id
                return func(obj,argin)
        return wrap
    return wrapper