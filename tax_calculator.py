import numpy as np
import pandas as pd
from tax_utility import get_psa, get_tax_brackets, pa_start_rate, pa_upper_limit

def main(): 
    # for manual testing the functions in this script

    # salary = 14500 # if pension is NPA (taken before tax, input annual income - pension; else just input annual income)
    # interest_earned = 2500
    # isa_interest_earned = 0
    # taxable_interest = interest_earned - isa_interest_earned
    # total_taxable_income = salary + taxable_interest

    # print(f"Income: £{salary}")
    # print('Tax from salary')
    # print(f"Tax Due: £{calculate_income_tax(salary):.2f}")
    # print(f"Tax Due per month: £{calculate_income_tax(salary)/12:.2f}")
    # print('=====================================================')
    
    # print(f"Interest earned: £{interest_earned}")
    # print(f"Taxable interest: £{taxable_interest}")
    # print(f"Saving allowance (excl ISA): £{get_saving_allowance(salary)}")
    # print(f"Tax from saving interest: £{tax_from_saving_interest(salary, interest_earned, isa_interest_earned)}")
    # # print(f"total tax payable: £{calculate_income_tax(salary+interest_earned)}")

    # # total tax payable
    # print(f"Total tax payable: £{calculate_income_tax(total_taxable_income)}")

    # personal allowance
    salary = float(input("Enter your annual salary: "))
    non_isa_saving_interest = float(input("Enter your non-ISA saving interest earned: "))

    print(f"Salary: £{salary}")
    print(f"Non-ISA Saving Interest: £{non_isa_saving_interest}")
    print("------------------------------")
    print(f'Personal allowance: £{get_personal_allowance(salary)}')
    print(f'Total income tax: £{calculate_income_tax(salary, non_isa_saving_interest)}')
    print(f'Income tax from salary: £{calculate_income_tax(salary)}')
    print(f'Tax from saving interest: £{tax_from_saving_interest(salary, non_isa_saving_interest)}')
    print(f'Taxable saving interest: {taxable_saving_interest(salary, non_isa_saving_interest)}')
    print("------------------------------")
    print(f'testing resulst: {testing(salary, non_isa_saving_interest)}')
    
def get_personal_allowance(non_savings_income): 
    pa_start_rate_limit = pa_start_rate()
    pa_upper_limit_rate = pa_upper_limit()
    if non_savings_income > pa_upper_limit_rate: 
        pa = 0
    else: 
        pa = min(pa_upper_limit_rate - non_savings_income, pa_start_rate_limit)
    return pa
    
def taxable_saving_interest(non_saving_income, non_isa_saving_interest=0): 
    '''
    get the taxable saving interest based on non_saving_income and non_isa_saving_interest
    '''
    non_saving_income = float(non_saving_income)
    non_isa_saving_interest = float(non_isa_saving_interest)

    total_non_isa_income = non_saving_income + non_isa_saving_interest

    # get parameters
    tax_brackets = get_tax_brackets()
    tax_brackets = tax_brackets.to_dict(orient="records")
    psa_brackets = get_psa()
    
    # find out which tax bracket the non_saving_income is in
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
    non_saving_income = float(non_saving_income)
    non_isa_saving_interest = float(non_isa_saving_interest)

    taxable_interest = taxable_saving_interest(non_saving_income, non_isa_saving_interest)['taxable_saving_interest']

    taxable_income = non_saving_income + taxable_interest



    # get parameters
    tax_bracket = get_tax_brackets()
    
    # calcaulate tax from taxable income
    tax_due = 0.0

    for _, row in tax_bracket.iterrows():
        lower = row['lower_limit']
        upper = row['upper_limit']
        rate = row['rate']
        
        # If income is less than the lower limit, skip this bracket
        if taxable_income <= lower:
            bracket_tax = 0.0
    
        # Taxable amount in this bracket
        else: 
            taxable = min(taxable_income, upper) - lower
            bracket_tax = taxable * rate

        if bracket_tax < 0: 
            raise ValueError(f"The {row['bracket']} bracket is returning negative tax of {bracket_tax}. ")
        
        tax_due += bracket_tax
    
    return tax_due

def tax_from_saving_interest(salary, non_isa_saving_interest):
    pass
    """
    Calculate the tax owed from interest earned on savings.
    
    Parameters:
    - income: Annual income of the individual.
    - interest_earned: Total interest earned from savings.
    
    Returns:
    - Tax owed from the interest earned.
    """
    if not all(isinstance(x, (int, float)) for x in [salary, non_isa_saving_interest]): 
        raise TypeError("All inputs must be numeric (int or float).")

    tax_from_salary = calculate_income_tax(salary)

    total_income_tax = calculate_income_tax(salary, non_isa_saving_interest)

    tax_from_saving_interest = total_income_tax - tax_from_salary

    return tax_from_saving_interest


def testing(non_saving_income, non_isa_saving_interest=0):

    non_saving_income = float(non_saving_income)
    non_isa_saving_interest = float(non_isa_saving_interest)

    total_non_isa_income = non_saving_income + non_isa_saving_interest

    deductable_interest = taxable_saving_interest(non_saving_income)['personal_allowance'] + taxable_saving_interest(non_saving_income)['psa']

    taxable_income = total_non_isa_income - deductable_interest

    return {
        'non_saving_income': non_saving_income,
        'non_isa_saving_interest': non_isa_saving_interest,
        'total_non_isa_income': total_non_isa_income,
        'deductable_interest': deductable_interest,
        'taxable_income': taxable_income
    }

if __name__ == "__main__":
    main()
