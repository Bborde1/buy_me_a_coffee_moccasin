from moccasin.config import get_active_network


def withdraw():
    active_network = get_active_network()
    # coffee = active_network.manifest_named("buy_me_a_coffee")
    coffee = active_network.get_latest_contract_unchecked("buy_me_a_coffee")
    print(f"Working with contract {coffee.address}")
    coffee.withdraw()


def moccasin_main():
    return withdraw()
