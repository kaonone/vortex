# Credit: https://github.com/banteg/multicall.py/blob/master/multicall/constants.py
from enum import IntEnum


class Network(IntEnum):
    Mainnet = 1
    Kovan = 42
    Rinkeby = 4
    Görli = 5
    xDai = 100
    Forknet = 1337
    BSC = 56
    Polygon = 137
    Hardhat = 31337
    Arbitrum = 42161


MULTICALL_ADDRESSES = {
    Network.Mainnet: "0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441",
    Network.Kovan: "0x2cc8688C5f75E365aaEEb4ea8D6a480405A48D2A",
    Network.Rinkeby: "0x42Ad527de7d4e9d9d011aC45B31D8551f8Fe9821",
    Network.Görli: "0x77dCa2C955b15e9dE4dbBCf1246B4B85b651e50e",
    Network.xDai: "0xb5b692a88BDFc81ca69dcB1d924f59f0413A602a",
    Network.Forknet: "0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441",
    Network.BSC: "0xec8c00da6ce45341fb8c31653b598ca0d8251804",
    Network.Polygon: "0x11ce4B23bD875D7F5C6a31084f55fDe1e9A87507",
    Network.Arbitrum: "0x7A7443F8c577d537f1d8cD4a629d40a3148Dd7ee",
    Network.Hardhat: "0x7A7443F8c577d537f1d8cD4a629d40a3148Dd7ee",
}
