import pandas as pd
import pytest
# from pandas.testing import assert_frame_equal
from tax_calculator import get_personal_allowance, calculate_income_tax

# personal allowance tests
def test_get_personal_allowance_full_5000(): 
    expected = 5000
    assert get_personal_allowance(0) == expected
    assert get_personal_allowance(1000) == expected
    assert get_personal_allowance(12570) == expected

def test_get_personal_allowance_partial_5000():
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