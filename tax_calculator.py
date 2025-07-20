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
    print(f'Personal saving allowance: £{get_taxable_saving_details(salary, non_isa_saving_interest)["psa"]}')
    # print(f'Total income tax: £{calculate_income_tax(salary, non_isa_saving_interest)}')
    # print(f'Income tax from salary: £{calculate_income_tax(salary)}')
    # print(f'Tax from saving interest: £{tax_from_saving_interest(salary, non_isa_saving_interest)}')
    # print(f'Taxable saving details: {get_taxable_saving_details(salary, non_isa_saving_interest)}')
    print("------------------------------")
    # for i in calculate_income_tax(salary, non_isa_saving_interest).items():
        # print(f"{i[0]}: {i[1]}")
    income_tax_df = calculate_income_tax(salary, non_isa_saving_interest)

    print(f"Total tax: £{income_tax_df['tax'].sum()}")
    print(f"Tax from salary: £{income_tax_df['tax_non_saving_income'].sum()}")
    print(f"Tax from saving interest: £{income_tax_df['tax_saving_interest'].sum()}")
    print("------------------------------")
    print("Income tax details: ")
    print(income_tax_df)
    
def get_personal_allowance(non_savings_income): 
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
    non_saving_income = float(non_saving_income) #49270
    non_isa_saving_interest = float(non_isa_saving_interest) #1010

    pa = get_taxable_saving_details(non_saving_income, non_isa_saving_interest)['personal_allowance'] #0
    psa = get_taxable_saving_details(non_saving_income, non_isa_saving_interest)['psa'] #500

    # psa not deducted yet as it's included in evaluating the tax bracket
    taxable_saving_interest = max(non_isa_saving_interest - pa, 0) #1010
    taxable_income = non_saving_income + taxable_saving_interest #1010+49270 = 50280

    # get parameters
    tax_bracket = get_tax_brackets()
    
    # calcaulate tax from taxable income, psa not deducted yet
    # tax_due = 0.0
    bracket_details = []
    # remaining_taxable_income = taxable_income
    # remaining_non_saving_income = non_saving_income
    # remaining_taxable_saving_interest = taxable_saving_interest

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
            bracket_tax_total = 0.0
            bracket_tax_non_saving_income = 0.0
            bracket_tax_saving_interest = 0.0
    
        # Taxable amount in this bracket
        else: 
            bracket_taxable_income = min(taxable_income, upper) - lower
            bracket_taxable_non_saving_income = max(min(non_saving_income, upper) - lower, 0)
            bracket_taxable_saving_interest = bracket_taxable_income - bracket_taxable_non_saving_income
            
            bracket_tax_total = bracket_taxable_income * rate
            bracket_tax_non_saving_income = bracket_taxable_non_saving_income * rate if bracket_taxable_non_saving_income > 0 else 0.0
            bracket_tax_saving_interest = bracket_taxable_saving_interest * rate if bracket_taxable_saving_interest > 0 else 0.0

        
        bracket_details.append({
            'bracket': bracket, 
            'lower_limit': lower,
            'upper_limit': upper,
            'rate': rate,
            'taxable': bracket_taxable_income, 
            'taxable_non_saving_income': bracket_taxable_non_saving_income, 
            'taxable_saving_interest': bracket_taxable_saving_interest, 
            # 'tax': bracket_tax_total,
            # 'tax_non_saving_income': bracket_tax_non_saving_income,
            # 'tax_saving_interest': bracket_tax_saving_interest
        })

    # bracket_details_df = pd.DataFrame(bracket_details)

    remaining_psa = psa

    for bracket in bracket_details: 
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
    # bracket_details_df = bracket_details_df.fillna(0)
        # tax_due = bracket_details_df['tax'].sum()

        # if bracket_tax < 0: 
        #     raise ValueError(f"The {row['bracket']} bracket is returning negative tax of {bracket_tax}. ")
        # 
        # tax_due += bracket_tax

    # return tax_due
    # return {'taxable_saving_interest': taxable_saving_interest,
            # 'taxable_income (before psa deduction)': taxable_income,
            # 'tax_bracket': taxable_income_tax_bracket,
            # 'tax_before_psa': tax_before_psa,
            # 'tax_due': tax_due, 
            # 'psa': psa,
            # 'psa_deduction': psa_deduction,
            # 'taxed_psa_bracket': taxed_psa_bracket, 
            # 'psa_tax_deduction': psa_tax_deduction,
            # 'tax_rate_psa': tax_rate_psa
            # }
    return bracket_details_df

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

    deductable_interest = get_taxable_saving_details(non_saving_income)['personal_allowance'] + get_taxable_saving_details(non_saving_income)['psa']

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
