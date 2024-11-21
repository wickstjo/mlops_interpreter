from dataclasses import dataclass, field

class base_strategy:
    def __init__(self, input_params: dict):
        assert isinstance(input_params, dict), f"ARG 'input_params' MUST BE OF TYPE DICT"

        @dataclass
        class create_state:

            # STATIC INFO
            batch_size: int = input_params['base_strategy']['batch_size']
            transaction_fee: int = input_params['base_strategy']['transaction_fee']

            # TRACK CURRENT CAPITAL & STOCK OWNERSHIP
            num_capital: int = input_params['base_strategy']['init_capital']
            num_stock: int = input_params['base_strategy']['init_stocks']

            # MOVING WINDOW OF REAL VALUES & PREDICTIONS
            model_predictions: list[float] = field(default_factory=list)
            real_values: list[float] = field(default_factory=list)

            # TRACK BUY/SELL/HOLD DECISION SEQUENCE
            decision_log: list[dict] = field(default_factory=list)

            # VALUES NEEDED TO CREATE YAML OVERVIEW
            init_capital: int = input_params['base_strategy']['init_capital']
            init_stock_count: int = input_params['base_strategy']['init_stocks']
            init_stock_value: int = None
            final_stock_value: int = None

        # CREATE THE STATE
        self.state = create_state()

        # MAKE THE CUSTOM STRATEGYS' PARAMS AVAILABLE
        self.custom_strategy_params: dict = input_params['custom_strategy']['strategy_params']

    ################################################################################################
    ################################################################################################

    # SAFE GETTER FUNCS FOR CHILD STRATEGIES
    # INSTEAD OF DIRECTLY INTERACTING WITH THE BASE STATE, WHICH IS DANGEROUS
    def get_capital(self): return self.state.num_capital
    def get_stocks(self): return self.state.num_stock
    def get_transaction_fee(self): return self.state.transaction_fee

    # RETURNS TRUE/FALSE, THE NUMBER OF STOCKS TO BUY, AND A HUMAN-READABLE REASON
    def buy(self, latest_values: list[dict], predicted_values: list[dict]):
        raise NotImplementedError()
    
    # RETURNS TRUE/FALSE, THE NUMBER OF STOCKS TO SELL, AND A HUMAN-READABLE REASON
    def sell(self, latest_values: list[dict], predicted_values: list[dict]):
        raise NotImplementedError()

    ################################################################################################
    ################################################################################################

    # LET STRATEGY MAKE DECISION
    def make_decision(self, latest_known_value: float, predicted_value: float):

        # SAVE FIRST STOCK VALUE FOR LOGGING PURPOSES
        if self.state.init_stock_value == None:
            self.state.init_stock_value = latest_known_value

        # ADD NEW VALUES TO CONTAINERS
        self.state.real_values.append(latest_known_value)
        self.state.model_predictions.append(predicted_value)
        self.state.final_stock_value = latest_known_value

        # THE DEFAULT DECISION IS TO HOLD
        # THE REASON FOR THE HOLD WILL BE FILLED IN LATER
        decision_watermark = {
            'decision': 'hold',
            'reason': 'TBD'
        }

        # CANT MAKE DECISION YET -- STILL COLLECTING INITIAL BATCHES
        if len(self.state.model_predictions) < self.state.batch_size:
            decision_watermark['reason'] = 'COLLECTING INITIAL BATCH WINDOWS'
            return self.log_decision(decision_watermark)

        # TRUNCATE CONTAINERS TO KEEP SEQUENTIAL ROLLING WINDOW
        if len(self.state.model_predictions) > self.state.batch_size:
            self.state.model_predictions = self.state.model_predictions[1:]
            self.state.real_values = self.state.real_values[1:]

    ################################################################################################
    ################################################################################################

        # RUN THE CHILD-STRATEGY'S BUY/SELL DECISIONS
        buy_block = self.buy(self.state.real_values, self.state.model_predictions)
        sell_block = self.sell(self.state.real_values, self.state.model_predictions)

        # MAKE SURE THEY HAVE RETURN VALUES
        assert buy_block != None, f"BUY FUNC RETURNED NONE, EXPECTING (BOOL, INT, STR)"
        assert sell_block != None, f"sell FUNC RETURNED NONE, EXPECTING (BOOL, INT, STR)"

        # MAKE SURE THERE ARE THREE RETURN VALUES
        assert len(buy_block) == 3, f"BUY FUNC RETURNED TOO {len(buy_block)} VALUES, EXPECTING (BOOL, INT, STR)"
        assert len(sell_block) == 3, f"SELL FUNC RETURNED TOO {len(sell_block)} VALUES, EXPECTING (BOOL, INT, STR)"

        # EXTRACT THE VALUES
        buy_decision, buy_n_stocks, buy_reason = buy_block
        sell_decision, sell_n_stocks, sell_reason = sell_block

        # ENFORCE RETURN TYPES
        assert isinstance(buy_decision, bool), f"RETURN VALUE 'buy_decision' MUST BE OF TYPE BOOL, GOT {type(buy_decision)}"
        assert isinstance(sell_decision, bool), f"RETURN VALUE 'sell_decision' MUST BE OF TYPE BOOL, GOT {type(sell_decision)}"

        assert isinstance(buy_n_stocks, int), f"RETURN VALUE 'buy_n_stocks' MUST BE OF TYPE INT, GOT {type(buy_n_stocks)}"
        assert isinstance(sell_n_stocks, int), f"RETURN VALUE 'sell_n_stocks' MUST BE OF TYPE INT, GOT {type(sell_n_stocks)}"

        assert isinstance(buy_reason, str), f"RETURN VALUE 'buy_reason' MUST BE OF TYPE STR, GOT {type(buy_reason)}"
        assert isinstance(sell_reason, str), f"RETURN VALUE 'sell_reason' MUST BE OF TYPE STR, GOT {type(sell_reason)}"

        # PREVENT NEGATIVE/POSITIVE STOCK BUYS/SELLS
        assert buy_n_stocks >= 0, 'CHILD STRATEGY TRIED TO BUY A NEGATIVE AMOUNT OF STOCKS'
        assert sell_n_stocks >= 0, 'CHILD STRATEGY TRIED TO SELL A NEGATIVE AMOUNT OF STOCKS'

        # PREVENT SIMULTANOUS BUYS AND SELLS
        assert (buy_decision and sell_decision) == False, 'CHILD STRATEGY TRIED TO BUY AND SELL SIMULTANOUSLY'

        # PROCESS BUY DECISION
        if buy_decision:

            # HOW MUCH CAPITAL DO WE NEED TO BUY n STOCKS?
            required_capital = (buy_n_stocks * latest_known_value) + self.state.transaction_fee

            # BLOCK BUYS WHEN WE DONT HAVE ENOUGH CAPITAL
            if self.state.num_capital < required_capital:
                decision_watermark['reason'] = 'BUY BLOCKED DUE TO LACK OF CAPITAL'
                return self.log_decision(decision_watermark)

            # OTHERWISE, UPDATE STATE
            self.state.num_capital -= required_capital
            self.state.num_stock += buy_n_stocks

            # UPDATE WATERMARK AND EXIT
            return self.log_decision({
                'decision': 'buy',
                'reason': buy_reason
            })

        # REGISTER SELL
        if sell_decision:

            # BLOCK SELLS WHEN WE DONT HAVE ENOUGH STOCKS
            if self.state.num_stock < sell_n_stocks:
                decision_watermark['reason'] = 'SELL BLOCKED DUE TO LACK OF STOCKS'
                return self.log_decision(decision_watermark)

            # HOW MUCH MONEY DID WE MAKE?
            cumulative_capital = (sell_n_stocks * latest_known_value) - self.state.transaction_fee

            # OTHERWISE, UPDATE STATE
            self.state.num_stock -= sell_n_stocks
            self.state.num_capital += cumulative_capital

            # UPDATE WATERMARK AND EXIT
            return self.log_decision({
                'decision': 'sell',
                'reason': sell_reason
            })
        
        # OTHERWISE, JUST HOLD
        decision_watermark['reason'] = 'NO OTHER CONDITION WAS MET'
        return self.log_decision(decision_watermark)

    ################################################################################################
    ################################################################################################

    # ADD DECISION TO LOG, THEN RETURN IT TO THE CALLEE
    def log_decision(self, decision_watermark: dict):
        self.state.decision_log.append(decision_watermark)
        return decision_watermark
    
    ################################################################################################
    ################################################################################################

# foo = base_strategy({
#     'strategy_name': 'foo',
#     'batch_size': 3,
#     'starting_capital': 1000,
#     'starting_stocks': 0,
# })

# print(foo._state)