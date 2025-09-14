import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from tax_calculator import calculate_income_tax

def main(): 
    '''
    Main function to run the saving interest analysis. 
    1. Get user inputs: non-saving income, current balance
    2. Calculate the best account under the current balance
    3. Simulate the best account by balance range
    4. Plot the true AER by balance for each account

    Variables: 
    - non_saving_income: float, user's non-saving income (e.g., salary, rental income)
    - current_balance: float, user's current saving account balance
    - accounts: list of tuples, each tuple contains account name and a dictionary of account details
        - aer: float, annual equivalent rate (interest rate)
        - monthly_fee: float, monthly fee for the account
        - isa: bool, whether the account is an ISA (tax-free) account
    - lower: int, lower bound of balance range for simulation
    - upper: int, upper bound of balance range for simulation
    - range_step: int, step size for balance range simulation (default: 100)

    True AER calculation:
    1. Calculate annual interest: balance * aer
    2. If not ISA, calculate tax on interest and subtract from annual interest, non_saving_income is used to determine tax rate
    3. Calculate annual fee: monthly_fee * 12
    4. Calculate true annual interest: annual interest - tax - annual fee
    5. Calculate true AER: true annual interest / balance
    6. Return true AER
    '''
    print('Welcome to the UK Saving Interest Analysis Tool!')
    print('This tool helps you find the best saving account based on your income and balance.')
    print('You can compare different accounts and see how taxes and fees affect your returns.')
    print('Let\'s get started!')
    print('')
    # basic user inputs

    non_saving_income = input(
            'Enter your non-saving income (e.g., salary, rental income) in £ (default: £25,000): '
        )

    if non_saving_income == '':
        non_saving_income = 25000
    else: 
        non_saving_income = float(non_saving_income)

    current_balance = input(
            'Enter your saving account balance in £ (default: £5,000): '
        )

    if current_balance == '':
        current_balance = 5000
    else: 
        current_balance = float(current_balance)
    
    if current_balance <= 0: 
        raise ValueError('Current balance must be greater than zero. ')

    # saving accounts info
    accounts = [
        ('monzo', {'aer': 0.03, 'monthly_fee': 0, 'isa': False}),
        ('barclays_rainy_day', {'aer': 0.0428, 'monthly_fee': 5, 'isa': False}), 
        ('monzo_perks', {'aer': 0.035, 'monthly_fee': 7, 'isa': False}), 
        ('barclays_1_yr_flexible_cash_isa', {'aer': 0.037, 'monthly_fee': 0, 'isa': True})
    ]

    df = get_accounts_df(accounts, current_balance, non_saving_income)

    # return reuslts
    ## 1. find best account under the current balance
    print('=======================')
    print('1. Best account under the current balance')
    print(f'With the current balance of £{current_balance}, the best account is: ')
    print(df.loc[df['true_aer'].idxmax(), 'account'])
    print(f"True AER: {df['true_aer'].max():.4%}")
    print(f'True annual return: £{df.loc[df["true_aer"].idxmax(), "true_annual_return"]:.2f}')
    
    ### tax breakdown for the best account
    print('-----------------------')
    print('Tax breakdown for the best account: ')
    best_account_pre_tax_interest = df.loc[df['true_aer'].idxmax(), 'pre_tax_annual_interest']
    taxable = 0 if df.loc[df['true_aer'].idxmax(), 'isa'] == True else best_account_pre_tax_interest
    tax_details = calculate_income_tax(non_saving_income, taxable)['tax_breakdown']
    print(tax_details)

    ### return all accounts details
    print('-----------------------')
    print('Accounts by True AER: ')
    print(df.sort_values(by='true_aer', ascending=False))
    print('')

    ## 2. multiple balance simulation to find the best account by balance
    print('=======================')
    print('2. Compare accounts by balance range')

    continue_script() # ask user if they want to continue to part 2
        
    ### select balance range
    lower = input('Enter the lower bound of balance range in £ (default: £1,000): ')
    upper = input('Enter the upper bound of balance range in £ (default: £5,000): ')
    
    if lower == '': 
        lower = 1000
    else: 
        lower = int(lower)

    if upper == '': 
        upper = 5000+1
    else: 
        upper = int(upper) + 1

    if lower == 0 or upper == 0: 
        raise ValueError('Balance range cannot be zero. ')
    if lower >= upper: 
        raise ValueError('Lower bound must be less than upper bound. ')

    ### calculate the best account by balance
    balance_sim = simulate_balances(accounts, non_saving_income, lower, upper) 

    print(best_acc_by_bal_segment(balance_sim))

    ## 3. ploting the true AER by balance for each account
    print('=======================')
    print('3. Plotting True AER by Balance for Each Account')

    continue_script() # ask user if they want to continue to part 2

    print('Please wait, the plot will be shown on a new window. ')

    ploting_df = reshape_returns(accounts, non_saving_income, lower, upper)
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=ploting_df,
             x='balance', 
             y='true_aer', 
             hue='account', 
             palette='tab10')
    plt.title('True AER by Balance for Different Accounts')
    plt.xlabel('Balance (£)')
    plt.ylabel('True AER')
    plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
    plt.grid(True)
    plt.legend(title='Account')
    plt.show()


def get_true_aer(
        non_saving_income: float, balance: float, monthly_fee: float, aer: float, isa: bool
        ) -> float:  
    '''
    Calculate the true AER after tax and fees. 
    '''

    annual_interest = balance * aer
    if isa == False: 
        tax_due = calculate_income_tax(non_saving_income, annual_interest)['tax_saving_interest']
        annual_interest -= tax_due

    annual_fee = monthly_fee * 12
    true_annual_interest = annual_interest - annual_fee
    return true_annual_interest / balance

