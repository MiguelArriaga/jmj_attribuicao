from kedro.pipeline import Pipeline, node
from .nodes import generate_initial_seeds, generate_preliminary_regions, plot_regions

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=generate_initial_seeds,
                inputs=["parishes","pilgrims","distance_matrix"],
                outputs="initial_language_seeds",
                name="generate_seed_parishes",
            ),
            node(
                func=generate_preliminary_regions,
                inputs=["distance_matrix","all_neighbours","initial_language_seeds"],
                outputs="closest_seed_parishes",
                name="generate_preliminary_regions",
            ),
            node(
                func=plot_regions,
                inputs=["parishes","initial_language_seeds","closest_seed_parishes"],
                outputs="regions_plot",
                name="plot_regions",
            ),
        ]
    )
