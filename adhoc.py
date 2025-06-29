import pandas as pd
import numpy as np

def main(): 
    print(calculate_income_tax_split(35000, 5000))

def pa_start_rate(): 
    return 5000

def pa_upper_limit(): 
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



def calculate_income_tax_split(non_savings_income, savings_interest):
    # brackets = get_tax_brackets()
    # total_income = non_savings_income + savings_interest
    # personal_allowance = 12570
    # remaining_pa = max(0, personal_allowance - non_savings_income)
    
    # # Apply remaining personal allowance to savings interest
    # tax_free_savings = min(remaining_pa, savings_interest)
    # taxable_savings = savings_interest - tax_free_savings

    # # Apply starting rate for savings
    # starting_rate_limit = 5000
    # if non_savings_income < personal_allowance:
    #     starting_rate_available = starting_rate_limit
    # elif non_savings_income < personal_allowance + starting_rate_limit:
    #     starting_rate_available = personal_allowance + starting_rate_limit - non_savings_income
    # else:
    #     starting_rate_available = 0

    # starting_rate_used = min(taxable_savings, starting_rate_available)
    # taxable_savings -= starting_rate_used

    # # Apply PSA (assume basic rate taxpayer for now)
    # psa = 1000 if total_income <= 50270 else 500 if total_income <= 125140 else 0
    # psa_used = min(taxable_savings, psa)
    # taxable_savings -= psa_used

    # # Tax salary (non-savings income)
    # tax_due = 0
    # for _, row in brackets.iterrows():
    #     lower = row['lower_limit']
    #     upper = row['upper_limit']
    #     rate = row['rate']

    #     # Non-savings income
    #     if non_savings_income > lower:
    #         taxable_amount = min(non_savings_income, upper) - lower
    #         tax_due += taxable_amount * rate

    #     # Savings income (taxable portion only)
    #     if taxable_savings > 0:
    #         if total_income > lower:
    #             bracket_range = min(total_income, upper) - lower
    #             savings_in_this_band = min(taxable_savings, bracket_range)
    #             tax_due += savings_in_this_band * rate
    #             taxable_savings -= savings_in_this_band

    # return round(tax_due, 2)

    # get parameters
    tax_bracket = get_tax_brackets()
    pa_start_rate_limit = pa_start_rate()
    pa_upper_limit_rate = pa_upper_limit()
    psa_brackets = get_psa()

    # calcaulate tax from non-savings income
    tax_due = 0.0

    for _, row in tax_bracket.iterrows():
        lower = row['lower_limit']
        upper = row['upper_limit']
        rate = row['rate']
        
        # If income is less than the lower limit, skip this bracket
        if non_savings_income <= lower:
            bracket_tax = 0.0
    
        # Taxable amount in this bracket
        else: 
            taxable = min(non_savings_income, upper) - lower
            bracket_tax = taxable * rate

        if bracket_tax < 0: 
            raise ValueError(f"The {row['bracket']} bracket is returning negative tax of {bracket_tax}. ")
        
        tax_due += bracket_tax

    # calculate if the saving interest is taxable
    
    if non_savings_income > pa_upper_limit_rate: 
        pa = 0
    else: 
        pa = max(pa_upper_limit_rate - non_savings_income, pa_start_rate_limit)
    
    return tax_due, pa


if __name__ == "__main__": 
    main()