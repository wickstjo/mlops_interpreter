from common.testing import base_unittest
from pydantic import BaseModel, Field

##############################################################################################################
##############################################################################################################

class input_schema(BaseModel):
    sequence_ratio: list[dict[str, float]] = Field(min_length=3, max_length=3)

##############################################################################################################
##############################################################################################################

# APPLY PIPELINE FEATURES ON SUBSET
# AND EXTRACT LABEL COLUMN FROM THE RESULTING DATAFRAME
def generate_segment_labels(dataset_segments: dict[str, list[dict]], pipeline: list[tuple], label_column: str):
    container = {}

    for segment_name, subset in dataset_segments.items():

        # TODO: TEST IF THIS IS NECESSARY
        # TODO: TEST IF THIS IS NECESSARY
        # TODO: TEST IF THIS IS NECESSARY
        cloned_dataset = [x for x in subset]

        # APPLY EACH FEATURE
        for _, feature in pipeline:
            cloned_dataset = feature.transform(cloned_dataset)
        
        # EXTRACT THE LABEL COLUMN
        labels = cloned_dataset[label_column].tolist()
        container[segment_name] = labels

    return container

##############################################################################################################
##############################################################################################################

class tests(base_unittest):
    def test_00_input_schema(self):
        pass