from pydantic import BaseModel
from common.testing import run_tests, build_and_validate_schema
from common import misc
from pandas import DataFrame

from mappings.data_retrieval import repository as retrieval_options
from mappings.features import repository as feature_options
from mappings.models import repository as model_options
from mappings.scalers import repository as scaler_options
from mappings.segmentation import repository as segmentation_options

##############################################################################################################
##############################################################################################################

# HIDE TRACEBACK ERRORS TEMPORARILY
import sys
sys.tracebacklimit = 0

class name_params_pair(BaseModel):
    name: str
    params: dict

class method_params_pair(BaseModel):
    method: str
    params: dict

class dataset_schema(BaseModel):
    method: str
    params: dict
    expected_schema: dict[str, str]

class training_schema(BaseModel):
    feature_columns: list[str]
    label_column: str
    segmentation: method_params_pair
    scaler: name_params_pair
    model: name_params_pair

class config_schema(BaseModel):
    dataset: dataset_schema
    features: list[name_params_pair]
    training: training_schema

##############################################################################################################
##############################################################################################################

def run():
    try:

    #####################################################################################
    ### LOAD & VALIDATE YAML

        raw_config: dict = misc.load_yaml('config.yaml')
        config: config_schema = config_schema(**raw_config)

    #####################################################################################
    ### UNITTEST DATASET RETRIEVAL

        dataset_module = retrieval_options.get_tests(config.dataset.method)
        run_tests(dataset_module, config.dataset.params)

        # THE TESTS PASSED -- LOAD IN A SAMPLE OF THE REAL DATASET FOR OTHER TESTS
        fetching_func = retrieval_options.get(config.dataset.method)
        sample_dataset = DataFrame(fetching_func(config.dataset.params, unittest_limit=200))

        # SELECT A SAMPLE ROW & MAKE SURE IT FOLLOWS EXPECTED SCHEMA
        sample_row = sample_dataset.iloc[0].to_dict()
        build_and_validate_schema(sample_row, config.dataset.expected_schema)

    #####################################################################################
    ### UNITTEST FEATURES

        # HIDDEN FEATURE -- CONVERT ANY INPUT TO A DATAFRAME
        feature_module = feature_options.get_tests('to_dataframe')
        run_tests(feature_module, {})

        # APPLY EACH NORMAL FEATURE
        for feature in config.features:
            feature_module = feature_options.get_tests(feature.name)
            run_tests(feature_module, {
                **feature.params,
                '_sample_dataset': sample_dataset
            })

        # HIDDEN FEATURE -- DROP ROWS WITH NANS
        feature_module = feature_options.get_tests('drop_nan_rows')
        run_tests(feature_module, {})

        # HIDDEN FEATURE -- EXTRACT FEATURE COLUMNS
        feature_module = feature_options.get_tests('extract_columns')
        run_tests(feature_module, { 'columns': config.training.feature_columns })

        # HIDDEN FEATURE -- CONVERT FROM DATAFRAME TO FLOAT MATRIX
        # SINCE THE SCALER (NEXT STEP) DOES NOT UNDERSTAND WHAT A DATAFRAME IS
        feature_module = feature_options.get_tests('to_float_matrix')
        run_tests(feature_module, {})

    #####################################################################################
    ### UNITTEST DATASET SEGMENTATION

        segmentation_module = segmentation_options.get_tests(config.training.segmentation.method)
        run_tests(segmentation_module, config.training.segmentation.params)

    #####################################################################################
    ### MAKE SURE ALL REQUIRED COLUMNS EXIST

        # FETCH BASELINE DATASET COLUMNS
        all_columns = list(config.dataset.expected_schema.keys())

        # APPEND IN EACH FEATURE COLUMN
        for feature in config.features:
            all_columns.append(feature.params['output_column'])

        # MAKE SURE LABEL COLUMN EXISTS
        label_error = f"LABEL COLUMN '{config.training.label_column}' DOES NOT EXIST.\nOPTIONS: {all_columns}"
        assert config.training.label_column in all_columns, label_error

        # MAKE SURE ALL FEATURE COLUMNS EXIST
        for column_name in config.training.feature_columns:
            feature_error = f"FEATURE COLUMN '{config.training.label_column}' DOES NOT EXIST.\nOPTIONS: {all_columns}"
            assert column_name in all_columns, feature_error

        # TODO: UNITTEST LABEL EXTRACTION FUNC
        # TODO: UNITTEST LABEL EXTRACTION FUNC
        # TODO: UNITTEST LABEL EXTRACTION FUNC

    #####################################################################################
    ### UNITTEST SCALER

        scaler_module = scaler_options.get_tests(config.training.scaler.name)
        run_tests(scaler_module, config.training.scaler.params)

    #####################################################################################
    ### UNITTEST MODEL

        model_module = model_options.get_tests(config.training.model.name)
        run_tests(model_module, config.training.model.params)

        # IF ALL TESTS PASSED, PROCEED WITH THE EXPERIMENT
        return True

    # OTHERWISE, AT LEAST ONE TEST FAILED
    # THEREFORE, BLOCK THE EXPERIMENT
    except AssertionError as error:
        print(f'\nINTERPRETER-SIDE ASSERTION ERROR:')
        print('----------------------------------------------------------------------')
        print(error)
        return False
    
    except Exception as error:
        print(f'\nINTERPRETER-SIDE FATAL ERROR:')
        print('----------------------------------------------------------------------')
        print(error)
        return False
    
##############################################################################################################
##############################################################################################################

if __name__ == '__main__':
    run()