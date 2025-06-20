import numpy as np
import pandas as pd

def psa_start_rate(): 
    return 5000

def psa_upper_limit(): 
    return 17570

def get_psa(): 

    # set personal allowance as the same as basic rate
    # as anyone with income below 12570, for any amount that they exceed 12570 + 5000, will still have the personal allowance of 1000 under basic rate
    personal_saving_allowance = {
        'personal_allowance': 1000, 
        'basic_rate': 1000, 
        'higher_rate': 500, 
        'additional_rate': 0
    }

    return personal_saving_allowance


def get_tax_brackets(): 
    # tax brackets base on annnual income
    tax_brackets = [
        {'bracket': 'personal_allowance', 'lower_limit': 0, 'upper_limit': 12570, 'rate': 0.00},
        {'bracket': 'basic_rate', 'lower_limit': 12570, 'upper_limit': 50270, 'rate': 0.20},
        {'bracket': 'higher_rate', 'lower_limit': 50270, 'upper_limit': 125140, 'rate': 0.40},
        {'bracket': 'additional_rate', 'lower_limit': 125140, 'upper_limit': np.inf, 'rate': 0.45}
        ]

    tax_brackets = pd.DataFrame(tax_brackets)

    return tax_brackets

