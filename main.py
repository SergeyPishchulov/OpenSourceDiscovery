import hydra
from omegaconf import DictConfig, OmegaConf

from api.main import run


@hydra.main(version_base=None, config_path="./conf", config_name="config")
def main(cfg: DictConfig):
    run(cfg)


if __name__ == "__main__":
    main()
