from hydra import compose, initialize
from omegaconf import OmegaConf

with initialize(version_base=None, config_path="",):
    CFG = compose(config_name="config")
