# pragma version 0.4.0 

"""
@license MIT 
@title Buy Me A Coffee!
@author You!
@notice This contract is for creating a sample funding contract
"""

from interfaces import AggregatorV3Interface
import get_price_module


# Constants & Immutables
MINIMUM_USD: public(constant(uint256)) = as_wei_value(5, "ether")
PRICE_FEED: public(immutable(AggregatorV3Interface)) # 0x694AA1769357215DE4FAC081bf1f309aDC325306 sepolia
OWNER: public(address)

# Storage
funders: public(DynArray[address, 1000])
funder_to_amount_funded: public(HashMap[address, uint256])

# With constants: 262,853
@deploy
def __init__(price_feed: address):
    PRICE_FEED = AggregatorV3Interface(price_feed)
    self.OWNER = msg.sender

@external
@payable
def fund():
    self._fund()

@internal
@payable
def _fund():
    """Allows users to send $ to this contract
    Have a minimum $ amount to send

    How do we convert the ETH amount to dollars amount?
    """
    usd_value_of_eth: uint256 = get_price_module._get_eth_to_usd_rate(PRICE_FEED, msg.value)
    assert usd_value_of_eth >= MINIMUM_USD, "You must spend more ETH!"
    self.funders.append(msg.sender)
    self.funder_to_amount_funded[msg.sender] += msg.value


@external
def withdraw():
    """Take the money out of the contract, that people sent via the fund function.

    How do we make sure only we can pull the money out?
    """
    assert msg.sender == self.OWNER, "Not the contract owner!"
    raw_call(self.OWNER, b"", value = self.balance)
    # send(OWNER, self.balance)
    # resetting
    for funder: address in self.funders:
        self.funder_to_amount_funded[funder] = 0
    self.funders = []



@external 
@view 
def get_eth_to_usd_rate(eth_amount: uint256) -> uint256:
    return get_price_module._get_eth_to_usd_rate(PRICE_FEED, eth_amount)

@external 
@payable 
def __default__():
    self._fund()