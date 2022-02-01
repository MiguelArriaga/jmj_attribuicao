import pandas as pd


def find_neighbours(pid, distance_matrix: pd.DataFrame):
    return distance_matrix[str(pid)].sort_values().index.values[1:] # remove itself


def generate_neighbours_catalog(distance_matrix: pd.DataFrame) -> pd.DataFrame:
    """

    Args:
        distance_matrix:

    Returns:
        neighbours DataFrame - Each column contains the distances to a specific parish. So neighbours["33"] is a sequence
                               of parishes from the closest to parish "33" to the furthest.
    """
    neighbours_dict = {}
    for pid in distance_matrix.index.values:
        neighbours_dict[str(pid)] = find_neighbours(pid, distance_matrix)

    return pd.DataFrame(neighbours_dict)
