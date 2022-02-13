import pandas as pd
import numpy as np
import logging

log = logging.getLogger(__name__)


def generate_initial_seeds(parishes: pd.DataFrame,
                           pilgrims: pd.DataFrame,
                           distance_matrix: pd.DataFrame):
    """This function makes a circle with equidistant points (one for each language) and finds the nearest parish."""

    mean_distance = distance_matrix.mean().mean()
    center = parishes[["x", "y"]].mean()
    seed_radius = 2 / 3 * mean_distance

    initial_language_seeds = pilgrims.groupby("glanguage").sum()[["gsize"]]
    num_languages = len(initial_language_seeds)
    delta_angle = 2 * 3.1415 / num_languages
    initial_language_seeds["seed"] = 0
    for i, lang in enumerate(initial_language_seeds.index.values):
        x = center["x"] + seed_radius * np.cos(i * delta_angle)
        y = center["y"] + seed_radius * np.sin(i * delta_angle)
        parish = ((parishes["x"] - x) ** 2 + (parishes["y"] - y) ** 2).sort_values().index[0]
        initial_language_seeds.at[lang, "seed"] = str(parish)
    return initial_language_seeds


def generate_preliminary_regions(distance_matrix: pd.DataFrame,
                                 all_neighbours: pd.DataFrame,
                                 language_seeds: pd.DataFrame):
    """Generate regions based on voronoi splitting."""

    distance_matrix.columns = distance_matrix.columns.astype(int)
    all_neighbours.columns = all_neighbours.columns.astype(int)

    seeds = language_seeds["seed"].values

    # go to the neighbours table and make a new table with True when the value is a language seed
    neighbour_seeds = all_neighbours.applymap(lambda x: x in seeds)

    closest = []
    for pid in distance_matrix.columns:
        if pid in seeds:
            # the parish is an actual seed
            closest_seed = pid
        else:
            # select only the rows that are seeds for the neighbours of the parish and then take the top one (the closest)
            closest_seed = all_neighbours.loc[neighbour_seeds[pid], pid].iloc[0]
        closest.append([pid, closest_seed])

    closest_seed_parishes = pd.DataFrame(closest, columns=["pid", "closest_seed"]).set_index("pid")
    closest_seed_parishes = closest_seed_parishes.merge(
        language_seeds.reset_index().set_index("seed")[["glanguage"]],
        how="left",
        left_on="closest_seed",
        right_index=True)

    return closest_seed_parishes


def get_cost_matrix(seeds, weights, distance_matrix, weight_method=0):
    """The 'cost' (i.e. distance) between the seeds and the other parishes."""

    distance_to_seeds = distance_matrix.loc[seeds, :]

    if weight_method == 0:
        cost_matrix = distance_to_seeds

    elif weight_method == 1:
        inv_dist = 1 / (distance_to_seeds + 0.001)
        normalized_distance_score = inv_dist.div(inv_dist.sum())
        weighted_score = normalized_distance_score.mul(weights, axis=0)
        cost_matrix = 1 / weighted_score

    return cost_matrix


def custom_sigmoid(x, scaling=0.5):
    return ((2 / (1 + np.exp(-x * scaling))) - 1) * 0.1 + 0.1


def optimize_region_sizes(parishes: pd.DataFrame,
                          initial_language_seeds: pd.DataFrame,
                          distance_matrix: pd.DataFrame,
                          all_neighbours: pd.DataFrame,
                          ):
    """Generate regions based on weights"""

    distance_matrix.columns = distance_matrix.columns.astype(int)
    all_neighbours.columns = all_neighbours.columns.astype(int)

    language_seeds = initial_language_seeds.copy()
    language_seeds["weights"] = language_seeds["gsize"] / language_seeds["gsize"].sum()
    language_seeds["csize"] = 0

    target_ratio = language_seeds["gsize"].sum() / parishes["psize"].sum()
    weight_method = 1

    for _ in range(15):
        seeds = language_seeds["seed"].values
        weights = language_seeds["weights"].values

        cost_matrix = get_cost_matrix(seeds, weights, distance_matrix, weight_method=weight_method)
        seed_attribution = cost_matrix.idxmin().rename("closest_seed").to_frame()

        # Adjust weights (increase weights of lang below target and decrease others)
        cluster_sizes = seed_attribution.join(parishes).groupby("closest_seed")["psize"].sum()
        language_seeds["csize"] = language_seeds.merge(cluster_sizes, left_on="seed", right_index=True)["psize"]
        capacity_measure = ((language_seeds.gsize / language_seeds.csize) - target_ratio) / target_ratio
        log.info("capacity measure (group_size/cluster_size)-target_ratio: " + str(np.linalg.norm(capacity_measure)))
        w_scaling = capacity_measure.apply(custom_sigmoid)
        new_weights = w_scaling * language_seeds["weights"]
        language_seeds["weights"] = new_weights / new_weights.sum()

        # Adjust seed location
        attr_by_cluster = seed_attribution.reset_index().set_index("closest_seed")
        new_seeds = []
        for s in seeds:
            p_in_c = attr_by_cluster.loc[s, "index"].values
            cluster_cost_matrix = get_cost_matrix(p_in_c, 1, distance_matrix.loc[p_in_c, p_in_c],
                                                  weight_method=weight_method)
            best_seed = cluster_cost_matrix.sum().idxmin()
            new_seeds.append(best_seed)

        language_seeds["seed"] = new_seeds

    # Final
    seeds = language_seeds["seed"].values
    weights = language_seeds["weights"].values
    cost_matrix = get_cost_matrix(seeds, weights, distance_matrix, weight_method=weight_method)
    seed_attribution = cost_matrix.idxmin().rename("closest_seed").to_frame()

    log.info("Final Capacities: \n" +
             "Target: " + str(target_ratio) + "\n"+
             str(language_seeds.gsize / language_seeds.csize))

    seed_to_lang_map = language_seeds.reset_index().set_index("seed")[["glanguage"]]
    language_region_parishes = seed_attribution.merge(seed_to_lang_map, left_on="closest_seed", right_index=True,
                                                      how="left")

    # from .P0_plot_functions import plot_regions
    # fig = plot_regions(parishes, language_seeds, language_region_parishes)
    # import matplotlib.pyplot as plt
    # plt.show()

    return language_region_parishes, language_seeds
