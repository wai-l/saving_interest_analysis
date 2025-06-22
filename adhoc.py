import pandas as pd

def main(): 
    print(calculate_income_tax_split(35000, 5000))

def get_tax_brackets():
    return pd.DataFrame([
        {"bracket": "personal_allowance", "lower_limit": 0, "upper_limit": 12570, "rate": 0.00},
        {"bracket": "basic_rate", "lower_limit": 12570, "upper_limit": 50270, "rate": 0.20},
        {"bracket": "higher_rate", "lower_limit": 50270, "upper_limit": 125140, "rate": 0.40},
        {"bracket": "additional_rate", "lower_limit": 125140, "upper_limit": float('inf'), "rate": 0.45}
    ])

def calculate_income_tax_split(non_savings_income, savings_interest):
    brackets = get_tax_brackets()
    total_income = non_savings_income + savings_interest
    personal_allowance = 12570
    remaining_pa = max(0, personal_allowance - non_savings_income)
    
    # Apply remaining personal allowance to savings interest
    tax_free_savings = min(remaining_pa, savings_interest)
    taxable_savings = savings_interest - tax_free_savings

    # Apply starting rate for savings
    starting_rate_limit = 5000
    if non_savings_income < personal_allowance:
        starting_rate_available = starting_rate_limit
    elif non_savings_income < personal_allowance + starting_rate_limit:
        starting_rate_available = personal_allowance + starting_rate_limit - non_savings_income
    else:
        starting_rate_available = 0

    starting_rate_used = min(taxable_savings, starting_rate_available)
    taxable_savings -= starting_rate_used

    # Apply PSA (assume basic rate taxpayer for now)
    psa = 1000 if total_income <= 50270 else 500 if total_income <= 125140 else 0
    psa_used = min(taxable_savings, psa)
    taxable_savings -= psa_used

    # Tax salary (non-savings income)
    tax_due = 0
    for _, row in brackets.iterrows():
        lower = row['lower_limit']
        upper = row['upper_limit']
        rate = row['rate']

        # Non-savings income
        if non_savings_income > lower:
            taxable_amount = min(non_savings_income, upper) - lower
            tax_due += taxable_amount * rate

        # Savings income (taxable portion only)
        if taxable_savings > 0:
            if total_income > lower:
                bracket_range = min(total_income, upper) - lower
                savings_in_this_band = min(taxable_savings, bracket_range)
                tax_due += savings_in_this_band * rate
                taxable_savings -= savings_in_this_band

    return round(tax_due, 2)

if __name__ == "__main__": 
    main()