from common.misc import create_repository, option
from components.models import linear_regression

repository = create_repository({
    'linear_regression': option(
        linear_regression.model,
        linear_regression.tests
    )
}, label='model')