"""Project pipelines."""
from typing import Dict
import os
import logging

from kedro.pipeline import Pipeline
from .pipelines import get_pipelines

log = logging.getLogger(__name__)

def register_pipelines() -> Dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from a pipeline name to a ``Pipeline`` object.
    """

    pipelines = get_pipelines()
    log.info("automated pipelines:\n  - " + "\n  - ".join([n for n, f in pipelines]))
    pipeline_dict = {n: f for n, f in pipelines}
    pipeline_dict.update({"__default__": sum([f for n, f in pipelines])})
    return pipeline_dict
