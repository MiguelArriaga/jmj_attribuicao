import pandas as pd
import logging

log = logging.getLogger(__name__)


def generate_distance_matrix(parishes: pd.DataFrame) -> pd.DataFrame:
    """Processes the parishes data to compute the distance matrix.
    Can be replaced with a better distance matrix.
    """
    distance_matrix = pd.DataFrame(index=parishes.index, columns=parishes.index)
    for irow, row in parishes.iterrows():
        xs = parishes["x"] - row["x"]
        ys = parishes["y"] - row["y"]
        dist = (xs ** 2 + ys ** 2) ** 0.5
        distance_matrix[irow] = dist
    return distance_matrix


def find_neighbours(pid, distance_matrix: pd.DataFrame):
    return distance_matrix[pid].sort_values().index.values[1:]  # remove itself

def generate_neighbours_catalog(distance_matrix: pd.DataFrame) -> pd.DataFrame:
    """

    Args:
        distance_matrix:

    Returns:
        neighbours DataFrame - Each column contains the distances to a specific parish. So neighbours["33"] is a sequence
                               of parishes from the closest to parish "33" to the furthest.
    """
    distance_matrix.columns = distance_matrix.columns.astype(int)
    all_neighbours_dict = {}

    for pid in distance_matrix.index.values:
        all_neighbours_dict[pid] = find_neighbours(pid, distance_matrix)

    all_neighbours = pd.DataFrame(all_neighbours_dict)
    all_neighbours.index.name = "d_order"

    return all_neighbours
