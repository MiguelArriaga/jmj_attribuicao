"""Project pipelines."""
from typing import Dict
import os
import logging

from kedro.pipeline import Pipeline
from .pipelines.all_pipelines import all_pplns

log = logging.getLogger(__name__)

def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """

    ppln_iter = all_pplns.items()
    log.info("automated pipelines:\n  - " + "\n  - ".join([n for n, f in ppln_iter]))
    pipeline_dict = {n: f for n, f in ppln_iter}
    pipeline_dict.update({"__default__": sum([f for n, f in ppln_iter])})
    return pipeline_dict
