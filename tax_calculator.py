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
    # print(f'Total income tax: £{calculate_income_tax(salary, non_isa_saving_interest)}')
    # print(f'Income tax from salary: £{calculate_income_tax(salary)}')
    # print(f'Tax from saving interest: £{tax_from_saving_interest(salary, non_isa_saving_interest)}')
    # print(f'Taxable saving details: {get_taxable_saving_details(salary, non_isa_saving_interest)}')
    print("------------------------------")
    for i in calculate_income_tax(salary, non_isa_saving_interest).items():
        print(f"{i[0]}: {i[1]}")
    # print(calculate_income_tax(salary, non_isa_saving_interest))
    
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
    tax_due = 0.0
    # bracket_details = []

    for _, row in tax_bracket.iterrows():
        # bracket = row['bracket']
        lower = row['lower_limit']
        upper = row['upper_limit']
        rate = row['rate']
        
        # If income is less than the lower limit, skip this bracket
        if taxable_income <= lower:
            # taxable = 0.0
            # bracket_taxable_non_saving_income = 0.0
            # bracket_taxable_saving_interest = 0.0
            bracket_tax = 0.0
            # bracket_tax_for_non_saving_income = 0.0
            # bracket_tax_for_saving_interest = 0.0
    
        # Taxable amount in this bracket
        else: 
            taxable = min(taxable_income, upper) - lower
            # taxable_non_saving_income = max(min(non_saving_income, upper) - lower, 0)
            # bracket_taxable_saving_interest = taxable - taxable_non_saving_income
            
            bracket_tax = taxable * rate
            # bracket_tax_for_non_saving_income = taxable_non_saving_income * rate if taxable_non_saving_income > 0 else 0.0
            # bracket_tax_for_saving_interest = bracket_taxable_saving_interest * rate if bracket_taxable_saving_interest > 0 else 0.0

        
        # bracket_details.append({
        #     'bracket': bracket,
        #     'rate': rate,
        #     'taxable': taxable, 
        #     'taxable_non_saving_income': taxable_non_saving_income, 
        #     'taxable_saving_interest': taxable_saving_interest, 
        #     'tax': bracket_tax,
        #     'tax_non_saving_income': bracket_tax_for_non_saving_income,
        #     'tax_saving_interest': bracket_tax_for_saving_interest
        # })

        # bracket_details_df = pd.DataFrame(bracket_details)
        # tax_due = bracket_details_df['tax'].sum()

        # if bracket_tax < 0: 
        #     raise ValueError(f"The {row['bracket']} bracket is returning negative tax of {bracket_tax}. ")
        # 
        tax_due += bracket_tax
        
    tax_before_psa = tax_due #7544

    # deduct tax from psa
    if taxable_saving_interest > 0: 
    # get tax bracket base on total taxable income
        taxable_income_tax_bracket = get_taxable_saving_details(non_saving_income, non_isa_saving_interest)['tax_bracket'] #higher_rate 0.4
        '''
        get correct tax bracket that was taxed but need psa deduction
        - if the taxable saving interest is in the personal allowance bracket, then nothing need to be deducted (as it's already 0)
        # to do: 
        ## get the bracket of the first taxable saving interest
        ## if the salary is in the personal allowance but saving interest creeps into basic rate, take basic rate as that's the first taxable saving interest
        ## if the salary is in the basic rate but saving interest crreps into higher rate, take the first taxable savintg interest bracket
        ## if the salary and saving interest is both in the same taxable bracket, that that bracket
        ## what if: saving push it to higher rate so the psa is 500, but the 500 was charged partially at basic rate and partially at higher rate?
        '''
        psa = psa # place holder, we already have the psa from get_taxable_saving_details

        # get tax bracket for the first taxable saving interest
        non_saving_income_bracket = get_taxable_saving_details(non_saving_income)['tax_bracket']
        non_saving_income_bracket_upper = tax_bracket[tax_bracket['bracket'] == non_saving_income_bracket]['upper_limit'].values[0]
        if non_saving_income == non_saving_income_bracket_upper: 
            # if the non_saving_income is at the upper limit of the bracket, then the taxable saving interest is in the next bracket
            taxable_income_tax_bracket = tax_bracket[tax_bracket['lower_limit'] > non_saving_income]['bracket'].values[0]
        elif non_saving_income < non_saving_income_bracket_upper: 
            # if the non_saving_income doesn't hit the upper limit, it means the first taxable saving interest is in the same bracket as the non_saving_income
            taxable_income_tax_bracket = non_saving_income_bracket

        if taxable_income_tax_bracket == 'personal_allowance': 
            # if the taxable income is in the personal allowance bracket, then no tax to deduct from psa
            psa_deduction = 0
            tax_rate_psa = 0
            taxed_psa_bracket = 'personal_allowance'
            psa_tax_deduction = 0

        # this is wrong
        tax_bracket_low_lim = tax_bracket[tax_bracket['bracket'] == taxable_income_tax_bracket]['lower_limit'].values[0] #50270; should get 12570 for basic rate
    # deduction_from_non_saving_income = min(non_saving_income - tax_bracket_low_lim, 0)

    # if taxable salary = 35000 and non_isa_saving_interest = 1000; psa_deduction = 1000
    # if taxable salary = 12569 and non_isa_saving_interest = 6000; psa_deduction = 999

        psa_deduction = min(psa, taxable_saving_interest - (tax_bracket_low_lim - non_saving_income)) #should be: min(500, 1010 - (12570 - 49270)) = min(500, 37710) = 500
    
    
    # get tax bracket base on non_saving_income + psa deductable; this is to determine the tax to deduct from the psa
        taxed_psa_bracket = get_taxable_saving_details(non_saving_income, psa_deduction)['tax_bracket'] # basic_rate 0.2
        tax_rate_psa = tax_bracket[tax_bracket['bracket'] == taxed_psa_bracket]['rate'].values[0] #0.2
        psa_tax_deduction = psa_deduction * tax_rate_psa

        tax_due -= psa_tax_deduction

        

        # # to accomodate the cases where the saving interest pushed the tax bracket to basic rate
        # if taxed_psa_bracket == 'personal_allowance' and taxable_income > tax_bracket[tax_bracket['bracket'] == 'personal_allowance']['upper_limit'].values[0]: 
        #     taxed_psa_bracket = 'basic_rate'

        # rate = tax_bracket[tax_bracket['bracket'] == taxed_psa_bracket]['rate'].values[0]

        # psa_deduction = min(psa, taxable_saving_interest)
        
        # tax_due -= psa_deduction * rate

    # if tax_due < 0: 
    #     raise ValueError(f"Tax due is negative: {tax_due}. This should not happen. Please check the input values.")
    
    # return tax_due
    return {'taxable_saving_interest': taxable_saving_interest,
            'taxable_income (before psa deduction)': taxable_income,
            'tax_bracket': taxable_income_tax_bracket,
            'tax_before_psa': tax_before_psa,
            'tax_due': tax_due, 
            'psa': psa,
            'psa_deduction': psa_deduction,
            'taxed_psa_bracket': taxed_psa_bracket, 
            'psa_tax_deduction': psa_tax_deduction,
            'tax_rate_psa': tax_rate_psa
            }
    # return bracket_details_df

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
