# Security tools usage

Akropolis Delphi package provides abilities to run security tools upon its code for continuous development.
Tools included:
* [Slither](https://github.com/crytic/slither)
* [Echidna](https://github.com/crytic/echidna)
* [Manticore](https://github.com/trailofbits/manticore)

Before launching any of the utilities, verify that you have installed all dependencies for the project:

```bash
npm install
```

## 1. Flattener

The project includes script for flattening Delphi smart contracts. Script is built with the usage of Brownie framework APIs.

Run:
```bash
npm run sec:flatten
```

Verify, that flattened files has appeared in the the *flattened* directory.

## 2. Slither

### Prerequisites
The first step is to install Slither (if it is not installed yet). Full recommendations for installation can be found on [Slither's GitHub](https://github.com/crytic/slither).

Dependency: [python3](https://www.python.org/downloads/release/python-368/) version 3.6 or greater, python3-dev.

To install the tool run the command:

```bash
pip3 install slither-analyzer
```

### Launch

1. Flatten necessary contracts:

```bash
npm run sec:flatten
```

2. Run script for Slither launching:

```bash
npm run sec:slither
```

Detectors' settings can be corrected in [Slither's config file](slither/slither-config.json)

## 3. Echidna

Test contracts for Echidna with defined properties to be tested are located in [contracts/test/echidna](contracts/test/echidna) directory.
[Configuration file](echidna/echidna_conf.yaml) contains necessary settings.

### Prerequisites

To start the analysis you need to load *echidna* binary file in the root directory of the project:
Run the script:

```bash
npm run sec:load-echidna
```

Also, be awared, that Echidna requires Slither to be installed as well.
The main restirction: Echidna does not work correctly on Windows.

1. Flatten necessary echidna contracts:

```bash
npm run sec:flatten-echidna
```

2. Compile all contracts:

```bash
npm run compile
```

3. Run the analyzer:

```bash
npm run sec:echidna
```

## 4. Manticore

### Prerequisites

Install Manticore:

```
pip3 install "manticore[native]"
```

### Launch

1. Flatten necessary contracts:

```bash
npm run sec:flatten
```

2. Compile the flattened files:

```bash
npx truffle compile
```

3. Run the analyzer

```
manticore flattened/VaultSavings.sol --contract VaultSavings
```