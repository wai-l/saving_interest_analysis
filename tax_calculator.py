import numpy as np
import pandas as pd
from tax_utility import get_psa, get_tax_brackets, pa_start_rate, pa_upper_limit

def main(): 
    '''
    the main function here is for manual testing purpose
    '''
    salary = float(input("Enter your annual salary: "))
    non_isa_saving_interest = float(input("Enter your non-ISA saving interest earned: "))

    print(f"Salary: £{salary}")
    print(f"Non-ISA Saving Interest: £{non_isa_saving_interest}")
    print("------------------------------")
    print(f'Personal allowance: £{get_personal_allowance(salary)}')
    print(f'Personal saving allowance: £{get_taxable_saving_details(salary, non_isa_saving_interest)["psa"]}')
    # print(f'Total income tax: £{calculate_income_tax(salary, non_isa_saving_interest)}')
    # print(f'Income tax from salary: £{calculate_income_tax(salary)}')
    # print(f'Tax from saving interest: £{tax_from_saving_interest(salary, non_isa_saving_interest)}')
    # print(f'Taxable saving details: {get_taxable_saving_details(salary, non_isa_saving_interest)}')
    print("------------------------------")
    # for i in calculate_income_tax(salary, non_isa_saving_interest).items():
        # print(f"{i[0]}: {i[1]}")
    income_tax_details = calculate_income_tax(salary, non_isa_saving_interest)

    print(f"Total tax: £{income_tax_details['total_tax']}")
    print(f"Tax from salary: £{income_tax_details['tax_non_saving_income']}")
    print(f"Tax from saving interest: £{income_tax_details['tax_saving_interest']}")
    print("------------------------------")
    print("Income tax details: ")
    print(income_tax_details['tax_breakdown'])


    # return {'tax_breakdown': bracket_details_df, 
    #         'total_tax': bracket_details_df['tax'].sum(), 
    #         'tax_non_saving_income': bracket_details_df['tax_non_saving_income'].sum(), 
    #         'tax_saving_intereset': bracket_details_df['tax_saving_interest'].sum()
    #         }
    
def get_personal_allowance(non_savings_income): 
    '''
    return pa base on non-saving income
    this function is used in the 'get_taxable_saving_details' function
    '''
    pa_start_rate_limit = pa_start_rate()
    pa_upper_limit_rate = pa_upper_limit()
    if non_savings_income > pa_upper_limit_rate: 
        pa = 0
    else: 
        pa = min(pa_upper_limit_rate - non_savings_income, pa_start_rate_limit)
    return pa
    
def get_taxable_saving_details(non_saving_income, non_isa_saving_interest=0): 
    '''
    get the taxable saving interest based on non_saving_income and non_isa_saving_interest
    use function - get_personal_allowance
    used by - calculate_income_tax
    '''
    non_saving_income = float(non_saving_income)
    non_isa_saving_interest = float(non_isa_saving_interest)

    total_non_isa_income = non_saving_income + non_isa_saving_interest

    # get parameters
    tax_brackets = get_tax_brackets()
    tax_brackets = tax_brackets.to_dict(orient="records")
    psa_brackets = get_psa()
    
    # find out which tax bracket the non_isa_income is in
    if total_non_isa_income <= 0:  
        tax_bracket = 'personal_allowance'

    for bracket in tax_brackets:
        lower = bracket['lower_limit']
        upper = bracket['upper_limit']
        if lower < total_non_isa_income <= upper:
            tax_bracket =  bracket['bracket']
    
    # calculate deducatable from pa and psa

    personal_allowance = get_personal_allowance(non_saving_income)
    psa = psa_brackets[tax_bracket]

    taxable_saving_interest = max(
        non_isa_saving_interest - personal_allowance - psa, 
        0
        )

    return {'tax_bracket': tax_bracket, 
            'personal_allowance': personal_allowance,
            'psa': psa, 
            'taxable_saving_interest': taxable_saving_interest
            }



