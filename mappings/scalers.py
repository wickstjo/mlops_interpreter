from common.misc import create_repository, option
from components.scalers import standard_scaler, minmax_scaler

repository = create_repository({
    'standard_scaler': option(
        standard_scaler.scaler,
        standard_scaler.tests
    ),
    'minmax_scaler': option(
        minmax_scaler.scaler,
        minmax_scaler.tests
    )
}, label='scaler')