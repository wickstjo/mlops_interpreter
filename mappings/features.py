from common.misc import create_repository, option
from components.features import shift_column, stochastic_k, to_float_matrix
from components.features import to_dataframe, drop_nan_rows, extract_columns

repository = create_repository({

    # STANDARD FEATURES
    'shift_column': option(
        shift_column.feature,
        shift_column.tests
    ),
    'stochastic_k': option(
        stochastic_k.feature,
        stochastic_k.tests
    ),

    # "HIDDEN" FEATURES
    'to_dataframe': option(
        to_dataframe.feature,
        to_dataframe.tests
    ),
    'drop_nan_rows': option(
        drop_nan_rows.feature,
        drop_nan_rows.tests
    ),
    'extract_columns': option(
        extract_columns.feature,
        extract_columns.tests
    ),
    'to_float_matrix': option(
        to_float_matrix.feature,
        to_float_matrix.tests
    ),
}, label='feature')