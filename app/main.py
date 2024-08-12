import hydra
from omegaconf import DictConfig, OmegaConf

from app.api.main import run


# @hydra.main(version_base=None, config_path="./conf", config_name="config")
def main():
    run()


if __name__ == "__main__":
    main()
