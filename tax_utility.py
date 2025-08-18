import numpy as np
import pandas as pd

# personal allowance
def pa_start_rate(): 
    return 5000

def pa_upper_limit(): 
    return 17570

# personal saving allowance; separate from personal allowance
def get_psa(): 
    personal_saving_allowance = {
        'personal_allowance': 0, 
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

'''
we can potentially reconfigure this to something like this when the tax rate changes; courtesy of chat gpt
# tax_config.py

class TaxConfigBase:
    """Shared base for all tax years unless overridden."""
    PERSONAL_ALLOWANCE = 12_570
    TAX_BRACKETS = [
        {"bracket": "personal_allowance", "lower_limit": 0, "upper_limit": 12_570, "rate": 0.00},
        {"bracket": "basic_rate", "lower_limit": 12_570, "upper_limit": 50_270, "rate": 0.20},
        {"bracket": "higher_rate", "lower_limit": 50_270, "upper_limit": 125_140, "rate": 0.40},
        {"bracket": "additional_rate", "lower_limit": 125_140, "upper_limit": float("inf"), "rate": 0.45}
    ]
    SAVINGS_START_RATE = 5_000
    PERSONAL_SAVINGS_ALLOWANCE = {
        'personal_allowance': 0, 
        'basic_rate': 1_000,
        'higher_rate': 500,
        'additional_rate': 0
    }


class TaxConfig2024(TaxConfigBase):
    """Inherits from base, override if needed."""
    pass


class TaxConfig2027(TaxConfigBase):
    """Override just the updated rules here."""
    PERSONAL_ALLOWANCE = 13_000
    TAX_BRACKETS = [
        {"bracket": "personal_allowance", "lower_limit": 0, "upper_limit": 13_000, "rate": 0.00},
        {"bracket": "basic_rate", "lower_limit": 13_000, "upper_limit": 52_000, "rate": 0.20},
        {"bracket": "higher_rate", "lower_limit": 52_000, "upper_limit": 130_000, "rate": 0.40},
        {"bracket": "additional_rate", "lower_limit": 130_000, "upper_limit": float("inf"), "rate": 0.45}
    ]


def get_tax_config(year: int = 2024):
    """Factory function to return the config for a given year."""
    if year == 2027:
        return TaxConfig2027()
    return TaxConfig2024()  # Default
'''