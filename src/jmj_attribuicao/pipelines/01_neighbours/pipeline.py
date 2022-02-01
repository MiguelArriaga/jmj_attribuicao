from kedro.pipeline import Pipeline, node
from .nodes import generate_neighbours_catalog

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=generate_neighbours_catalog,
                inputs="distance_matrix",
                outputs="all_neighbours",
                name="generate_neighbours_catalog",
            ),
        ]
    )