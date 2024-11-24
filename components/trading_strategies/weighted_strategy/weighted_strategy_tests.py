from common.testing import unittest_base
from weighted_strategy import weighted_strategy
import random

class validation_tests(unittest_base):
    def test_weighted_strategy_00_validate_inputs(self):

        # YANK OUT THE PARAMS INTENDED FOR THE STRATEGY
        custom_params = self.input_params['custom_strategy']['strategy_params']

        # MAKE SURE THEY MATCH SCHEMA
        self.validate_schema(custom_params, {
            'buy_weight': float,
            'sell_weight': float,
        })

        # MAKE SURE BUY WEIGHT IS IN RANGE
        buy_error = f"BUY_WEIGHT NOT IN VALID RANGE"
        self.assertGreaterEqual(custom_params['buy_weight'], 1, msg=buy_error)

        # MAKE SURE SELL WEIGHT IS IN RANGE
        sell_error = f"SELL_WEIGHT NOT IN VALID RANGE"
        self.assertGreater(custom_params['sell_weight'], 0, msg=sell_error)
        self.assertLessEqual(custom_params['sell_weight'], 1, msg=sell_error)

        # MAKE SURE THE CUSTOM PARAMS ARE CORRECTLY SAVED IN THE STATE
        strategy = weighted_strategy(self.input_params)
        self.assertEqual(custom_params, strategy.custom_strategy_params)

    ################################################################################################
    ################################################################################################

    def create_prefilled_strategy(self, init_capital=None, init_stocks=None):

        # OVERRIDE INIT STOCKS VALUE WHEN NEEDED
        if init_capital != None: self.input_params['base_strategy']['init_capital'] = init_capital
        if init_stocks != None: self.input_params['base_strategy']['init_stocks'] = init_stocks

        # CREATE THE STRATEGY & FILL THE BATCH WINDOW
        strategy = weighted_strategy(self.input_params)
        [strategy.make_decision(1, 2) for _ in range(strategy.state.batch_size - 1)]

        return strategy

    ################################################################################################
    ################################################################################################

    def test_weighted_strategy_01_buy_condition(self):
        strategy = self.create_prefilled_strategy(init_capital=100)
        buy_weighting = strategy.custom_strategy_params['buy_weight']

        # GENERATE A VALUE THAT SHOULD ALWAYS RESULT IN A BUY
        real_value = random.uniform(1, 10)
        inflated_predict_value = real_value * buy_weighting

        # MAKE & VERIFY A BUY DECISION
        output_1 = strategy.make_decision(real_value, inflated_predict_value)
        self.assertEqual(output_1['decision'], 'buy', 'BUY CONDITION IS NOT WORKING CORRECTLY')

        # REDUCING THE THRESHOLD SLIGHTLY SHOULD RESULT IN A HOLD
        output_2 = strategy.make_decision(real_value, inflated_predict_value * 0.99)
        self.assertEqual(output_2['decision'], 'hold', 'BUY CONDITION IS NOT WORKING CORRECTLY')

    ################################################################################################
    ################################################################################################

    def test_weighted_strategy_02_sell_condition(self):
        strategy = self.create_prefilled_strategy(init_stocks=1)
        sell_weighting = strategy.custom_strategy_params['sell_weight']

        # GENERATE A VALUE THAT SHOULD ALWAYS RESULT IN A SELL
        real_value = random.uniform(1, 10)
        reduced_predict_value = real_value * sell_weighting

        # MAKE A DECISION
        output = strategy.make_decision(real_value, reduced_predict_value)
        self.assertEqual(output['decision'], 'sell', 'SELL CONDITION IS NOT WORKING CORRECTLY')

        # INCREASING THE THRESHOLD SLIGHTLY SHOULD RESULT IN A HOLD
        output_2 = strategy.make_decision(real_value, reduced_predict_value * 1.01)
        self.assertEqual(output_2['decision'], 'hold', 'SELL CONDITION IS NOT WORKING CORRECTLY')

    ################################################################################################
    ################################################################################################

    def test_weighted_strategy_03_hold_condition(self):
        strategy = self.create_prefilled_strategy(init_stocks=1, init_capital=100)

        # GENERATE JUST THE ONE VALUE
        random_value = random.uniform(1, 10)

        # THIS SHOULD GUARANTEE A HOLD CONDITION
        output = strategy.make_decision(random_value, random_value)
        self.assertEqual(output['decision'], 'hold', 'HOLD CONDITION IS NOT WORKING CORRECTLY')

    ################################################################################################
    ################################################################################################