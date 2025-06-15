import numpy as np
import pandas as pd

def main(): 
    # income = input("Enter your annual income: ")
    # print(saving_allowance(income))

    incomes = [12569, 12570, 12571, 13000, 17570, 17571]

    for income in incomes: 
        saving_allowance_ = saving_allowance(income)
        print(f'Income: {income}, Saving Allowance: {saving_allowance_}')

def saving_allowance(income): 
    annual_income = int(income) if isinstance(income, (int, float)) else float(income)

    # calculate if there's any personal allowance base on income
    # if income is below 12570, personal allowance is 5000
    # if income is above 12570, personal allowance is any amount above 12570 subtracted from 5000
    # if income is above 17570, personal allowance is 0
    start_rate_for_saving_limit = 5000
    pa_upper_limit = 17570
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
    personal_saving_allowance = {
        'personal_allowance': 1000, 
        'basic_rate': 1000, 
        'higher_rate': 500, 
        'additional_rate': 0
    }

    # tax brackets base on annnual income
    tax_brackets = [
        {'bracket': 'personal_allowance', 'lower_limit': 0, 'upper_limit': 12570, 'rate': 0.00},
        {'bracket': 'basic_rate', 'lower_limit': 12570, 'upper_limit': 50270, 'rate': 0.20},
        {'bracket': 'higher_rate', 'lower_limit': 50270, 'upper_limit': 125140, 'rate': 0.40},
        {'bracket': 'additional_rate', 'lower_limit': 125140, 'upper_limit': np.inf, 'rate': 0.45}
        ]

    tax_brackets = pd.DataFrame(tax_brackets)

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
    
def tax_from_saving_interest(income, interest_earned, tax_free_interest=None):
    """
    Calculate the tax owed from interest earned on savings.
    
    Parameters:
    - income: Annual income of the individual.
    - interest_earned: Total interest earned from savings.
    - tax_free_interest: Optional; the amount of interest that is tax-free.
    
    Returns:
    - Tax owed from the interest earned.
    """
    pass

if __name__ == "__main__":
    main()