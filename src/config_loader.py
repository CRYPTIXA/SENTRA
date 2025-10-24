import yaml
import os

def load_config(file_path="config/config.yaml"):

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File {file_path} not found")

    with open(file_path, "r") as f:
        config = yaml.safe_load(f)


    return config

config = load_config()

telegram_token = config["telegram_token"]
whale_threshold = config["whale_threshold_usd"]

rpc_urls = config.get("rpc_urls", {})
infura_url = rpc_urls.get("infura")
alchemy_url = rpc_urls.get("alchemy")


nhost_api_url = config["nhost"]["api_url"]
nhost_admin_secret = config["nhost"]["admin_secret"]