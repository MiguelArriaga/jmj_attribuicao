import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging

log = logging.getLogger(__name__)

COLORS = {"EN": 'b', "IT": 'g', "DE": 'r', "ES": "y", "FR": "c", "OT": "m"}

def generate_initial_seeds(parishes: pd.DataFrame,
                      pilgrims: pd.DataFrame,
                      distance_matrix: pd.DataFrame):
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

    language_seeds["seed"] = language_seeds["seed"].astype(str)
    all_neighbours.index = all_neighbours.index.astype(str)
    seeds = language_seeds["seed"].values

    neighbour_seeds = all_neighbours.applymap(lambda x: str(x) in seeds)
    closest = []
    for pid in distance_matrix.columns:
        if str(pid) in seeds:
            closest_seed = str(pid)
        else:
            closest_seed = str(all_neighbours.loc[neighbour_seeds[pid], pid].iloc[0])
        closest.append([pid,closest_seed])

    closest_seed_parishes = pd.DataFrame(closest, columns=["pid", "closest_seed"]).set_index("pid")
    closest_seed_parishes=closest_seed_parishes.merge(
        language_seeds.reset_index().set_index("seed")[["glanguage"]],
        how="left",
        left_on="closest_seed",
        right_index=True)

    return closest_seed_parishes

def plot_regions(parishes, language_seeds, closest_seed_parishes):
    parishes.index = parishes.index.astype(str)
    plt.show()
    plt.ion()
    fig, ax = plt.subplots(1, 1)
    # ax.scatter(parishes["x"], parishes["y"], color="k", s=50)
    for lang, row in language_seeds.iterrows():
        par = str(row["seed"])
        ax.scatter(parishes.at[par, "x"], parishes.at[par, "y"], color=COLORS[lang], marker="*", label=lang, s=50)
    ax.legend()
    ax.axis('square')
    ax.set_aspect('equal')

    pl = parishes.join(closest_seed_parishes)
    for ir, row in pl.iterrows():
        ax.scatter(row["x"], row["y"], color=COLORS[row["glanguage"]], s=200, label=row["glanguage"],
                   alpha=0.5)
    # plt.legend()
    return fig


