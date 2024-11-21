from common import misc
from pandas import DataFrame

from actions.data_retrieval.load_dataset import load_dataset
from actions.feature_engineering.to_dataframe.to_dataframe import to_dataframe
from actions.feature_engineering.shift_column.shift_column import shift_column
from actions.feature_engineering.stochastic_k.stochastic_k import stochastic_k
from actions.feature_engineering.to_feature_matrix.to_feature_matrix import to_feature_matrix
from actions.feature_engineering.drop_nan_rows.drop_nan_rows import drop_nan_rows

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

def run():

    # LOAD EXPERIMENT YAML
    experiment_config: dict = misc.load_yaml('config.yaml')
    pipeline_components = []

    # LOAD A SAMPLE DATASET
    dataset_config: dict = experiment_config['dataset']
    dataset: list[dict] = load_dataset(dataset_config, unittesting=200)

    ########################################################################################
    ########################################################################################

    # FEATURE MAPPING
    available_features = {
        'shift_column': shift_column,
        'stochastic_k': stochastic_k,
    }

    # CONVERT INPUT TO DATAFRAME
    pipeline_components.append(('hidden_input_conversion', to_dataframe()))

    # ADD EACH CUSTOM FEATURE
    for nth, block in enumerate(experiment_config['feature_engineering']['features']):
        feature_name = block['feature_name']
        feature_params = block['feature_params']

        feature_instance = available_features[feature_name](feature_params)
        pipeline_components.append((f'yaml_feature_{nth+1}', feature_instance))

    # DROP ALL ROWS WITH NAN VALUES
    pipeline_components.append(('hidden_drop_nan', drop_nan_rows()))

    ########################################################################################
    ########################################################################################

    # CREATE A TEMP DATAFRAME TO GENERATE TRAINING LABELS
    temp_dataset = DataFrame(dataset)

    # APPLY EACH FEATURE
    for block in pipeline_components:
        _, feature = block
        feature.transform(temp_dataset)

    # EXTRACT THE LABEL COLUMN
    label_column = experiment_config['model_training']['label_column']
    labels = temp_dataset[label_column].tolist()
    
    # EXTRACT THE TIMESTAMPS FOR ROWS WITH LABELS
    # THEN DELETE THE TEMP DATAFRAME TO FREE UP MEMORY
    timestamps_with_labels = temp_dataset['timestamp'].tolist()
    del temp_dataset

    # FILTER OUT ALL DATASET ROWS WITHOUT LABELS
    dataset = [x for x in dataset if x['timestamp'] in timestamps_with_labels]

    ########################################################################################
    ########################################################################################

    # CONVERT DATAFRAME TO FLOAT MATRIX
    pipeline_components.append(('hidden_ouput_conversion', to_feature_matrix({
        'feature_columns': experiment_config['model_training']['feature_columns']
    })))

    # ADD THE SCALER AND MODEL
    pipeline_components.append(('standard_scaler', StandardScaler()))
    pipeline_components.append(('linreg_model', LinearRegression()))

    # CREATE THE PIPELINE
    pipeline = Pipeline(pipeline_components)
    print(pipeline)

if __name__ == '__main__':
    run()
