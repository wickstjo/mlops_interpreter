from common.misc import create_repository, option
from components.data_retrieval import from_cassandra

repository = create_repository({
    'from_cassandra': option(
        from_cassandra.load_dataset,
        from_cassandra.tests
    )
}, label='dataset_method')