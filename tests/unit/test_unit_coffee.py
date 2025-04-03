from eth_utils import to_wei
import boa
import random
from tests.conftest import SEND_VALUE

RANDOM_USER = boa.env.generate_address("non-owner")
TEN_FUNDERS_ADDRESSES = [boa.env.generate_address(f"funder_{i}") for i in range(10)]
FUNDER_VALUES = [to_wei(random.randint(5, 10), "ether") for i in range(10)]
TEN_FUNDERS = dict(zip(TEN_FUNDERS_ADDRESSES, FUNDER_VALUES))


def test_price_feed_is_correct(coffee, eth_usd):
    assert coffee.PRICE_FEED() == eth_usd.address


def test_starting_values(coffee, account):
    assert coffee.MINIMUM_USD() == to_wei(5, "ether")
    assert coffee.OWNER() == account.address


def test_fund_fails_without_enough_eth(coffee):
    with boa.reverts():
        coffee.fund()


def test_fund_with_money(coffee, account):
    # Arrange
    boa.env.set_balance(account.address, SEND_VALUE)
    # Act
    coffee.fund(value=SEND_VALUE)
    # Assert
    funder = coffee.funders(0)
    assert funder == account.address
    assert coffee.funder_to_amount_funded(funder) == SEND_VALUE


def test_non_owner_cannot_withdraw(coffee_funded, account):
    with boa.env.prank(RANDOM_USER):
        with boa.reverts("Not the contract owner!"):
            coffee_funded.withdraw()


def test_owner_can_withdraw(coffee_funded):
    with boa.env.prank(coffee_funded.OWNER()):
        coffee_funded.withdraw()
    assert boa.env.get_balance(coffee_funded.address) == 0


def test_ten_funders(coffee):
    boa.env.set_balance(coffee.OWNER(), 0)
    for funder, value in TEN_FUNDERS.items():
        boa.env.set_balance(funder, value)
        with boa.env.prank(funder):
            coffee.fund(value=value)

    with boa.env.prank(coffee.OWNER()):
        coffee.withdraw()

    assert boa.env.get_balance(coffee.address) == 0
    assert boa.env.get_balance(coffee.OWNER()) == sum(TEN_FUNDERS.values())


def test_get_rate(coffee):
    assert coffee.get_eth_to_usd_rate(SEND_VALUE) > 0


def test_default(coffee, account):
    boa.env.set_balance(account.address, SEND_VALUE)
    with boa.env.prank(account.address):
        boa.env.raw_call(to_address=coffee.address, value=SEND_VALUE)

    assert (
        boa.env.get_balance(coffee.address) == SEND_VALUE
    ), f"Values not equal {boa.env.get_balance(coffee.address)} does not equal {SEND_VALUE}"
