# UK Saving Interest Analysis
A Python tool for analyzing savings account interest rates, tax implications, and effective returns in the UK. 

## ✅ Use Case
Find the best saving account at this moment based on the user's income and saving account balance, so they can decide where to put their money.

## ❌ Limitations
- The accounts data is hardcoded in the script, and may not be up-to-date. 
- The account details do not fully cover all the varaibles in the real world (e.g. variable interest rate, bonus interest rate, account limit, etc. ). At this point the it only covers the basic interest rate, monthly fees, and ISA status.
- The tax rules are based on UK tax system, last updated in July 2025. 

## 📂 Project Structure
```
    saving_interest_analysis/
    │── main.py                # Entry point for running the analysis  
    │── tax_calculator.py      # Core functions for tax calculation  
    │── tax_utility.py         # Tax information including tax brackets and tax rates  
    │── test_tax_calculator.py # Unit tests for tax calculations  
    │── requirements.txt       # Python dependencies
    │── README.md              # Project documentation (this file)
```
## 🚀 Features
- Calculate true AER (Annual Equivalent Rate) after tax and fees base on tax brackets
- Support for ISA (tax-free savings) and non-ISA accounts
- Compare multiple savings accounts and recommend the best one
- Simulate balances across different ranges and find optimal accounts based with varying saving accounts balance
- Modular tax calculation with test coverage

## 🛠 Requirements
- Python 3.9+
- Dependencies:
```pip install -r requirements.txt```

## ▶️ How to use
1. Clone the repository and navigate to the project directory.
2. Install dependencies
3.  Make sure the tax rules in the ```tax_utility.py``` are up-to-date.
4.  Modify the accounts data in ```main.py``` if needed.
5.  Run the main script to perform an interest analysis

## 📌 Future roadmap
- Add saving account varibles (e.g. variable interest rate, bonus interest rate, account limit, etc.)
- Support multiple tax years
- Frontend interface
- More comprehensive test coverage

## ⚠️ Disclaimer
This application is for educational and research purposes only. It is not intended as financial advice. Always do your own research and consult with financial professionals before making investment decisions.

## License
This project is licensed under the MIT License. See the LICENSE file for details.
