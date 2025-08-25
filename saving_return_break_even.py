import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from tax_calculator import calculate_income_tax

def main(): 
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
    
    accounts = [
        ('monzo', {'aer': 0.0325, 'monthly_fee': 0, 'isa': False}),
        ('barclays_rainy_day', {'aer': 0.0461, 'monthly_fee': 5, 'isa': False}), 
        ('monzo_perks', {'aer': 0.0385, 'monthly_fee': 7, 'isa': False}), 
        ('barclays_1_yr_flexible_cash_isa', {'aer': 0.0385, 'monthly_fee': 0, 'isa': True})
    ]

    df = get_accounts_df(accounts, current_balance, non_saving_income)

    # 1. find best account under the current balance
    print('=======================')
    print(f'With the current balance of £{current_balance}, the best account is: ')
    print(df.loc[df['true_aer'].idxmax(), 'account'])
    print(f"True AER: {df['true_aer'].max():.4%}")
    print(f'True annual return: £{df.loc[df["true_aer"].idxmax(), "true_annual_return"]:.2f}')
    
    ## tax breakdown for the best account
    print('-----------------------')
    print('Tax breakdown for the best account: ')
    best_account_pre_tax_interest = df.loc[df['true_aer'].idxmax(), 'pre_tax_annual_interest']
    taxable = 0 if df.loc[df['true_aer'].idxmax(), 'isa'] == True else best_account_pre_tax_interest
    tax_details = calculate_income_tax(non_saving_income, taxable)['tax_breakdown']
    print(tax_details)

    ## return all accounts details
    print('-----------------------')
    print('Accounts by True AER: ')
    print(df.sort_values(by='true_aer', ascending=False))
    print('')

    # 2. multiple balance simulation to find the best account by balance
    print('=======================')
    print('Compare accounts by balance range')
    ## select balance range
    lower = input('Enter the lower bound of balance range in £ (default: £1,000): ')
    upper = input('Enter the upper bound of balance range in £ (default: £25,000): ')

    if lower == '': 
        lower = 1000
    else: 
        lower = int(lower)

    if upper == '': 
        upper = 25000+1
    else: 
        upper = int(upper) + 1

    balances = np.arange(lower, upper, 100)
    
    best_account_by_balance = []

    aer_table = df.copy()

    for balance in balances: 
        aer_table['true_aer'] = aer_table.apply(lambda row: get_true_aer(non_saving_income, balance, row['monthly_fee'], row['aer'], row['isa']), axis=1)
        best_account = aer_table.loc[aer_table['true_aer'].idxmax(), 'account']
        best_aer = aer_table['true_aer'].max()
        best_account_by_balance.append({'balance': balance, 'best_account': best_account, 'true_aer': best_aer})   

    best_account_by_balance = pd.DataFrame(best_account_by_balance)
    best_account_by_balance['true_aer'] = best_account_by_balance['true_aer'].apply(lambda x: f"{x:.4%}")
    
    print('-----------------------')
    print('Best account by balance:')
    
    best_account_by_balance_pivot = (
        best_account_by_balance
        .groupby('best_account')
        .agg(minimum_balance=('balance', 'min'),
             maximum_balance=('balance', 'max')
             )
        .reset_index()
        .rename(columns={'balance': 'min_balance', 'balance': 'max_balance'})
        .sort_values('minimum_balance', ascending=True)
    )
    
    print(best_account_by_balance_pivot)

    # # ploting the true AER by balance for each account        

    # return_by_balance = []

    # for balance in balances: 
    #     row = {'balance': balance}
    #     for account in accounts: 
    #         row[account] = get_true_aer(non_saving_income, 
    #                                     balance, 
    #                                     df[df['account'] == account]['monthly_fee'].values[0],
    #                                     df[df['account'] == account]['aer'].values[0], 
    #                                     df[df['account'] == account]['isa'].values[0])
    #     return_by_balance.append(row)

    # return_by_balance = pd.DataFrame(return_by_balance)

    # return_by_balance_unpivoted = return_by_balance.melt(id_vars=['balance'],
    #                                                     var_name='account', 
    #                                                     value_name='true_aer')

    # plt.figure(figsize=(12, 6))
    # sns.lineplot(data=return_by_balance_unpivoted,
    #          x='balance', 
    #          y='true_aer', 
    #          hue='account', 
    #          palette='tab10')
    # plt.title('True AER by Balance for Different Accounts')
    # plt.xlabel('Balance (£)')
    # plt.ylabel('True AER')
    # plt.axhline(0, color='black', linewidth=0.5, linestyle='--')
    # plt.grid(True)
    # plt.legend(title='Account')
    # plt.show()

def get_true_aer(
        non_saving_income: float, balance: float, monthly_fee: float, aer: float, isa: bool
        ) -> float:  
    '''
    Calculate the tru AER after tax and fees. 
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

if __name__ == "__main__":
    main()