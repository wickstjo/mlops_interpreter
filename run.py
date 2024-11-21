from common import misc, testing
from actions.dataset.load_dataset import load_dataset

def run():
    try:

    ##########################################################################
    ### LOAD EXPERIMENT YAML CONFIG

        experiment_config: dict = misc.load_yaml('config.yaml')
        errors: list = []

        # COMPARE CONFIG AGAINST MINIMUM REQUIRED SCHEMA
        testing.validate_schema(experiment_config, {
            'dataset': dict,
            'feature_engineering': {
                'features': list,
                'drop_nans': bool
            },
            'segmentation': list,
            'trading_strategy': {
                'base_strategy': dict,
                'custom_strategy': {
                    'strategy_name': str,
                }
            }
        })

    ##########################################################################
    ### COMPLETED TESTS

        # TEST DATASET LOADING
        dataset_config: dict = experiment_config['dataset']
        errors += testing.run_tests('actions/dataset', dataset_config)

        # ALL THE DATASET TESTS PASSED
        # MAKE A REAL SAMPLE DATASET AVAILABLE FOR OTHER TESTS
        sample_dataset: list[dict] = load_dataset(dataset_config, unittesting=200)

        # # TEST FEATURE ENGINEERING
        features_config: dict = experiment_config['feature_engineering']['features']
        errors += feature_prep(features_config, sample_dataset)

        # TEST DATA SEGMENTATION
        segmentation_config: dict = experiment_config['segmentation']
        errors += testing.run_tests('actions/segmentation', segmentation_config)

    ##########################################################################
    ### TESTS IN DEVELOPMENT

        # TEST THE BASE TRADING STRATEGY
        trading_config: dict = experiment_config['trading_strategy']
        errors += testing.run_tests('actions/trading_strategies', trading_config)

        # TEST THE CUSTOM STRATEGY
        strategy_name = trading_config['custom_strategy']['strategy_name']
        errors += testing.run_tests(f'actions/trading_strategies/{strategy_name}', trading_config)


















    # OTHERWISE, STOP THE EXPERIMENT HERE
    except Exception as error:
        return print(f'\nFATAL EXCEPTION: {error}')


def feature_prep(features_config, sample_dataset):
    errors = []
    feature_columns = set()

    # LOOP THROUGH EACH FEATURE
    for nth, feature_block in enumerate(features_config):

        # MAKE SURE IT CONTAINS THE CORRECT PROPERTIES
        for prop_name in ['feature_name', 'feature_params', 'output_column']:
            assert prop_name in feature_block, f"PROPERTY '{prop_name}' MISSING FROM FEATURE #{nth+1}"

        feature_name = feature_block['feature_name']
        feature_params = feature_block['feature_params']
        output_column = feature_block['output_column']

        # MAKE SURE OUTPUT COLUMN NAMES ARE UNIQUE
        assert output_column not in feature_columns, f"DUPLICATE FEATURE OUTPUT COLUMN FOUND ({output_column})"
        feature_columns.add(output_column)

        # UNITTEST THE FEATURE
        errors += testing.run_tests(f"actions/feature_engineering/{feature_name}", {
            **feature_params,
            '_sample_dataset': sample_dataset
        })

    return errors

run()
