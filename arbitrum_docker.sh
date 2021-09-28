#/bin/sh

# This will build an image with the name "arbitrum_docker", compile the contracts 
# ,add the arbitrum network  and  interactively log in
# TODO mount current directory to enable hot reloading.
# TODO host on docker hub
# ./arb-deploy.sh
# rm -rf hardhat
docker build -t arbitrum_docker . && docker run -it arbitrum_docker /bin/sh