from base_strategy import base_strategy

class weighted_strategy(base_strategy):
    def buy(self, real_values: list[dict], predicted_values: list[dict]):

        # ONLY CONSIDER LATEST VALUES ON BATCH ARRAYS
        latest_real = real_values[-1]
        latest_predicted = predicted_values[-1]

        # EXTRACT THE BUY WEIGHT
        buy_weight = self.custom_strategy_params['buy_weight']

        if (latest_real * buy_weight) <= latest_predicted:
            return True, 1, 'WEIGHTED BUY CONDITION MET'

        return False, 0, ''

    ################################################################################################
    ################################################################################################

    def sell(self, real_values: list[dict], predicted_values: list[dict]):

        # ONLY CONSIDER LATEST VALUES ON BATCH ARRAYS
        latest_real = real_values[-1]
        latest_predicted = predicted_values[-1]

        # EXTRACT THE SELL WEIGHT
        sell_weight = self.custom_strategy_params['sell_weight']

        if (latest_real * sell_weight) >= latest_predicted:
            return True, 1, 'WEIGHTED SELL CONDITION MET'

        return False, 0, ''