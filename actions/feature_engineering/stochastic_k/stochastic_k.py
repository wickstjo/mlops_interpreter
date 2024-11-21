import pandas as pd

def stochastic_k(df: pd.DataFrame, input_params: dict):
    assert isinstance(df, pd.DataFrame), f"ARG 'df' MUST OF A PANDAS DATAFRAME, GOT {type(df)}"
    assert isinstance(input_params, dict), f"ARG 'input_params' MUST OF A DICT INT, GOT {type(input_params)}"

    # YANK OUT THE FEATURE WINDOW SIZE
    window_size: int = input_params['window_size']

    # CREATE THE FEATURE
    p1 = df['close'] - df['low'].rolling(window_size).min()
    p2 = df['high'].rolling(window_size).max() - df['low'].rolling(window_size).min()
    series = 100 * (p1 / p2)

    # RETURN AS A SELF-CONTAINED LIST
    return series.to_list()