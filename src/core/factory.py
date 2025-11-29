from .engines.rapid_engine import RapidEngine


def create_engine(engine_type: str, config):
    if engine_type == "rapid":
        return RapidEngine(config)
    else:
        raise ValueError("Unknown engine type")