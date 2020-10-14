import functools
import json
from typing import Any, Dict, Union
from ska.log_transactions import transaction

def identify_with_id(name:str,arg_name:str):
    def wrapper(func):
        @functools.wraps(func)
        def wrap(obj,*args,**kwargs):
            if args:
                argin = args[0]
            elif kwargs:
                argin = kwargs[arg_name]
            parameters = json.loads(argin)
            with transaction(name, parameters,logger=obj.logger) as transaction_id:
                obj.transaction_id = transaction_id
                return func(obj,argin)
        return wrap
    return wrapper

def inject_id(obj,data:Dict)->Dict:
    id = getattr(obj,"transaction_id",None)
    if id:
        data['transaction_id'] = id
    return data
    

def update_with_id(obj,parameters:Any)->Union[Dict,str]:
    if isinstance(parameters,str):
        parameters = json.loads(parameters)
        inject_id(obj,parameters)
        return json.dumps(parameters)
    elif isinstance(parameters,dict):
        inject_id(obj,parameters)
        return parameters
    else: raise Exception(f'arg {parameters} is of not type dict or string')

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
        return wrap
    return wrapper