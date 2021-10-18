brownie pm install "iearn-finance/yearn-vaults@0.3.4" || true
brownie pm install "OpenZeppelin/openzeppelin-contracts@3.3.0" || true
brownie pm install "OpenZeppelin/openzeppelin-contracts-upgradeable@3.3.0" || true

brownie pm clone "iearn-finance/yearn-vaults@0.3.4" || true
brownie pm clone "OpenZeppelin/openzeppelin-contracts@3.3.0" || true
brownie pm clone "OpenZeppelin/openzeppelin-contracts-upgradeable@3.3.0" || true
