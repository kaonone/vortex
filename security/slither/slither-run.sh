rm -rf build/*
npx truffle compile
rm -f build/contracts/BasisVault.json build/contracts/BasisStrategy.json
slither . --config-file ./security/slither/slither-config.json  || true