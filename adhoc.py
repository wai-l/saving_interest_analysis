import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from tax_calculator import calculate_income_tax



def get_true_aer(non_saving_income: float, balance: float, monthly_fee: float, aer: float, isa: bool) -> float:
    """
    Calculate the true AER (Annual Equivalent Rate) after tax and fees.
    """
    annual_interest = balance * aer
    if not isa:
        tax_due = calculate_income_tax(non_saving_income, annual_interest)["tax_saving_interest"]
        annual_interest -= tax_due

    annual_fee = monthly_fee * 12
    true_annual_interest = annual_interest - annual_fee
    return true_annual_interest / balance



def prepare_accounts(accounts: list[tuple], current_balance: float, non_saving_income: float) -> pd.DataFrame:
    """
    Convert accounts list into DataFrame with pre-computed returns.
    """
    # Ensure unique account names
    keys = [k for k, _ in accounts]
    if len(keys) != len(set(keys)):
        raise ValueError("Account names must be unique")

    accounts_dict = {k: v for k, v in accounts}

    df = pd.DataFrame.from_dict(accounts_dict, orient="index").reset_index()
    df.columns = ["account", "aer", "monthly_fee", "isa"]

    # Pre-compute metrics
    df["pre_tax_annual_interest"] = df["aer"] * current_balance
    df["true_aer"] = df.apply(
        lambda row: get_true_aer(non_saving_income, current_balance, row["monthly_fee"], row["aer"], row["isa"]), axis=1
    )
    df["saving_interest_tax"] = df.apply(
        lambda row: calculate_income_tax(non_saving_income, current_balance * row["aer"])["tax_saving_interest"], axis=1
    )
    df["true_annual_return"] = (
        current_balance * df["aer"] - df["saving_interest_tax"] - df["monthly_fee"] * 12
    )

    return df


def simulate_balances(accounts: list[tuple], balances: list, non_saving_income: float) -> pd.DataFrame:
    """
    Simulate the best account by balance.
    """
    df_accounts = pd.DataFrame.from_dict(dict(accounts), orient="index").reset_index()
    df_accounts.columns = ["account", "aer", "monthly_fee", "isa"]

    results = []
    for balance in balances:
        best_return = float("-inf")
        best_account = None

        for _, row in df_accounts.iterrows():
            true_aer = get_true_aer(non_saving_income, balance, row["monthly_fee"], row["aer"], row["isa"])
            if true_aer > best_return:
                best_return, best_account = true_aer, row["account"]

        results.append({"balance": balance, "best_account": best_account, "true_aer": best_return})

    return pd.DataFrame(results)


def reshape_returns(accounts: list[tuple], balances: list, non_saving_income: float) -> pd.DataFrame:
    """
    Get long-format returns (for plotting).
    """
    df_accounts = pd.DataFrame.from_dict(dict(accounts), orient="index").reset_index()
    df_accounts.columns = ["account", "aer", "monthly_fee", "isa"]

    records = []
    for balance in balances:
        for _, row in df_accounts.iterrows():
            records.append({
                "balance": balance,
                "account": row["account"],
                "true_aer": get_true_aer(non_saving_income, balance, row["monthly_fee"], row["aer"], row["isa"])
            })
    return pd.DataFrame(records)


def main():
    non_saving_income = 32000
    current_balance = 25000

    accounts = [
        ("monzo", {"aer": 0.0325, "monthly_fee": 0, "isa": False}),
        ("barclays_rainy_day", {"aer": 0.0461, "monthly_fee": 5, "isa": False}),
        ("monzo_perks", {"aer": 0.0385, "monthly_fee": 7, "isa": False}),
        ("barclays_1_yr_flexible_cash_isa", {"aer": 0.0385, "monthly_fee": 0, "isa": True}),
    ]

    # 1. Single balance analysis
    df = prepare_accounts(accounts, current_balance, non_saving_income)
    print("=== Accounts at current balance ===")
    print(df.sort_values("true_aer", ascending=False))

    # 2. Multiple balances simulation
    balances = np.arange(1000, 25001, 500)
    best_by_balance = simulate_balances(accounts, balances, non_saving_income)
    print("\n=== Best account by balance range ===")
    print(
        best_by_balance.groupby("best_account")
        .agg(min_balance=("balance", "min"), max_balance=("balance", "max"))
    )

    # 3. Plot returns
    returns_long = reshape_returns(accounts, balances, non_saving_income)
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=returns_long, x="balance", y="true_aer", hue="account", palette="tab10")
    plt.title("True AER by Balance")
    plt.xlabel("Balance (£)")
    plt.ylabel("True AER")
    plt.axhline(0, color="black", linewidth=0.5, linestyle="--")
    plt.grid(True)
    plt.legend(title="Account")
    plt.show()


if __name__ == "__main__":
    main()
