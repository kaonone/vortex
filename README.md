# Vortex
Vortex is a protocol that leverage the funding rate from a perpetual protocol and the fees from a Uniswap v3 position in order to achieve superior returns.

For more on this please see [Vortex Description](https://docs.google.com/document/u/1/d/1pU-ORN8N2z-U6BjOJRtOa2KEJgqdzrut45aq8O-plaA/edit?usp=sharing) and [Uni v3 ALM](https://docs.google.com/document/d/1IIK2xUQMWHrkthN0GlPCh3TPwchzi0Xi5BY6pLR1qnU/edit) .

## Development Instructions

* You will need Python 3.8 and >=Node.js 10.x
* Install the necessary dependencies (brownie 1.16.3, ganache-cli - latest)

```
cd basis
pip install -r requirements-dev.txt
npm install
```
* To run the arbitrum tests get an infura id that is compatible with arbitrum:
```
export WEB3_INFURA_PROJECT_ID=<YOUR ID>
```
* To run the bsc tests get a moralis id:
```
export MORALIS_PROJECT_ID=<YOUR ID>
```
* import the necessary networks in your brownie configuration
```
brownie import network-config.yaml
```
* Next you will need to install a brownie compatible version of hardhat in order to use arbitrum properly, to do this you will need to run the arb-deploy.sh bash script in this directory.

* To run the arbitrum tests, "-s" will provide print outputs which this test suite uses to visualise yield:
```
brownie test -s
```
To run the bsc tests
```
brownie test -s --network=bsc-main-fork
```
* Optional: if you run into bugs surrounding openzepellin imports you may have to run:
```
npm run clone-packages
```
## Requirements

* **Delta Neutrality** : The Strategy **MUST** create take opposing positions so as to achieve a delta neutral position .
* **Compounding**: The Basis Strategy and / or Uni v3 strategies **SHOULD** auto-compound.
* **Isolation**: The Basis Strategy and Active Liquidity Manager **MUST** be two separate products capable of been deployed independently.

## System Architecture 

## System Architecture (Labels and descriptions TBC)

![UniSwap ALM](images/Basis%202.0.png)

## Docs


## User Stories 

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
