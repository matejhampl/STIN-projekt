import pytest
import json
import datetime
from app.views import update_balance, update_transactions, get_balance, get_transactions

def test_update_balance(tmp_path, monkeypatch):
    # Set up temporary files
    balance_file = tmp_path / "balance_test.json"
    balance_file.write_text(json.dumps({}))

    exchange_rate_data = {"01.01.2023": {"USD": {"amount": 1, "rate": 20}, "CZK": {"amount": 1, "rate": 1}}}
    date_to_use = "01.01.2023"

    # Temporarily change the behavior of the get_exchange_rate() and get_date_to_use() functions
    monkeypatch.setattr("app.views.get_exchange_rate", lambda: exchange_rate_data)
    monkeypatch.setattr("app.views.get_date_to_use", lambda: date_to_use)

    user_email = "user_email@example.com"

    # Test adding positive amount
    msg, currency, amount = update_balance(user_email, 100, "USD", balance_file)
    with open(balance_file, "r") as file:
        all_balances = json.load(file)
    assert all_balances[user_email]["USD"] == 100
    assert msg == ""
    assert currency == "USD"
    assert amount == 100

    # Test subtracting an amount that is available in the balance
    msg, currency, amount = update_balance(user_email, -50, "USD", balance_file)
    with open(balance_file, "r") as file:
        all_balances = json.load(file)
    assert all_balances[user_email]["USD"] == 50
    assert msg == ""
    assert currency == "USD"
    assert amount == -50

    # Test subtracting an amount that is not available in the balance, but available in CZK

        # Test subtracting an amount that is not available in the balance and not available in CZK
    all_balances[user_email]["CZK"] = 0
    with open(balance_file, "w") as file:
        json.dump(all_balances, file)
    msg, currency, amount = update_balance(user_email, -10000, "USD", balance_file)
    with open(balance_file, "r") as file:
        all_balances = json.load(file)
    assert all_balances[user_email]["USD"] == 50
    assert all_balances[user_email]["CZK"] == 0
    assert msg == "Not enough funds."
    assert currency == "USD"
    assert amount == -10000

def test_update_transactions(tmp_path):
    transactions_file = tmp_path / "transactions_test.json"
    transactions_file.write_text('{}')

    user_email = "user_email@example.com"
    update_transactions(user_email, 100, "USD", transactions_file)
    transactions = get_transactions(user_email, transactions_file)
    last_transaction = transactions[-1]
    today = datetime.datetime.now().strftime("%d.%m.%Y")
    assert today in last_transaction
    assert last_transaction[today]["USD"] == "+100.00"
=======
from app.views import get_date_to_use, get_exchange_rate, save_exchange_rate

def test_get_date_to_use():
    # weekend
    weekend = datetime.datetime(2023, 3, 25) # saturday
    expected_date_weekend = "24.03.2023" # nearest friday
    assert get_date_to_use(weekend) == expected_date_weekend
    # weekday
    weekday = datetime.datetime(2023, 3, 22) # tuesday
    expected_date_weekday = "22.03.2023" # same day
    assert get_date_to_use(weekday) == expected_date_weekday

def test_get_exchange_rate(tmp_path):
    test_file = tmp_path / "exchange_rates_test.json"
    get_exchange_rate(test_file)
    
    assert test_file.exists()
    
    with open(test_file, "r") as file:
        exchange_rates = json.load(file)
    
    date_to_use = get_date_to_use()
    assert date_to_use in exchange_rates

def test_save_exchange_rate(tmp_path):
    test_file = tmp_path / "exchange_rates_test.json"
    test_date = "25.03.2023"
    test_data = {}
    
    save_exchange_rate(test_date, test_data, test_file)
    assert test_file.exists()
    
    with open(test_file, "r") as file:
        data = json.load(file)
    assert data
    
    assert test_date in data
    assert data[test_date]
