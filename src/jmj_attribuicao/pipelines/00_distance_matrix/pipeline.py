from kedro.pipeline import Pipeline, node
from .nodes import generate_distance_matrix

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=generate_distance_matrix,
                inputs="parishes",
                outputs="distance_matrix",
                name="generate_distance_matrix_node",
            ),
        ]
    )