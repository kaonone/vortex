wget "https://github.com/crytic/echidna/releases/download/v1.6.0/echidna-test-v1.6.0-Ubuntu-18.04.tar.gz"
tar -xf echidna-test-v1.6.0-Ubuntu-18.04.tar.gz
curl -o ./solc -fL https://github.com/ethereum/solidity/releases/download/v0.6.12/solc-static-linux
chmod u+x ./solc
export PATH=.:$PATH
