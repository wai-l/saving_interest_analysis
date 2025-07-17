import pandas as pd
import pytest
# from pandas.testing import assert_frame_equal
from tax_calculator import get_personal_allowance, calculate_income_tax, tax_from_saving_interest

# personal allowance tests
def test_get_personal_allowance_full_5000(): 
    expected = 5000
    assert get_personal_allowance(0) == expected
    assert get_personal_allowance(1000) == expected
    assert get_personal_allowance(12570) == expected

def test_get_personal_allowance_partial_5000():
    assert get_personal_allowance(12570.01) == 4999.99
    assert get_personal_allowance(12571) == 4999
    assert get_personal_allowance(17569) == 1
    assert get_personal_allowance(14500) == 3070 # 5000 - (14500-12570)

def test_get_personal_allowance_0(): 
    expected = 0
    assert get_personal_allowance(17570) == expected
    assert get_personal_allowance(20000) == expected
    assert get_personal_allowance(30000) == expected

# income tax tests
def test_calculate_income_tax_0(): 
    assert calculate_income_tax(0) == 0
    assert calculate_income_tax(1000) == 0
    assert calculate_income_tax(12570) == 0

def test_calculate_income_tax_basic_rate(): 
    # basic rate is 20% for income between 12570 and 50270
    assert round(calculate_income_tax(12570.01), 3) == 0.002
    assert calculate_income_tax(12571) == 0.20
    assert calculate_income_tax(15000) == 486 #0.20 * (15000 - 12570)
    assert calculate_income_tax(20000) == 1486 #0.20 * (20000 - 12570)
    assert calculate_income_tax(50270) == 7540 #0.20 * (50270 - 12570)

def test_calculate_income_tax_higher_rate():
    # higher rate is 40% for income between 50270 and 125140
    assert calculate_income_tax(50271) == 7540.4 #0.40 * (50271 - 50270) + 0.20 * (50270 - 12570)
    assert calculate_income_tax(60000) == 11432 #0.40 * (60000 - 50270) + 0.20 * (50270 - 12570)
    assert calculate_income_tax(125140) == 37488 #0.40 * (125140 - 50270) + 0.20 * (50270 - 12570)

def test_calculate_income_tax_additional_rate():
    # additional rate is 45% for income above 125140
    assert calculate_income_tax(125141) == 37488.45 #0.45 * (125141 - 125140) + 0.40 * (125140 - 50270) + 0.20 * (50270 - 12570)
    assert calculate_income_tax(150000) == 48675 #0.45 * (150000 - 125140) + 0.40 * (125140 - 50270) + 0.20 * (50270 - 12570)
    assert calculate_income_tax(200000) == 71175 #0.45 * (200000 - 125140) + 0.40 * (125140 - 50270) + 0.20 * (50270 - 12570)

# income tax tests with savings interest
## to be action
# saving interest tax tests
def test_tax_from_saving_interest_0(): 
    assert tax_from_saving_interest(0, 0) == 0
    # any non-saving income with no saving income should return 0 tax from saving interest
    assert tax_from_saving_interest(1000, 0) == 0
    assert tax_from_saving_interest(12570, 0) == 0
    assert tax_from_saving_interest(50270, 0) == 0
    assert tax_from_saving_interest(125140, 0) == 0
    # anyone does not exceed their pa and psa should return 0 tax from saving interest
    assert tax_from_saving_interest(0, 17570) == 0
    assert tax_from_saving_interest(1000, 17570) == 0
    assert tax_from_saving_interest(12569, 5000) == 0 # 12570 or 12569? 
    assert tax_from_saving_interest(12569, 6000) == 0 # 12570 or 12569? 
    # to be continued with more scenarios  with income but no taxable saving interest

