from kedro.pipeline import Pipeline, node
from .N0_pre_processing import generate_distance_matrix, generate_neighbours_catalog
from .N1_region_construction import generate_initial_seeds, optimize_region_sizes
from .N2_allocation_initialization import initialize_allocation
from .P0_plot_functions import plot_regions

all_pplns = {
    "generate_distance_matrix": Pipeline([
        node(
            func=generate_distance_matrix,
            inputs="parishes",
            outputs="distance_matrix",
            name="generate_distance_matrix_node",
        ),
    ]),

    "generate_neighbours_catalog": Pipeline([
        node(
            func=generate_neighbours_catalog,
            inputs="distance_matrix",
            outputs="all_neighbours",
            name="generate_neighbours_catalog",
        ),
    ]),

    "generate_initial_seeds": Pipeline([
        node(
            func=generate_initial_seeds,
            inputs=["parishes","pilgrims","distance_matrix"],
            outputs="initial_language_seeds",
            name="generate_initial_seeds",
        ),
    ]),

    "optimize_region_sizes": Pipeline([
        node(
            func=optimize_region_sizes,
            inputs=["parishes", "initial_language_seeds", "distance_matrix", "all_neighbours"],
            outputs=["language_region_parishes","language_seeds"],
            name="optimize_region_sizes",
        ),
    ]),

    "plot_regions": Pipeline([
        node(
            func=plot_regions,
            inputs=["parishes", "language_seeds", "language_region_parishes"],
            outputs="regions_plot",
            name="plot_regions",
        ),
    ]),

    "initialize_allocation": Pipeline([
        node(
            func=initialize_allocation,
            inputs=["parishes","pilgrims", "all_neighbours", "distance_matrix", "language_seeds", "language_region_parishes"],
            outputs="initial_allocation",
            name="initialize_allocation",
        ),
    ]),



}