def calculate_income_tax(non_saving_income, non_isa_saving_interest=0): 
    '''
    This function return a panda dataframe for breakdown of taxaxable income and tax by tax bracket and income type (salary and non_isa saving interest). 

    The calculationthis does not include dividend currently. 

    parameter: 
    - non_saving_income (usually means salary, can also be pension)
    - non_isa_saving_interest (any interest gain from a non isa account within the tax year)

    return: 
    - bracket_details_df: a panda dataframe that breakdown the taxable income and tax by tax bracket and income type
    - total_tax: total payable tax
    - tax_non_saving_income': tax from input field 'non_saving_income'
    - tax_saving_interest: tax from input field 'non_isa_saving_interest'
    '''
    non_saving_income = float(non_saving_income)
    non_isa_saving_interest = float(non_isa_saving_interest)

    # get variables from other functions
    pa = get_taxable_saving_details(non_saving_income, non_isa_saving_interest)['personal_allowance']
    psa = get_taxable_saving_details(non_saving_income, non_isa_saving_interest)['psa']

    # psa not deducted yet as it's included in evaluating the tax bracket
    taxable_saving_interest = max(non_isa_saving_interest - pa, 0)
    taxable_income = non_saving_income + taxable_saving_interest

    # get parameters
    tax_bracket = get_tax_brackets()
    
    # calcaulate tax from taxable income, psa not deducted yet
    bracket_details = []

    # loop through the brackets to get the taxable income and tax per bracket
    for _, row in tax_bracket.iterrows():
        bracket = row['bracket']
        lower = row['lower_limit']
        upper = row['upper_limit']
        rate = row['rate']
        
        # If income is less than the lower limit, skip this bracket
        if taxable_income <= lower:
            bracket_taxable_income = 0.0
            bracket_taxable_non_saving_income = 0.0
            bracket_taxable_saving_interest = 0.0
    
        # Taxable amount in this bracket
        else: 
            bracket_taxable_income = min(taxable_income, upper) - lower
            bracket_taxable_non_saving_income = max(min(non_saving_income, upper) - lower, 0)
            bracket_taxable_saving_interest = bracket_taxable_income - bracket_taxable_non_saving_income
        
        bracket_details.append({
            'bracket': bracket, 
            'lower_limit': lower,
            'upper_limit': upper,
            'rate': rate,
            'taxable': bracket_taxable_income, 
            'taxable_non_saving_income': bracket_taxable_non_saving_income, 
            'taxable_saving_interest': bracket_taxable_saving_interest, 
        })

    # loop through each bracket and their taxable income and deducte the psa
    remaining_psa = psa

    for bracket in bracket_details: 
        # if the rate is 0 - it is the personal allowance bracket, so tax doesn't apply
        # if remaining psa is 0 - we have used the full psa and start being taxed for saving interest
        # this replicate the logic: the psa deduction start from when you first start getting tax for your saving interest
        if bracket['rate'] == 0.00 or remaining_psa <= 0: 
            bracket['tax'] = bracket['taxable'] * bracket['rate'] 
            bracket['tax_non_saving_income'] = bracket['taxable_non_saving_income'] * bracket['rate']
            bracket['tax_saving_interest'] = bracket['taxable_saving_interest'] * bracket['rate']
        else: 
            psa_deduction = min(remaining_psa, bracket['taxable_saving_interest'])
            bracket['taxable'] -= psa_deduction
            bracket['taxable_saving_interest'] -= psa_deduction
            remaining_psa -= psa_deduction

            bracket['tax'] = bracket['taxable'] * bracket['rate'] 
            bracket['tax_non_saving_income'] = bracket['taxable_non_saving_income'] * bracket['rate']
            bracket['tax_saving_interest'] = bracket['taxable_saving_interest'] * bracket['rate']
    

    bracket_details_df = pd.DataFrame(bracket_details)

    return {'tax_breakdown': bracket_details_df, 
            'total_tax': bracket_details_df['tax'].sum(), 
            'tax_non_saving_income': bracket_details_df['tax_non_saving_income'].sum(), 
            'tax_saving_interest': bracket_details_df['tax_saving_interest'].sum()
            }


if __name__ == "__main__":
    main()