def get_accounts_df(
        accounts: list[tuple], 
        current_balance: float, 
        non_saving_income: float
        ) -> pd.DataFrame: 
    '''
    Convert accounts list into DataFrame and calculate the below metrics: 
    - pre_tax_annual_interest (aer * balance)
    - true_aer (after tax and fees)
    - saving_interest_tax (tax on the interest earned based on full income)
    - true_annual_return (annual interest - tax - fees)
    '''
    
    # Check for duplicate keys
    keys = [k for k, v in accounts]
    to_set = set(keys)

    if len(keys) != len(to_set):
        raise ValueError('Account names must be unique. Duplicate names found. ')
    else: 
        accounts = {k: v for k, v in accounts}

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(accounts, orient='index').reset_index()
    df.columns = ['account', 'aer', 'monthly_fee', 'isa']
    
    # get true AER under the current balance and other metrics
    df['pre_tax_annual_interest'] = df['aer'] * current_balance
    df['true_aer'] = df.apply(lambda row: get_true_aer(non_saving_income, current_balance, row['monthly_fee'], row['aer'], row['isa']), axis=1)
    df['saving_interest_tax'] = df.apply(lambda row: calculate_income_tax(non_saving_income, current_balance * row['aer'])['tax_saving_interest'], axis=1)
    df['true_annual_return'] = df.apply(lambda row: (current_balance * row['aer']) - row['saving_interest_tax'] - (row['monthly_fee'] * 12), axis=1)
    
    return df

def simulate_balances(
        accounts: list[tuple],
        non_saving_income: float,
        lower: int, 
        upper: int, 
        range_step: int = 100
): 
    '''
    Simulate the best account by balance.
    '''

    balances = np.arange(lower, upper, range_step)
    
    aer_table = pd.DataFrame.from_dict(dict(accounts), orient="index").reset_index()
    aer_table.columns = ["account", "aer", "monthly_fee", "isa"]

    results = []
    for balance in balances: 
        best_return = float('-inf') # set to negative infinity
        best_account = None

        for _, row in aer_table.iterrows(): 
            true_aer = get_true_aer(
                non_saving_income, balance, 
                monthly_fee=row['monthly_fee'],
                aer=row['aer'], 
                isa=row['isa']
            )
            if true_aer > best_return: 
                best_return = true_aer
                best_account = row['account']

        results.append(
            {'balance': balance, 'best_account': best_account, 'true_aer': best_return}
        )
    return pd.DataFrame(results)

def best_acc_by_bal_segment(balance_sim: pd.DataFrame) -> pd.DataFrame: 
    '''
    Take the balance simulation result dataframe, iterate through from lowest to higheset balance. 
    Create a segment table by getting the min and max balance for each segment. 

    If an account appears is the best account for multiple segments, it will be shown as multiple rows.
    '''
    
    segments = []
    prev_account = None
    segment_start = None
    start_aer = None
    prev_balance = None
    prev_aer = None

    balance_sim = balance_sim.sort_values(by='balance').reset_index(drop=True)

    for _, row in balance_sim.iterrows(): 
        # if the account changes, we have reached the end of a segment, so we can record that last segment
        if row['best_account'] != prev_account: 
            if prev_account is not None: 
                segments.append({
                    'account': prev_account, 
                    'min_balance': segment_start, 
                    'min_bal_true_aer': start_aer, 
                    'max_balance': prev_balance, 
                    'max_bal_true_aer': prev_aer
                })
            
            # after recording the last segment, start writing new segment
            segment_start = row['balance']
            start_aer = row['true_aer']

        # these are to record the last row's data, so when the acc change, we will use these to write the last segment data
        prev_balance = row['balance']
        prev_aer = row['true_aer']
        prev_account = row['best_account']

    # after the loop, we need to record the last segment
    segments.append({
        'account': prev_account, 
        'min_balance': segment_start, 
        'min_bal_true_aer': start_aer, 
        'max_balance': prev_balance, 
        'max_bal_true_aer': prev_aer
    })



    
    balance_segment = pd.DataFrame(segments)
        
    return balance_segment

def reshape_returns(
        accounts: list[tuple], 
        non_saving_income: float, 
        lower: int, 
        upper: int, 
        range_step: int = 100
        ) -> pd.DataFrame:
    '''
    Get long-format returns for plotting. 
    Instead of finding the right account by balance, this function returns the true AER for each account by balance.
    '''

    df_accounts = pd.DataFrame.from_dict(dict(accounts), orient='index').reset_index()
    df_accounts.columns = ['account', 'aer', 'monthly_fee', 'isa']

    balances = np.arange(lower, upper, range_step)

    records = []
    for balance in balances: 
        for _, row in df_accounts.iterrows(): 
            records.append({
                'balance': balance,
                'account': row['account'],
                'true_aer': get_true_aer(
                    non_saving_income, 
                    balance, 
                    row['monthly_fee'], 
                    row['aer'], 
                    row['isa']
                    )
            })
    return pd.DataFrame(records)

def continue_script(): 
    cont = input('Do you want to continue? (y/n): ').strip().lower()
    while True: 
        if cont == 'y': 
            return True
        elif cont == 'n': 
            sys.exit('Exiting the program. ')
        else: 
            cont = input('Invalid input. Please enter y or n: ')

if __name__ == "__main__":
    main()