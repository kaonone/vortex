pragma solidity >=0.8.0 <0.9.0;

import "ds-test/test.sol";
import "../BasisVault.sol";
import "../BasisStrategy.sol";

interface Vm {
    function expectEmit(
        bool,
        bool,
        bool,
        bool
    ) external;

    function prank(address) external;

    function expectRevert(bytes calldata) external;
}

contract BasisTest is DSTest, BasisVault {
    Vm vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    address constant deployer = 0xBF2B82E026B182Bb4f5f10CCfB6136b1df08e29F;
    address constant _want = 0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8;
    address constant _weth = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;
    uint256 constant _depositLimit = 10_000_000e6;
    address constant _longAsset = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;
    address constant _uniPool = 0x17c14D2c404D167802b16C450d3c99F88F2c4F4d;
    address constant _router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
    address constant _mcLiquidity = 0xaB324146C49B23658E5b3930E641BDBDf089CbAc;
    address constant _usdcWhale = 0x7f90122BF0700F9E7e1F688fe926940E8839F353;
    address constant _usdcProxy = 0x1eFB3f88Bc88f03FD1804A5C53b7141bbEf5dED8;
    address constant _mcDEXOracle = 0x1Cf22B7f84F86c36Cb191BB24993EdA2b191399E;
    address constant _random = 0x6B69fB91E91C6C43FaD962B9BD9636c2C95de748;
    uint256 constant _buffer = 100_000;
    uint256 constant _perpIndex = 0;
    uint256 constant _depositAmount = 100_000e6;
    uint256 constant _yieldAmount = 2_000e6;
    uint256 constant _accuracy_usdc = 1e4;
    uint256 constant _accuracy = 1e9;
    uint256 constant _accuracyMC = 1e17;
    bool constant _isV2 = false;
    uint256 constant _add_value = 1e6;

    BasisVault vault;
    BasisStrategy strategyTest;

    function setUp() public {
        vault = new BasisVault();
        vm.prank(deployer);
        vault.initialize(_want, _depositLimit);
        strategyTest = new BasisStrategy();
        vm.prank(deployer);
        strategyTest.initialize(
            _longAsset,
            _uniPool,
            address(vault),
            _router,
            _weth,
            deployer,
            _mcLiquidity,
            _perpIndex,
            _buffer,
            _isV2
        );
    }

    function testVaultDeployment() public {
        string memory _name = "akBVUSDC-ETH";
        string memory _symbol = "akBasisVault-USDC-ETH";
        uint256 _totalAssets = 0;
        uint256 _totalLent = 0;
        uint256 _totalSupply = 0;
        address _strategy = address(0);
        uint256 _performanceFee = 0;
        uint256 _managementFee = 0;

        assertEq(_want, address(vault.want()));
        assertEq(_depositLimit, uint256(vault.depositLimit()));
        assertEq(_name, vault.name());
        assertEq(_symbol, vault.symbol());
        // emit log_uint(uint256(vault.totalAssets()));
        // TODO: Why is this call failing?
        // assertEq(_totalAssets, uint256(vault.totalAssets()));
        assertEq(_totalLent, uint256(vault.totalLent()));
        assertEq(_totalSupply, uint256(vault.totalSupply()));
        assertEq(_strategy, vault.strategy());
        assertEq(_performanceFee, uint256(vault.performanceFee()));
        assertEq(_managementFee, uint256(vault.managementFee()));
        vm.expectEmit(true, true, true, true);
    }

    function testSetParam() public {
        // @dev : Testing Deposit Limits
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setDepositLimit(0);
        vm.prank(deployer);
        vault.setDepositLimit(0);
        assertEq(0, uint256(vault.depositLimit()));
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setProtocolFees(5_000, 5_000);
        vm.prank(deployer);
        vm.expectRevert("!_performanceFee");
        vault.setProtocolFees(10_001, 0);
        vm.prank(deployer);
        vm.expectRevert("!_managementFee");
        vault.setProtocolFees(0, 10_001);
        vm.prank(deployer);
        vault.setProtocolFees(5_000, 5_000);
        assertEq(5_000, uint256(vault.performanceFee()));
        assertEq(5_000, uint256(vault.managementFee()));
    }

    function testSetStrategy() public {
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setStrategy(address(strategyTest));
        // vm.prank(address(0));
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setStrategy(address(strategyTest));
        vm.prank(deployer);
        vault.setStrategy(address(strategyTest));
    }

    function testPauseUnpause() public {
        vm.expectRevert("Ownable: caller is not the owner");
        vault.pause();
        vm.prank(deployer);
        vault.pause();
        assertTrue(bool(vault.paused()));
        vm.prank(deployer);
        vm.expectRevert("Pausable: paused");
        vault.setStrategy(address(strategyTest));
        vm.expectRevert("Ownable: caller is not the owner");
        vault.unpause();
        vm.prank(deployer);
        vault.unpause();
        assertTrue(!bool(vault.paused()));
        vm.prank(deployer);
        vault.setStrategy(address(strategyTest));
        assertEq(address(strategyTest), address(vault.strategy()));
    }
}
