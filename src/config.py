from src.utils import get_config
from pathlib import Path

CONFIG_PATH = 'data/data.yaml'
configs = get_config(CONFIG_PATH)

END_DATE = configs['utils']['end_date']
BEG_DATE = configs['utils']['beg_date']
INPUT_DIR = Path(configs['utils']['input_dir'])