import numpy as np
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def main(): 


    current_balance = 1800

    accounts = [
        ('monzo', {'aer': 0.0325, 'monthly_fee': 0}),
        ('barclays_rainy_day', {'aer': 0.0461, 'monthly_fee': 5}), 
        ('monzo_perks', {'aer': 0.0385, 'monthly_fee': 7})
    ]

    # Check for duplicate keys
    
    keys = [k for k, v in accounts]
    to_set = set(keys)

    if len(keys) != len(to_set):
        raise ValueError('Account names must be unique')
    else: 
        accounts = {k: v for k, v in accounts}

    # Convert to DataFrame
    df = pd.DataFrame.from_dict(accounts, orient='index').reset_index()
    df.columns = ['account', 'aer', 'monthly_fee']
    # if df['account']. != len(df):
    #     raise ValueError('Account names must be unique')

    # get true AER under the current balance, and find the best account
    df['true_aer'] = df.apply(lambda row: get_true_aer(current_balance, row['monthly_fee'], row['aer']), axis=1)

    print(f'With the current balance of £{current_balance}, the best account is: ')
    print(df.loc[df['true_aer'].idxmax(), 'account'])
    print(f"True AER: {df['true_aer'].max():.4%}")
    print('=======================')
    print(f'True AER for each account with balance of £{current_balance}:')
    df['true_aer'] = df['true_aer'].apply(lambda x: f"{x:.4%}")
    print(df.sort_values(by='true_aer', ascending=False))

    # find which account has the highest true AER in different balances 
    balances = np.arange(1000, 5001, 1)
    
    best_account_by_balance = []

    aer_table = df.copy()

    for balance in balances: 
        aer_table['true_aer'] = aer_table.apply(lambda row: get_true_aer(balance, row['monthly_fee'], row['aer']), axis=1)
        best_account = aer_table.loc[aer_table['true_aer'].idxmax(), 'account']
        best_aer = aer_table['true_aer'].max()
        best_account_by_balance.append({'balance': balance, 'best_account': best_account, 'true_aer': best_aer})   

    best_account_by_balance = pd.DataFrame(best_account_by_balance)
    best_account_by_balance['true_aer'] = best_account_by_balance['true_aer'].apply(lambda x: f"{x:.4%}")
    
    print('=======================')
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

    # ploting the true AER by balance for each account        

    return_by_balance = []

    for balance in balances: 
        row = {'balance': balance}
        for account in accounts: 
            row[account] = get_true_aer(balance, 
                                        df[df['account'] == account]['monthly_fee'].values[0],
                                        df[df['account'] == account]['aer'].values[0])
        return_by_balance.append(row)

    return_by_balance = pd.DataFrame(return_by_balance)

    return_by_balance_unpivoted = return_by_balance.melt(id_vars=['balance'],
                                                        var_name='account', 
                                                        value_name='true_aer')

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

def get_true_aer(balance, monthly_fee, aer): 
    annual_interest = balance * aer 
    annual_fee = monthly_fee * 12
    true_annual_interest = annual_interest - annual_fee
    return true_annual_interest / balance

if __name__ == "__main__":
    main()