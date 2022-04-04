.ONESHELL:

install-all:
	$(MAKE) install-venvs
	$(MAKE) install-contracts-deps
	yarn

install-venvs:
	$(MAKE) install-ape-safe-venv
	$(MAKE) install-default-venv

install-default-venv:
	virtualenv venvs/default
	. venvs/default/bin/activate
	pip --require-virtualenv install -r requirements/default.txt
	brownie networks import network-config.yaml true

install-ape-safe-venv:
	virtualenv venvs/ape_safe
	. venvs/ape_safe/bin/activate
	pip --require-virtualenv install -r requirements/ape_safe.txt
	brownie networks import network-config.yaml true

GLOBAL_BROWNIE := $(shell command -v brownie 2> /dev/null)

install-contracts-deps:
ifeq ($(GLOBAL_BROWNIE),)
	. venvs/default/bin/activate
endif
	brownie pm install "Uniswap/uniswap-v3-core@1.0.0"
	brownie pm install "Uniswap/uniswap-v3-periphery@1.0.0"
	brownie pm install "OpenZeppelin/openzeppelin-contracts@4.0.0"
	brownie pm install "OpenZeppelin/openzeppelin-contracts-upgradeable@4.0.0"
	brownie pm clone "Uniswap/uniswap-v3-core@1.0.0"
	brownie pm clone "Uniswap/uniswap-v3-periphery@1.0.0"
	brownie pm clone "OpenZeppelin/openzeppelin-contracts@4.0.0"
	brownie pm clone "OpenZeppelin/openzeppelin-contracts-upgradeable@4.0.0"

switch-to-ganache-cli:
	npm remove -g ganache
	npm install -g ganache-cli@6.12.2

switch-to-ganache:
	npm remove -g ganache-cli
	npm install -g ganache@7.0.3

clean:
	rm -rf build hardhat OpenZeppelin Uniswap node_modules venv venvs flattened