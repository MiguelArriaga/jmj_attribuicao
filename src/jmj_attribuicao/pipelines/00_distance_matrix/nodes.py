import pandas as pd
import logging
log = logging.getLogger(__name__)


def generate_distance_matrix(parishes: pd.DataFrame) -> pd.DataFrame:
    """Processes the parishes data to compute the distance matrix.
    Can be replaced with a better distance matrix.

    Args:
        parishes: Raw data.

    Returns:

    """
    distance_matrix = pd.DataFrame(index=parishes.index, columns=parishes.index)
    for irow, row in parishes.iterrows():
        xs = parishes["x"] - row["x"]
        ys = parishes["y"] - row["y"]
        dist = (xs ** 2 + ys ** 2) ** 0.5
        distance_matrix[irow] = dist
    return distance_matrix

