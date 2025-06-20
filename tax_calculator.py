import numpy as np
import pandas as pd
from tax_utility import get_psa, get_tax_brackets, psa_start_rate, psa_upper_limit

def main(): 
    # income = input("Enter your annual income: ")
    # print(saving_allowance(income))

    incomes = [12569, 12570, 12571, 13000, 17570, 17571]

    # for income in incomes: 
    #     saving_allowance_ = saving_allowance(income)
    #     print(f'Income: {income}, Saving Allowance: {saving_allowance_}')

    # for income in incomes: 
    #     interest_earned = 1000
    #     # tax_owed = tax_from_saving_interest(income, interest_earned)
        # print(f'Income: {income}, Interest Earned: {interest_earned}')

    # Example usage:
    income = 27655.68 # if pension is NPA (taken before tax, input annual income - pension; else just input annual income)
    print(f"Income: £{income}")
    print(f"Tax Due: £{calculate_income_tax(income):.2f}")
    print(f'income by month: £{(income- calculate_income_tax(income))/12:.2f}')


def saving_allowance(income): 
    annual_income = int(income) if isinstance(income, (int, float)) else float(income)

    # calculate if there's any personal allowance base on income
    # if income is below 12570, personal allowance is 5000
    # if income is above 12570, personal allowance is any amount above 12570 subtracted from 5000
    # if income is above 17570, personal allowance is 0
    start_rate_for_saving_limit = psa_start_rate() # 5000
    pa_upper_limit = psa_upper_limit() # 17570
    pa_lower_limit = pa_upper_limit - start_rate_for_saving_limit

    # logic to determine how much is deducted from the £5000 personal allowance based on income
    if annual_income > pa_upper_limit:
        start_rate_of_saving = 0
    elif annual_income > pa_lower_limit:
        start_rate_of_saving = start_rate_for_saving_limit - (annual_income - pa_lower_limit)
    else: 
        start_rate_of_saving = start_rate_for_saving_limit

    # set personal allowance as the same as basic rate
    # as anyone with income below 12570, for any amount that they exceed 12570 + 5000, will still have the personal allowance of 1000 under basic rate
    personal_saving_allowance = get_psa()

    # tax brackets base on annnual income
    tax_brackets = get_tax_brackets()

    if annual_income == 0: 
        current_tax_bracket = 'personal_allowance'
    else: 
        current_tax_bracket = tax_brackets[(annual_income > tax_brackets['lower_limit']) & (annual_income <= tax_brackets['upper_limit'])]

        if current_tax_bracket.empty:
            raise ValueError("No applicable tax bracket found for the given income.")
            
        current_tax_bracket = current_tax_bracket['bracket'].values[0]

    # now based on the current tax bracket, calculate how much interest you can earn without paying tax
    # if current_tax_bracket == 'personal_allowance':
    #     tax_free_interest = personal_saving_allowance['personal_allowance']
    # else: 
    tax_free_interest = personal_saving_allowance[current_tax_bracket] + start_rate_of_saving

    return tax_free_interest

    # if you donn't have any personal income, you have a personal saving allowance of 5000
    # on top of it, you still have the personal allownace of 12570 with tax rate of 0%
    # so if you earn interest on saving up to 17570 without any other income, you won't pay any tax on it
    # if you earn interest on saving above 17570, you will pay tax on any amount that exceeds 17570 based on the tax breackets
    
def tax_from_saving_interest(income, interest_earned, saving_allowance, tax_free_interest=0):
    """
    Calculate the tax owed from interest earned on savings.
    
    Parameters:
    - income: Annual income of the individual.
    - interest_earned: Total interest earned from savings.
    - saving_allowance: The tax-free interest allowance based on the individual's income. (from saving_allowance function)
    - tax_free_interest: Optional; the amount of interest that is tax-free.
    
    Returns:
    - Tax owed from the interest earned.
    """
    if not all(isinstance(x, (int, float)) for x in [income, interest_earned, saving_allowance, tax_free_interest]): 
        raise TypeError("All inputs must be numeric (int or float).")

    taxable_interest = interest_earned - tax_free_interest - saving_allowance
    if taxable_interest < 0:
        taxable_interest = 0

    taxable_income = income + taxable_interest

    tax_brackets = get_tax_brackets()

    return taxable_income

def calculate_income_tax(income):
    brackets = get_tax_brackets()
    tax_due = 0.0

    for _, row in brackets.iterrows():
        lower = row['lower_limit']
        upper = row['upper_limit']
        rate = row['rate']
        
        # If income is less than the lower limit, skip this bracket
        if income <= lower:
            continue
        
        # Taxable amount in this bracket
        taxable = min(income, upper) - lower
        bracket_tax = taxable * rate
        tax_due += bracket_tax

    return tax_due

if __name__ == "__main__":
    main()