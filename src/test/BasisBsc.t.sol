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

    function startPrank(address) external;

    function stopPrank() external;

    function expectRevert(bytes calldata) external;
    
    function wrap(uint256) external;
}

contract BasisTestBsc is DSTest {
    Vm vm = Vm(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);
    address constant deployer = 0xBF2B82E026B182Bb4f5f10CCfB6136b1df08e29F;
    address constant _want = 0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56;
    address constant _weth = 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c;
    address constant _longAsset = 0x2170Ed0880ac9A755fd29B2688956BD959F933F8;
    address constant _uniPool = 0x7213a321F1855CF1779f42c0CD85d3D95291D34C;
    address constant _router = 0x10ED43C718714eb63d5aA57B78B54704E256024E;
    address constant _mcLiquidity = 0xdb282BBaCE4E375fF2901b84Aceb33016d0d663D;
    address constant _usdcWhale = 0x8894E0a0c962CB723c1976a4421c95949bE2D4E3;
    address constant _usdcProxy = 0x1eFB3f88Bc88f03FD1804A5C53b7141bbEf5dED8;
    address constant _mcDEXOracle = 0xa04197E5F7971E7AEf78Cf5Ad2bC65aaC1a967Aa;
    address constant _random = 0x6B69fB91E91C6C43FaD962B9BD9636c2C95de748;
    address[3] _users = [address(14), address(15), address(16)];
    uint256 constant _depositLimit = 10_000_000e18;
    uint256 constant _buffer = 100_000;
    uint256 constant _perpIndex = 0;
    uint256 constant _depositAmount = 100_000e18;
    uint256 constant _yieldAmount = 2_000e18;
    uint256 constant _accuracy_usdc = 1e16;
    uint256 constant _accuracy = 1e21;
    uint256 constant _accuracyMC = 1e17;
    uint256 constant _individualDepositLimit = 1_000_000e18;
    bool constant _isV2 = true;
    uint256 constant _add_value = 1e18;
    uint256 constant _tradeSlippage = 1000e18;

    BasisVault vault;
    BasisStrategy strategy;

    function setUp() public {
        vault = new BasisVault();
        vm.startPrank(deployer);
        vault.initialize(_want, _depositLimit, _individualDepositLimit);
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
        for (uint256 i=0; i < _users.length; i++){
            assertEq(IERC20(_want).balanceOf(_users[i]), 0);
            IERC20(_want).transfer(_users[i], _depositAmount);
        }
        vm.stopPrank();
    }

    function testVaultDeploymentBsc() public {
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
        vm.expectEmit(true, true, true, true);
    }

    function testSetParamBsc() public {
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

    function testSetStrategyBsc() public {
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setStrategy(address(strategy));
        // vm.prank(address(0));
        vm.expectRevert("Ownable: caller is not the owner");
        vault.setStrategy(address(strategy));
        vm.prank(deployer);
        vault.setStrategy(address(strategy));
    }

    function testPauseUnpauseBsc() public {
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

    function testDepositBsc() public {
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

    function testDepositFuzz(uint256 x) public {
        vm.prank(deployer);
        vault.setLimitState();
        vm.startPrank(_usdcWhale);
        IERC20(_want).approve(address(vault), 2**256 -1);
        vault.deposit(_depositAmount, _usdcWhale);
        emit log_named_int("vault value", int256(IERC20(_want).balanceOf(address(vault))));
        vault.withdraw(IERC20(address(vault)).balanceOf(_usdcWhale), 0, _usdcWhale);
        assertEq(IERC20(_want).balanceOf(address(vault)), 0);
        
        
    }

    function testIndividualDepositLimitBsc() public {
        vm.startPrank(_usdcWhale);
        IERC20(_want).approve(address(vault), 2**256 - 1);
        vault.deposit(_depositAmount, _usdcWhale);
        assertEq(uint256(vault.totalAssets()), _depositAmount);
        vm.expectRevert("user cap reached");
        vault.deposit(_individualDepositLimit + 10, _usdcWhale);
    }

    function testWithdrawBsc() public {

        for (uint256 i=0; i<_users.length; i++) {
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

    function testHarvestBsc() public {
        vm.startPrank(_usdcWhale);
        IERC20(_want).transfer(deployer, _depositLimit);
        vm.stopPrank();
        vm.startPrank(deployer);
        vault.setStrategy(address(strategy));
        strategy.setSlippageTolerance(int256(_tradeSlippage));
        vault.setProtocolFees(2000, 200);
        IERC20(_want).approve(address(vault), 2**256 - 1);
        vault.deposit(_depositAmount * 9, deployer);
        strategy.harvest();
        assertEq(IERC20(_want).balanceOf(address(vault)), 0);
        assertEq(IERC20(_want).balanceOf(address(strategy)), 0);
        // assertEq(int256(vault.totalLent()), (int256(_depositAmount * 9) / 1e12));
        (int256 cash, , , , , , , ) = strategy.getMarginAccount();
        (int256 price, ) = IOracle(_mcDEXOracle).priceTWAPLong();
        // int256 value = ((cash / price) + (int256(IERC20(_longAsset).balanceOf(address(strategy))) / price));
        // emit log_named_int("value", value);
        assert((cash / price) + (int256(IERC20(_longAsset).balanceOf(address(strategy))) / price) <= 1e4); 
        uint256 maxLoss = vault.expectedLoss(IERC20(address(vault)).balanceOf(deployer));
        emit log_named_int("balance vault", int256(maxLoss));
        vault.withdraw(IERC20(address(vault)).balanceOf(deployer), maxLoss, deployer);
        assertEq(IERC20(_want).balanceOf(address(vault)), 0);
        assertEq(vault.totalLent(), 0);
        assertEq(IERC20(_want).balanceOf(address(strategy)), 0);
        assertEq(vault.pricePerShare(), _add_value);
    }

    function whaleTransfer() public {
        vm.startPrank(_usdcWhale);
        for(uint256 i =0; i < _users.length; i++) {
            IERC20(_want).transfer(_users[i], _depositAmount * 8);
        }
        vm.stopPrank();
    }

    function testDepositHarvestBsc() public {
        whaleBuyLong();
        whaleTransfer();
        addressDeposit();
        vm.startPrank(deployer);
        vault.setStrategy(address(strategy));
        for(uint256 i = 0; i < 10; i++) {
            strategy.harvest();
        }
        vm.stopPrank();
        vm.startPrank(_users[2]);
        vault.deposit(_depositAmount * 2, _users[2]);
        vm.stopPrank();
        vm.startPrank(deployer);
        strategy.harvest();
        for (uint256 i = 0; i < 10; i++) {
            strategy.remargin();
        }
        vm.stopPrank();
        addressWithdraw();
        assertEq(vault.totalSupply(), 0);
        assertEq(vault.totalLent(), 0);
        assertEq(IERC20(_want).balanceOf(address(vault)), 0);
        assertEq(IERC20(_longAsset).balanceOf(address(strategy)), 0);

    }


    function testWithdrawHarvest() public {
        whaleTransfer();
        addressDepositAll();
        vm.startPrank(deployer);
        vault.setStrategy(address(strategy));
        vm.wrap(28801);
        strategy.harvest();
        vm.stopPrank();
        whaleBuyShort();
        uint256 balanceBefore = IERC20(_want).balanceOf(_users[0]);
        for(uint256 i = 0; i < _users.length; i++) {
            assertEq(IERC20(_want).balanceOf(_users[i]), 0);
        }
        vm.prank(deployer);
        for (uint256 i=0; i<20; i++){
            strategy.harvest();
        }
        uint256 loss = vault.expectedLoss(IERC20(address(vault)).balanceOf(_users[0]));
        vm.prank(_users[0]);
        vault.withdraw(IERC20(address(vault)).balanceOf(_users[0]), loss, _users[0]);
        assert (balanceBefore < IERC20(_want).balanceOf(_users[0]));
    }
 
    function whaleBuyLong() public {
        vm.startPrank(_usdcWhale);
        IERC20(_want).transfer(deployer, 2_000_000e18);
        vm.stopPrank();
        vm.startPrank(deployer);
        (int256 cash, , , , , , , , ) = IMCLP(_mcLiquidity).getMarginAccount(1, deployer);
        IMCLP(_mcLiquidity).setTargetLeverage(1, deployer, 1e18);
        // whale deposit to the pool
        IERC20(_want).approve(address(_mcLiquidity), 2**256 -1);
        IMCLP(_mcLiquidity).deposit(1, deployer, int256(1_500_000e18));
        // start trading
        (, , int256 amount, , , , , , )  =  IMCLP(_mcLiquidity).getMarginAccount(1, deployer);
        (int256 price, ) = IOracle(_mcDEXOracle).priceTWAPLong();
        int256 tradeAmount = int256((1_200_000e18 * 1e18) / price);
        emit log_named_int("trade amount", tradeAmount);
        emit log_named_int("price", price); 
        IMCLP(_mcLiquidity).trade(1, deployer, tradeAmount, price, (block.timestamp + 10000), deployer, 0x40000000);
    }

    function whaleBuyShort() public {
        vm.startPrank(_usdcWhale);
        IERC20(_want).transfer(deployer, 2_000_000e18);
        vm.stopPrank();
        vm.startPrank(deployer);
        (int256 cash, , , , , , , , ) = IMCLP(_mcLiquidity).getMarginAccount(1, deployer);
        IMCLP(_mcLiquidity).setTargetLeverage(1, deployer, 1e18);
        // whale deposit to the pool
        IERC20(_want).approve(address(_mcLiquidity), 2**256 -1);
        IMCLP(_mcLiquidity).deposit(1, deployer, int256(1_500_000e18));
        // start trading
        (, , int256 amount, , , , , , )  =  IMCLP(_mcLiquidity).getMarginAccount(1, deployer);
        (int256 price, ) = IOracle(_mcDEXOracle).priceTWAPLong();
        int256 tradeAmount = int256((1_000_000e18 * 1e18) / price);
        emit log_named_int("trade amount", tradeAmount);
        emit log_named_int("price", price); 
        IMCLP(_mcLiquidity).trade(1, deployer, -tradeAmount, price, (block.timestamp + 10000), deployer, 0x40000000);
    }

    function addressDeposit() public {
        for(uint256 i = 0; i<_users.length; i++){
            vm.startPrank(_users[i]);
            IERC20(_want).approve(address(vault), 2 ** 256 -1);
            vault.deposit(_depositAmount * 2, _users[i]);
            vm.stopPrank();
        } 
    }

    function addressDepositAll() public {
        for(uint256 i = 0; i<_users.length; i++){
            vm.startPrank(_users[i]);
            IERC20(_want).approve(address(vault), 2 ** 256 -1);
            vault.deposit(IERC20(_want).balanceOf(_users[i]), _users[i]);
            vm.stopPrank();
        } 
    }

    function addressWithdraw() public {
        for(uint256 i = 0; i<_users.length; i++){
            vm.startPrank(_users[i]);
            uint256 loss = vault.expectedLoss(IERC20(address(vault)).balanceOf(_users[i]));
            vault.withdraw(IERC20(address(vault)).balanceOf(_users[i]), loss, _users[i]);
            vm.stopPrank();
        } 
    }
}
