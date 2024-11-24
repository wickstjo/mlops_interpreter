from common.misc import create_repository, option
from components.segmentation import standard_ttv

repository = create_repository({
    'standard_ttv': option(
        standard_ttv.segment_dataset,
        standard_ttv.tests
    ),
}, label='segmentation_method')