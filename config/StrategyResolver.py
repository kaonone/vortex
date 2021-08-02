from helpers.StrategyCoreResolver import StrategyCoreResolver
from rich.console import Console
from brownie import interface

console = Console()

class StrategyResolver(StrategyCoreResolver):
    def hook_after_confirm_withdraw(self, before, after, params):
        """
            Specifies extra check for ordinary operation on withdrawal
            Use this to verify that balances in the get_strategy_destinations are properly set
        """
        assert True

    def hook_after_confirm_deposit(self, before, after, params):
        """
            Specifies extra check for ordinary operation on deposit
            Use this to verify that balances in the get_strategy_destinations are properly set
        """
        assert True

    def hook_after_earn(self, before, after, params):
        """
            Specifies extra check for ordinary operation on earn
            Use this to verify that balances in the get_strategy_destinations are properly set
        """
        assert True

    def confirm_harvest(self, before, after, tx):
        """
            Verfies that the Harvest produced yield and fees
        """
        console.print("=== Compare Harvest ===")
        self.manager.printCompare(before, after)
        self.confirm_harvest_state(before, after, tx)

        valueGained = after.get("sett.pricePerFullShare") > before.get(
            "sett.pricePerFullShare"
        )

        # Strategist should earn if fee is enabled and value was generated
        if before.get("strategy.performanceFeeStrategist") > 0 and valueGained:
            assert after.balances("want", "strategist") > before.balances(
                "want", "strategist"
            )

        # Strategist should earn if fee is enabled and value was generated
        if before.get("strategy.performanceFeeGovernance") > 0 and valueGained:
            assert after.balances("want", "governanceRewards") > before.balances(
                "want", "governanceRewards"
            )


    def confirm_tend(self, before, after, tx):
        """
        Tend Should;
        - Increase the number of staked tended tokens in the strategy-specific mechanism
        - Reduce the number of tended tokens in the Strategy to zero

        (Strategy Must Implement)
        """
        console.print("=== Compare Tend ===")
        self.manager.printCompare(before, after)
        # Tend only produces results if balance of want in strategy is > 0
        if before.get("strategy.balanceOfWant") > 0:
            # Check that balance of want on strategy goes to 0 after tend
            assert after.get("strategy.balanceOfWant") == 0

            # Amount deposited in pool must have increased
            assert after.get("strategy.balanceOfPool") > before.get("strategy.balanceOfPool")

    def get_strategy_destinations(self):
        """
        Track balances for all strategy implementations
        (Strategy Must Implement)
        """
        strategy = self.manager.strategy
        return {
            "chef": strategy.CHEF(),
            "pool": strategy.ibBTC_WBTC_LP(),
            "router": strategy.SUSHISWAP_ROUTER(),
            "badgerTree": strategy.badgerTree(),
        }   

    def add_balances_snap(self, calls, entities):
        super().add_balances_snap(calls, entities)
        strategy = self.manager.strategy

        sushi = interface.IERC20(strategy.SUSHI_TOKEN())
        wbtc = interface.IERC20(strategy.wBTC_TOKEN())
        ibbtc = interface.IERC20(strategy.ibBTC_TOKEN())
        wMATIC = interface.IERC20(strategy.reward())

        calls = self.add_entity_balances_for_tokens(calls, "sushi", sushi, entities)
        calls = self.add_entity_balances_for_tokens(calls, "wbtc", wbtc, entities)
        calls = self.add_entity_balances_for_tokens(calls, "ibbtc", ibbtc, entities)
        calls = self.add_entity_balances_for_tokens(calls, "wMATIC", wMATIC, entities)

        return calls

    def confirm_harvest_state(self, before, after, tx):
        key = "Harvest"
        if key in tx.events:
            if len(tx.events[key]) > 1:
                event = tx.events[key][1]
            else:
                event = tx.events[key][0] 

            keys = [
                "harvested",
            ]
            for key in keys:
                assert key in event

            console.print("[blue]== harvest() Harvest State ==[/blue]")
            self.printState(event, keys)

        key = "TreeDistribution"
        if key in tx.events:
            event = tx.events[key][0]
            keys = [
                "token",
                "amount",
            ]
            for key in keys:
                assert key in event

            console.print("[blue]== harvest() TreeDistribution State ==[/blue]")
            self.printState(event, keys)

            # If sushi is harvested, it is distributed to the tree
            assert after.balances("sushi", "badgerTree") > before.balances(
                "sushi", "badgerTree"
            )
            # All sushi harvested (after fees) is sent to the tree
            assert (
                after.balances("sushi", "badgerTree") - before.balances("sushi", "badgerTree") ==
                event["amount"]
            )
            # Governance rewards fees are charged
            assert after.balances("sushi", "governanceRewards") > before.balances(
                "sushi", "governanceRewards"
            )
            # Strategist rewards fees are charged
            assert after.balances("sushi", "strategist") > before.balances(
                "sushi", "strategist"
            )

    def printState(self, event, keys):
        for key in keys:
            print(key, ": ", event[key])