# scenario testings taken from moneysavingexpert.com
# https://www.moneysavingexpert.com/savings/tax-free-savings/
def test_scenario_1(): 
    '''
    Chris: Earns £14,500 from work, has £2,500 of savings income

    Chris will pay £386 in tax, all on his income from work. This is because he earns £1,930 more than his personal tax allowance of £12,570. 
    However, all his savings interest will be tax-free, as it's covered by the starting savings rate.
    As Chris earns more than £12,570, his income from work starts to eat in to his £5,000 starting savings rate allowance. 
    He loses £1 of starting savings allowance for every £1 he earns over his personal allowance, so he's left with £3,070 (£5,000 to £1,930) of his starting savings allowance.
    As this £3,070 more than covers his £2,500 interest, he doesn't owe any tax on it.
    '''
    assert calculate_income_tax(14500, 2500) == 386
    assert calculate_income_tax(14500) == 386
    assert tax_from_saving_interest(14500, 2500) == 0

def test_tax_from_saving_interest_scenario_2(): 
    '''
    Cheryl: No income from work, has £20,000 of savings income

    In this scenario, Cheryl will need to pay tax of just £286. As she has no earned income, the savings interest is mostly covered by a combination of allowances:
    - Personal allowance - the first £12,570 is tax-free
    - Starting savings rate - the next £5,000 is tax-free, so now £17,570 of the interest income is taxed at 0%
    - Personal savings allowance - means the next £1,000 is tax-free, so £18,570 is taxed at 0%.
    This leaves Cheryl with £1,430 of savings income which she will need to pay tax on. As she has no other income, this will be charged at the basic 20% rate, so she'll pay £286 in tax. 
    '''
    assert calculate_income_tax(0, 20000) == 286
    assert calculate_income_tax(0) == 0
    assert tax_from_saving_interest(0, 20000) == 286

def test_tax_from_saving_interest_scenario_3(): 
    '''
    Hannah: Earns £35,000 from work, has £5,000 of savings income

    Hannah will pay tax of £800 on her savings interest.
    The first £12,570 of her income from work is tax free, but she'll pay basic-rate 20% tax on the amount above that. 
    As she earns more than £17,570, there's no starting rate for savings available to her.
    However, as a basic-rate taxpayer, she does get a personal savings allowance of £1,000, which covers some of her interest. 
    However, the remaining interest of £4,000 will be taxed at 20%, meaning she'll pay £800 to HMRC, on top of the tax she pays on her salary 
    (though, as we're MSE, we'd suggest she shelters some of her savings in an ISA, legally cutting her tax bill). 
    '''
    assert tax_from_saving_interest(35000, 5000) == 800


# get more scenario testing from this: 
# https://blog.moneysavingexpert.com/2016/02/the-new-personal-savings-allowance-means-some-people-will-be-better-off-earning-less-interest/
# modified to suit the 2025 tax bucket
def test_tax_from_saving_interest_scenario_4(): 
    '''
    Near the limit but not over it

    Income from work: £49270
    Interest from savings accounts: £990
    Total income: £50,260 - so less than the higher-rate threshold
    Size of PSA: £1,000
    Total amount of interest earned after tax: £990 as all your interest is covered by the PSA

    In this scenario all of your savings interest would be tax-free.
    '''
    assert calculate_income_tax(49270, 990) == 7340
    assert calculate_income_tax(49270) == 7340
    assert tax_from_saving_interest(49270, 990) == 0

def test_tax_from_saving_interest_scenario_5(): 
    '''
    You earn £20 more savings interest, but take home LESS

    Income from work: £49,270
    Interest from savings accounts: £1,010
    Total income: £50,280 - so you are a higher-rate taxpayer
    Size of PSA: £500
    Total amount of interest earned after tax: £906 (£500 tax-free, £500 taxed at 20% and £10 taxed at 40%)

    Therefore, bizarrely, the fact you've earned slightly more interest means because a chunk more of it is taxed you actually end up taking home less. 
    You would actually have been slightly better off to have earned £10 less interest.

    A similar situation will occur for those at the brink of hitting the £150,000 earnings barrier where you become a top 45% rate taxpayer.
    In this scenario all of your savings interest would be tax-free.
    '''
    assert calculate_income_tax(49270, 1010) == 7444 # 7340 + 104
    assert tax_from_saving_interest(49270, 1010) == 104 # 500 tax-free, 500 taxed at 20%, 10 taxed at 40%
    # this didn't pass, which means the tax_from_saving_interest/ function needs to be fixed
