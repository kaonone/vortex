// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.0 <0.9.0;

import "ds-test/test.sol";
import "../contracts/BasisVault.sol";
import "../contracts/BasisStrategy.sol";

interface Vm {
    function expectEmit(
        bool,
        bool,
        bool,
        bool
    ) external;

    function prank(address) external;

    function startPrank(address) external;

    function stopPrank() external;

    function expectRevert(bytes calldata) external;
}

contract BasisTestArb is DSTest {
    Vm vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    address constant deployer = 0xBF2B82E026B182Bb4f5f10CCfB6136b1df08e29F;
    address constant _want = 0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8;
    address constant _weth = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;
    address constant _longAsset = 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1;
    address constant _uniPool = 0x17c14D2c404D167802b16C450d3c99F88F2c4F4d;
    address constant _router = 0xE592427A0AEce92De3Edee1F18E0157C05861564;
    address constant _mcLiquidity = 0xaB324146C49B23658E5b3930E641BDBDf089CbAc;
    address constant _usdcWhale = 0x7f90122BF0700F9E7e1F688fe926940E8839F353;
    address constant _usdcProxy = 0x1eFB3f88Bc88f03FD1804A5C53b7141bbEf5dED8;
    address constant _mcDEXOracle = 0x1Cf22B7f84F86c36Cb191BB24993EdA2b191399E;
    address constant _random = 0x6B69fB91E91C6C43FaD962B9BD9636c2C95de748;
    address[3] _users = [address(10), address(11), address(12)];
    uint256 constant _depositLimit = 10_000_000e6;
    uint256 constant _buffer = 100_000;
    uint256 constant _perpIndex = 0;
    uint256 constant _depositAmount = 100_000e2;
    uint256 constant _yieldAmount = 2_000e6;
    uint256 constant _accuracy_usdc = 1e4;
    uint256 constant _accuracy = 1e9;
    uint256 constant _accuracyMC = 1e17;
    uint256 constant _individualDepositLimit = 10_000_000e2;
    bool constant _isV2 = false;
    uint256 constant _add_value = 1e6;
    uint256 constant _tradeSlippage = 1000e18;

    BasisVault vault;
    BasisStrategy strategy;

    function setUp() public {
        vault = new BasisVault();
        vm.startPrank(deployer);
        vault.initialize(
            _want,
            _depositLimit,
            _individualDepositLimit,
            0,
            2500
        );
        strategy = new BasisStrategy();
        strategy.initialize(
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
        vm.stopPrank();
        // Deploy testnet tokens
        vm.startPrank(_usdcWhale);
        for (uint256 i = 0; i < _users.length; i++) {
            assertEq(IERC20(_want).balanceOf(_users[i]), 0);
            IERC20(_want).transfer(_users[i], _depositAmount);
        }
        vm.stopPrank();
    }

    function testVaultDeploymentArb() public {
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
        assertEq(_totalAssets, uint256(vault.totalAssets()));
        assertEq(_totalLent, uint256(vault.totalLent()));
        assertEq(_totalSupply, uint256(vault.totalSupply()));
        assertEq(_strategy, vault.strategy());
        assertEq(_performanceFee, uint256(vault.performanceFee()));
        assertEq(_managementFee, uint256(vault.managementFee()));
    }

    function testSetParamArb() public {
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

    function testSetStrategyArb() public {
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setStrategy(address(strategy));
        // vm.prank(address(0));
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setStrategy(address(strategy));
        vm.prank(deployer);
        vault.setStrategy(address(strategy));
    }

    function testPauseUnpauseArb() public {
        vm.expectRevert("Ownable: caller is not the owner");
        vault.pause();
        vm.prank(deployer);
        vault.pause();
        vm.prank(deployer);
        assertTrue(vault.paused());
        vm.prank(_usdcWhale);
        IERC20(_want).approve(address(vault), _depositAmount);
        vm.prank(_usdcWhale);
        vm.expectRevert("Pausable: paused");
        vault.deposit(_depositAmount, _usdcWhale);
        assertTrue(bool(vault.paused()));
        vm.expectRevert("Ownable: caller is not the owner");
        vault.unpause();
        vm.prank(deployer);
        vault.unpause();
        assertTrue(!bool(vault.paused()));
        vm.prank(_usdcWhale);
        IERC20(_want).approve(address(vault), _depositAmount);
        vm.prank(_usdcWhale);
        vault.deposit(_depositAmount, _usdcWhale);
        assertEq(uint256(vault.totalAssets()), _depositAmount);
    }

    function testDepositArb() public {
        for (uint256 i = 0; i < _users.length; i++) {
            vm.startPrank(_users[i]);
            IERC20(_want).approve(address(vault), _depositAmount);
            vault.deposit(_depositAmount, _users[i]);
            vm.expectRevert("!_amount");
            vault.deposit(0, _users[i]);
        }
        emit log_named_int("The depost amount is ", int256(_depositAmount * 3));
        emit log_named_int(
            "The total assets amount is ",
            int256(vault.totalAssets())
        );
        assertEq(uint256(vault.totalAssets()), _depositAmount * 3);
    }

    function testDepositArbFuzz(uint256 x) public {
        vm.prank(deployer);
        vault.setLimitState();
        vm.startPrank(_usdcWhale);
        IERC20(_want).approve(address(vault), 2**256 - 1);
        vault.deposit(_depositAmount, _usdcWhale);
        emit log_named_int(
            "vault value",
            int256(IERC20(_want).balanceOf(address(vault)))
        );
        vault.withdraw(
            IERC20(address(vault)).balanceOf(_usdcWhale),
            0,
            _usdcWhale
        );
        assertEq(IERC20(_want).balanceOf(address(vault)), 0);
    }

    function testIndividualDepositLimitArb() public {
        vm.startPrank(_usdcWhale);
        IERC20(_want).approve(address(vault), 2**256 - 1);
        vault.deposit(_depositAmount, _usdcWhale);
        assertEq(uint256(vault.totalAssets()), _depositAmount);
        vm.expectRevert("user cap reached");
        vault.deposit(_individualDepositLimit + 10, _usdcWhale);
    }

    function testWithdrawArb() public {
        for (uint256 i = 0; i < _users.length; i++) {
            vm.startPrank(_users[i]);
            IERC20(_want).approve(address(vault), _depositAmount);
            vault.deposit(_depositAmount, _users[i]);
            assertEq(IERC20(_want).balanceOf(_users[i]), 0);
            // start withdraw
            vault.withdraw(_depositAmount, 0, _users[i]);
            vm.expectRevert("!_shares");
            vault.withdraw(0, 0, _users[i]);
            assertEq(IERC20(_want).balanceOf(_users[i]), _depositAmount);
        }
        emit log_named_int("totalAssets", int256(vault.totalAssets()));
        assertEq(uint256(vault.totalAssets()), 0);
    }
}
