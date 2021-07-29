## Ideally, they have one file with the settings for the strat and deployment
## This file would allow them to configure so they can test, deploy and interact with the strategy

BADGER_DEV_MULTISIG = "0xb65cef03b9b89f99517643226d76e286ee999e77"

WANT = "0x6b175474e89094c44da98b954eedeac495271d0f" ## Dai
LP_COMPONENT = "0x028171bca77440897b824ca71d1c56cac55b68a3" ## aDAI
REWARD_TOKEN = "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9" ## AAVE Token

PROTECTED_TOKENS = [WANT, LP_COMPONENT, REWARD_TOKEN]
## Fees in Basis Points
DEFAULT_GOV_PERFORMANCE_FEE = 1000
DEFAULT_PERFORMANCE_FEE = 1000
DEFAULT_WITHDRAWAL_FEE = 75

FEES = [DEFAULT_GOV_PERFORMANCE_FEE, DEFAULT_PERFORMANCE_FEE, DEFAULT_WITHDRAWAL_FEE]