# Basis 2.0 (WIP)

Basis 2.0 is a protocol that leverage the funding rate from a perpetual protocol and the fees from a Uniswap v3 position in order to achieve superior returns.

For more on this please see [Basis 2.0 Description](https://docs.google.com/document/u/1/d/1pU-ORN8N2z-U6BjOJRtOa2KEJgqdzrut45aq8O-plaA/edit?usp=sharing) and [Uni v3 ALM](https://docs.google.com/document/d/1IIK2xUQMWHrkthN0GlPCh3TPwchzi0Xi5BY6pLR1qnU/edit) .

## Development Instructions

* Install the necessary dependencies (brownie 1.16.3, ganache-cli - latest)
* Get an infura, alchemy and etherscan id:
```
export WEB3_INFURA_PROJECT_ID=<YOUR ID>
export ALCHEMY_PROJECT_ID=<YOUR ID>
export ETHERSCAN_TOKEN=<YOUR ID>
```
* Other arbitrum repo examples (follows the instructions here:https://github.com/shuklaayush/WBTC-WETH-SLP-Arbitrum-Strategy for setting up the hardhat method), https://github.com/jalbrekt85/wBTC-Arbitrum-Strategy, https://github.com/shuklaayush/WETH-Sushi-SLP-Arbitrum-Strategy
* Add the network config for arbitrum
```
cd basis
brownie import network-config.yaml
```
There are a few things to do from here to try and get it to work:
```
To try the Alchemy way:
brownie test tests-mainnet --network=arb-main-fork

To try the Infura way:
brownie test tests-mainnet --network=arbitrum-main-fork

To try the hardhat way (make sure you have done the setup in https://github.com/shuklaayush/WETH-Sushi-SLP-Arbitrum-Strategy):
brownie test tests-mainnet
```

## Requirements

* **Delta Neutrality** : The Strategy **MUST** create take opposing positions so as to achieve a delta neutral position .
* **Compounding**: The Basis Strategy and / or Uni v3 strategies **SHOULD** auto-compound.
* **Isolation**: The Basis Strategy and Active Liquidity Manager **MUST** be two separate products capable of been deployed independently.

## System Architecture (Labels and descriptions TBC)

![UniSwap ALM](images/Basis%202.0.png)

## Smart Contracts

* Basis Contracts //These contract allow users to take earn a funding rate by entering the perpetual trade.
  * Vault // Isolates user funds and is able to administer them to a strategy.
    * State changing methods
      * `deposit(address user uint256 amount0 uint 256 amount1)` // Emits a Deposited Event
      * `withdraw(address user uint256 amount0 uint 256 amount1)` // Emits a Withdrawal Event
      * `collectProtocolFees()` // Collects the protocol fee.
      * `setProtocolFees(uint256 protocolFee)` // Sets the protocol fee
    * Informational Methods // Placeholder for now
      * `calculateShares()`
      * `calculateDebtOutstanding()`
      * `getTotalAmounts()`
  * Strategy
    * State Changing Methods
      * `calculateSplit(uint256 amount ) returns (uint256 amountPerp0 uint256 amountPerp1 uint256 amountLP0 uint256 amountLP1)`
      * `harvest()` // Recycles profits back into the position.
      * `unwind()` // Safely shuts down the strategy 
      * `openPerpPosition(uint256 perpetualIndex, address trader, int256 amountPerp, int256 limitPrice, uint256 deadline, address referrer, uint32 flags)`
      * `closePerpPosition(// Not sure what these parameters are for now)`
      * `openLPPosition(address ALM uint256 amountLP0 uint256 amountLP1)`
      * `closeLPPosition(address ALM bytes32 positionIndex)`
      * `emergencyExit()` // Circuit Breaker ; should be callable by the Governance , Owner (Multisig), and an additional person. Liquidates all the strategies positions even though they are loss making.
      * `pause()` // Circuit Breaker ; should be callable by the Governance , Owner (Multisig), and an additional person. This function might also check the perp state to see if the perp is in emergency mode.
      * `resume()` // Resume Normal operations after pause. should be callable by the Governance , Owner (Multisig), and an additional person.
    * Informational Methods
      * `calculateLimitPrice(uint256 markPrice) returns (uint256 limitPrice)` // calculates the limit price for opening the perp position. 
      * `getFundingRate() returns( uint256 fundingRate )` // Calls Perp.Getter.getPerpetualInfo and returns the fundingRate. Might not be necessary since we can already return the fundingRate from getPerpState()
      * `isFundingRateNegative(fundingRate) returns(bool)`  //Does this matter? In the long run its positive no? I don't think taking the opposite side of the trade would be beneficial in the long run.
      * `getPerpState(uint256 perpetualIndex) returns (PerpetualState state, uint256 fundingRate, address oracle)`
* ALM Contracts : These contracts are responsible for managing LP positions within a range , while minimizing the effects of Impermanent Loss and trading costs.
  * Vault: No changes are necessary with the vault contract contract.
  * Strategy
    * `claimReward(bytes32 merkleRoot address)` // claims the rewards from the SWISE contract. 
    * harvest()

## User Stories (We will complete this tomorrow)

1) As a user , I want to deposit funds into the Basis Vaults so that I can earn market neutral yield.
   * Deposit
   * Deposit to strategy
   * Calculate shares
   * Return shares to user
   * Calculate split
   * Deposit to Perp
   * Deposit to ALM
2) As a user , I want to withdraw funds from the Basis Vaults.
3) As a user, I want to compound my position so that I can accumulate more yield.

## Things to consider

* [Markets can close](https://github.com/mcdexio/mai-protocol-v3/blob/b7846a06969f2eeb61dcdcf6da15acfb19b3c038/contracts/module/TradeModule.sol#L119) 
* [Funding Rate Calculation](https://github.com/mcdexio/mai-protocol-v3/blob/b7846a06969f2eeb61dcdcf6da15acfb19b3c038/contracts/module/PerpetualModule.sol#L300-L324)
* Funding Rate: How much of the funding rate does the trader earn v AMM?

## Resources

* [Mai Protocol v3 Github](https://github.com/mcdexio/mai-protocol-v3/tree/b7846a06969f2eeb61dcdcf6da15acfb19b3c038)
* [Mai v3 Documents][https://docs.mcdex.io/mai-protocol-v3]
* [Hop Protocol](https://github.com/hop-protocol/contracts/blob/master/contracts/bridges/L2_Bridge.sol)
