from common import misc
from sklearn.pipeline import Pipeline
from pydantic import BaseModel

from mappings.data_retrieval import repository as retrieval_options
from mappings.features import repository as feature_options
from mappings.models import repository as model_options
from mappings.scalers import repository as scaler_options
from mappings.segmentation import repository as segmentation_options

from components.segmentation.generate_labels import generate_segment_labels

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
        raw_config: dict = misc.load_yaml('config.yaml')
        config = config_schema(**raw_config)

        pipeline_components = []

    ########################################################################################
    ### LOAD & SEGMENT DATASET

        retrieval_method = retrieval_options.get(config.dataset.method)
        dataset = retrieval_method(config.dataset.params)
        # dataset = retrieval_method(config.dataset.params, unittest_limit=200)

        segmentation_method = segmentation_options.get(config.training.segmentation.method)
        dataset = segmentation_method(config.training.segmentation.params, dataset)

    ########################################################################################
    ### ADD FIRST LAYER OF FEATURES

        # HIDDEN -- CONVERT INPUT TO DATAFRAME
        feature_instance = feature_options.create('to_dataframe')
        pipeline_components.append(('hidden_to_df', feature_instance))

        # NORMAL -- APPLY EACH CUSTOM FEATURE
        for nth, feature in enumerate(config.features):
            feature_instance = feature_options.create(feature.name, feature.params)
            pipeline_components.append((f'{nth}_{feature.name}', feature_instance))

        # HIDDEN -- DROP ROWS WITH NANS
        feature_instance = feature_options.create('drop_nan_rows')
        pipeline_components.append(('hidden_drop_nans', feature_instance))

    ########################################################################################
    ### GENERATE LABELS WITH THE CURRENT SET OF FEATURES

        labels: dict[str, list] = generate_segment_labels(
            dataset, 
            pipeline_components, 
            config.training.label_column
        )

    ########################################################################################
    ### ADD SECOND LAYER OF FEATURES

        # HIDDEN -- EXTRACT FEATURE COLUMNS
        feature_instance = feature_options.create('extract_columns', { 'columns': config.training.feature_columns })
        pipeline_components.append(('hidden_feature_extraction', feature_instance))

        # HIDDEN -- CONVERT DATAFRAME TO FLAOT MATRIX
        feature_instance = feature_options.create('to_float_matrix')
        pipeline_components.append(('hidden_to_matrix', feature_instance))

    ########################################################################################
    ### ADD SCALER & MODEL

        scaler_instance = scaler_options.create(config.training.scaler.name, config.training.scaler.params)
        pipeline_components.append(('scaler', scaler_instance))

        model_instance = model_options.create(config.training.model.name, config.training.model.params)
        pipeline_components.append(('model', model_instance))

    ########################################################################################
    ### TRAIN THE PIPELINE

        pipeline = Pipeline(pipeline_components)
        pipeline.fit(dataset['train'], labels['train'])

    ########################################################################################
    ### EVALUATE PIPELINE

        # CHECK MODEL SCORE FOR EACH DATASET SEGMENT
        train_score = round(pipeline.score(dataset['train'], labels['train']), 4)
        test_score = round(pipeline.score(dataset['test'], labels['test']), 4)
        valid_score = round(pipeline.score(dataset['validate'], labels['validate']), 4)

        train_len = len(dataset['train'])
        test_len = len(dataset['test'])
        validate_len = len(dataset['validate'])
        total_len = train_len + test_len + validate_len

        print('--------')
        print(f'DATASET LEN:\t\t{total_len}')
        print(f'TRAIN SEGMENT:\t\t{train_len}')
        print(f'TEST SEGMENT:\t\t{test_len}')
        print(f'VALIDATE SEGMENT:\t{validate_len}')
        
        print('--------')
        print(f'TRAIN SCORE:\t\t{train_score}')
        print(f'TEST SCORE:\t\t{test_score}')
        print(f'VALIDATE SCORE:\t\t{valid_score}')

        print('--------')
        print('SKLEARN PIPELINE STEPS:')
        for step in pipeline.steps:
            print(f'   {step}')
        print('--------')

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

if __name__ == '__main__':
    run()
