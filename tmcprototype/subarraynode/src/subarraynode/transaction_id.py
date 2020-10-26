import functools
import json
import os
from typing import Any, Dict, Union
import logging
from ska.log_transactions import transaction

ENABLE_TRANSACTION_IDS = os.getenv('ENABLE_TRANSACTION_IDS')

def identify_with_id(name:str,arg_name:str):
    def wrapper(func):
        @functools.wraps(func)
        def wrap(obj,*args,**kwargs):
            if ENABLE_TRANSACTION_IDS:
                if args:
                    argin = args[0]
                elif kwargs:
                    argin = kwargs[arg_name]
                else: raise ValueError("no arguments provided for wrapping with transaction ids")
                try:
                    parameters = json.loads(argin)
                except Exception:
                    logging.warning('unable to use transaction id as not able to parse input arguments into a dictionary')
                    return func(obj,argin)
                with transaction(name, parameters,logger=obj.logger) as transaction_id:
                    obj.transaction_id = transaction_id
                    return func(obj,argin)
            else: return func(obj,*args,**kwargs)
        return wrap
    return wrapper

def inject_id(obj,data:Dict)->Dict:
    id = getattr(obj,"transaction_id",None)
    if ENABLE_TRANSACTION_IDS:
        if id:
            data['transaction_id'] = id
    return data
    

def update_with_id(obj,parameters:Any)->Union[Dict,str]:
    if ENABLE_TRANSACTION_IDS:
        if isinstance(parameters,str):
            parameters = json.loads(parameters)
            inject_id(obj,parameters)
            return json.dumps(parameters)
        elif isinstance(parameters,dict):
            inject_id(obj,parameters)
            return parameters
        else: raise Exception(f'arg {parameters} is of not type dict or string')
    return parameters

def inject_with_id(arg_position:int,arg_name:str):
    def wrapper(func):
        @functools.wraps(func)
        def wrap(obj,*args,**kwargs):
            if args:
                updated_args = list(args)
                updated_args[arg_position] = update_with_id(obj,args[arg_position])
                args = tuple(updated_args)
            elif kwargs:
                kwargs[arg_name] = update_with_id(obj,kwargs[arg_name])
            else: raise Exception('arguments not matching wrap function')
            return func(obj,*args,**kwargs)
        if ENABLE_TRANSACTION_IDS:
            return wrap
        else: return func
    return wrapper