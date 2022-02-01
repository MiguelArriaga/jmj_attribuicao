def get_pipelines():
    import os
    import os.path as p
    import importlib

    pipelines_folder = p.dirname(p.abspath(__file__))
    dirs = [d for d in os.listdir(pipelines_folder) if (p.isdir(p.join(pipelines_folder, d)) and not d.startswith("_"))]

    pipelines = []
    for d in dirs:
        m = importlib.import_module(__package__ + "." + d)
        pipelines.append(tuple([d, m.create_pipeline()]))
    return pipelines
