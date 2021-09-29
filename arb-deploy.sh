#bin/sh

git clone https://github.com/shuklaayush/hardhat.git
cd hardhat
git checkout fix/arbitrum
yarn --frozen-lockfile
yarn build
cd packages/hardhat-core
yarn pack
cd ../../../

ls 
pwd 
yarn add ./hardhat/packages/hardhat-core/hardhat-v2.6.2.tgz -W