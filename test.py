from common import misc, testing
from actions.data_retrieval.load_dataset import load_dataset
from pandas import DataFrame

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
                'drop_nan_rows': bool
            },
            'model_training': {
                'feature_columns': list,
                'label_column': str,
                'segmentation': list,
                'scalar': str or bool,
            },
            'trading_strategy': {
                'base_strategy': dict,
                'custom_strategy': {
                    'strategy_name': str,
                }
            },
        })

    ##########################################################################
    ### COMPLETED TESTS

        # TEST DATASET LOADING
        dataset_config: dict = experiment_config['dataset']
        # errors += testing.run_tests('actions/dataset', dataset_config)
        if len(errors) > 0: return print(errors)

        # ALL THE DATASET TESTS PASSED
        # MAKE A REAL SAMPLE DATASET AVAILABLE FOR OTHER TESTS
        sample_dataset: DataFrame = load_dataset(dataset_config, unittesting=200)
        print(sample_dataset.head(5))
        print()

        # TEST FEATURE ENGINEERING
        features_config: dict = experiment_config['feature_engineering']['features']
        errors += testing.feature_suite(features_config, sample_dataset)

        # feature = stochastic_k({ 'window_size': 5, 'output_column': 'sk5' })
        # modified_df = feature.transform(sample_dataset)
        # print(modified_df.head(10))

        # feature = shift_column({ 'target_column': 'close', 'shift_by': 2, 'output_column': 'shifted_close' })
        # modified_df = feature.transform(sample_dataset)
        # print(modified_df.head(10))

        # feature = vectorize_df({ 'feature_columns': [
        #     'open', 'close', 'high', 'low', 'volume',
        # ] })
        # output = feature.transform(sample_dataset)
        # print(output[:10])

        # # TEST DATA SEGMENTATION
        # segmentation_config: dict = experiment_config['segmentation']
        # errors += testing.run_tests('actions/segmentation', segmentation_config)

        # # TEST THE BASE TRADING STRATEGY
        # trading_config: dict = experiment_config['trading_strategy']
        # errors += testing.run_tests('actions/trading_strategies', trading_config)

        # # TEST THE CUSTOM STRATEGY
        # strategy_name = trading_config['custom_strategy']['strategy_name']
        # errors += testing.run_tests(f'actions/trading_strategies/{strategy_name}', trading_config)

    ##########################################################################
    ### TESTS IN DEVELOPMENT

        # # TEST THE BASE MODEL
        # model_training_config: dict = experiment_config['model_training']
        # errors += testing.run_tests('actions/model_training', model_training_config)

















    # OTHERWISE, STOP THE EXPERIMENT HERE
    except Exception as error:
        return print(f'\nFATAL EXCEPTION: {error}')

if __name__ == '__main__':
    run()
