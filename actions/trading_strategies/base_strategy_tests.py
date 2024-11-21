from common.testing import unittest_base
from base_strategy import base_strategy
import random

################################################################################################
################################################################################################

class mock_strategy(base_strategy):
    def buy(self, real_values: list[dict], predicted_values: list[dict]):
        if real_values[-1] < predicted_values[-1]:
            return True, 1, 'NAIVE BUY CONDITION MET'

        return False, 0, ''

    def sell(self, real_values: list[dict], predicted_values: list[dict]):
        if real_values[-1] > predicted_values[-1]:
            return True, 1, 'NAIVE SELL CONDITION MET'

        return False, 0, ''

################################################################################################
################################################################################################

class validation_tests(unittest_base):
    def test_base_strategy_00_validate_inputs(self):

        # VALIDATE INPUT AGAINST REFERENCE SCHEMA
        self.validate_schema(self.input_params, {
            'base_strategy': {
                'batch_size': int,
                'transaction_fee': int,
                'init_capital': int,
                'init_stocks': int,
            },
            'custom_strategy': {
                'strategy_name': str,
                'strategy_params': dict
            }
        }, root_path='trading_strategy')

        # PREVENT TOO SMALL BATCH SIZES
        self.assertGreater(self.input_params['base_strategy']['batch_size'], 0, msg='BATCH SIZE MUST BE LARGER THAN 0')

        # PREVENT INIT CAPITAL AND INIT STOCKS FROM BEING NEGATIVE
        self.assertGreaterEqual(self.input_params['base_strategy']['init_capital'], 0, msg='INIT_CAPITAL CANNOT START FROM NEGATIVE')
        self.assertGreaterEqual(self.input_params['base_strategy']['init_stocks'], 0, msg='INIT_STOCKS COUNT CANNOT START FROM NEGATIVE')

        # PREVENT BOTH CAPITAL AND STOCK COUNT TO START FROM ZERO
        # WOULD BLOCK THE STRATEGY FROM DOING ANYTHING
        dual_error = 'BOTH CAPITAL AND STOCK COUNT CANNOT START FROM ZERO'
        self.assertTrue(self.input_params['base_strategy']['init_capital'] > 0 or self.input_params['init_stocks'] > 0, msg=dual_error)

        # MAKE SURE THE TRADE PENALTY IS POSITIVE
        self.assertGreater(self.input_params['base_strategy']['transaction_fee'], 0, msg='TRANSACTION FEE CANNOT BE NEGATIVE')

        # MAKE SURE THE CUSTOM STRATEGY HAS A PROPER NAME
        self.assertGreater(len(self.input_params['custom_strategy']['strategy_name']), 0, msg='LENGTH OF THE CUSTOM STRATEGY NAME CANNOT BE 0')

    ################################################################################################
    ################################################################################################

    def create_mock_strategy(self, prefilled=False, init_capital=None, init_stocks=None):

        # DEFAULT TO YAML CONFIG PARAMS
        default_config = self.input_params

        # OVERRIDE CAPITAL/STOCK VALUES FOR TESTING
        if init_capital != None: default_config['base_strategy']['init_capital'] = init_capital
        if init_stocks != None: default_config['base_strategy']['init_stocks'] = init_stocks

        # CREATE THE STRATEGY
        strategy = mock_strategy(default_config)

        # FILL THE BATCH WINDOW WHEN REQUESTED
        # SO THE NEXT INVOCATION PRODUCES A REAL DECISION
        if prefilled:
            [strategy.make_decision(1, 2) for _ in range(strategy.state.batch_size - 1)]

        return strategy

    ################################################################################################
    ################################################################################################

    def test_base_strategy_01_batch_windows_logic(self):
        strategy = self.create_mock_strategy(prefilled=True, init_capital=100)

        # MAKE SURE ALL THE DECISIONS PRE-BATCH WINDOW ARE HOLDS
        for item in strategy.state.decision_log:
            self.assertEqual(item['decision'], 'hold')

        # THEN RUN ONE OF EACH DECISION
        buy_decision = strategy.make_decision(1, 2)['decision']
        sell_decision = strategy.make_decision(2, 1)['decision']
        hold_decision = strategy.make_decision(1, 1)['decision']

        # VERIFY THE OTHERS
        self.assertEqual(buy_decision, 'buy')
        self.assertEqual(sell_decision, 'sell')
        self.assertEqual(hold_decision, 'hold')

        # FINALLY, MAKE SURE THE BATCH WINDOWS HAVE BEEN TRUNCATED CORRECTLY
        self.assertEqual(len(strategy.state.model_predictions), strategy.state.batch_size)
        self.assertEqual(len(strategy.state.real_values), strategy.state.batch_size)

    ################################################################################################
    ################################################################################################

    def test_base_strategy_02_buying_state_change(self):
        strategy = self.create_mock_strategy(prefilled=True, init_capital=11)

        # SAVE THE INITIAL VALUES
        pre_capital = strategy.state.num_capital
        pre_stocks = strategy.state.num_stock

        # MAKE & VERIFY BUY DECISION
        rng_price = random.randrange(2, 10)
        output = strategy.make_decision(rng_price, rng_price+1)
        self.assertEqual(output['decision'], 'buy')

        # FIND THE DELTAS OF THE NEW VALUES
        capital_delta = strategy.state.num_capital - pre_capital
        stocks_delta = strategy.state.num_stock - pre_stocks

        # MAKE SURE THEY'RE CORRECT
        self.assertEqual(capital_delta, -(rng_price + strategy.state.transaction_fee))
        self.assertEqual(stocks_delta, 1)

    ################################################################################################
    ################################################################################################

    def test_base_strategy_03_buying_without_capital(self):
        strategy = self.create_mock_strategy(prefilled=True, init_capital=0)

        output = strategy.make_decision(1, 2)
        self.assertEqual(output['decision'], 'hold')

    ################################################################################################
    ################################################################################################

    def test_base_strategy_04_selling_state_change(self):
        strategy = self.create_mock_strategy(prefilled=True, init_stocks=1)

        # SAVE THE INITIAL VALUES
        pre_capital = strategy.state.num_capital
        pre_stocks = strategy.state.num_stock

        # MAKE & VERIFY SELL DECISION
        rng_price = random.randrange(2, 10)
        output = strategy.make_decision(rng_price, rng_price-1)
        self.assertEqual(output['decision'], 'sell')

        # FIND THE DELTAS OF THE NEW VALUES
        capital_delta = strategy.state.num_capital - pre_capital
        stocks_delta = strategy.state.num_stock - pre_stocks

        # MAKE SURE THEY'RE CORRECT
        self.assertEqual(capital_delta, (rng_price - strategy.state.transaction_fee))
        self.assertEqual(stocks_delta, -1)

    ################################################################################################
    ################################################################################################

    def test_base_strategy_05_selling_without_stocks(self):
        strategy = self.create_mock_strategy(prefilled=True, init_stocks=0)

        output = strategy.make_decision(2, 1)
        self.assertEqual(output['decision'], 'hold')

    ################################################################################################
    ################################################################################################

    def test_base_strategy_06_holding_state_change(self):
        strategy = self.create_mock_strategy(prefilled=True)

        # SAVE THE INITIAL VALUES
        pre_capital = strategy.state.num_capital
        pre_stocks = strategy.state.num_stock

        # MAKE & VERIFY HOLD DECISION
        output = strategy.make_decision(420, 420)
        self.assertEqual(output['decision'], 'hold')

        # FIND THE DELTAS OF THE NEW VALUES
        capital_delta = strategy.state.num_capital - pre_capital
        stocks_delta = strategy.state.num_stock - pre_stocks

        # MAKE SURE THEY'RE CORRECT
        self.assertEqual(capital_delta, 0)
        self.assertEqual(stocks_delta, 0)

    ################################################################################################
    ################################################################################################

    def test_base_strategy_07_outputs_match_log(self):
        strategy = self.create_mock_strategy()
        outputs = []

        # MAKE 100 RANDOM DECISION
        for _ in range(100):
            first, second = random.randrange(3), random.randrange(3)
            output = strategy.make_decision(first, second)
            outputs.append(output)

        # MAKE SURE OUTPUTS & STRATEGY LOG MATCH
        self.assertEqual(outputs, strategy.state.decision_log)

    ################################################################################################
    ################################################################################################

    def test_base_strategy_08_getter_funcs_work_correctly(self):
        strategy = self.create_mock_strategy()

        # REAL VALUES OBTAINED THROUGH STATE
        state_capital = strategy.state.num_capital
        state_stocks = strategy.state.num_stock

        # SAME VALUES OBTAINED THROUGH GETTER FUNCS
        getter_capital = strategy.get_capital()
        getter_stocks = strategy.get_stocks()

        # MAKE SURE OUTPUTS & STRATEGY LOG MATCH
        self.assertEqual(state_capital, getter_capital, 'CAPITAL GETTER FUNC RETURNING INCORRECT VALUE')
        self.assertEqual(state_stocks, getter_stocks, 'STOCKS GETTER FUNC RETURNING INCORRECT VALUE')