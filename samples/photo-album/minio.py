from pathlib import Path
from os import getenv


_conf_folder = '/configurations/devMinio'
is_deploy = Path(_conf_folder).exists()

_params_keys = ["accesskey", "secretkey", "endpoint_url", "s3_bucket_name"]

def _get_key_value(key):
    if (is_deploy):
        return Path(f'{_conf_folder}/{key}').read_text()
    else:
        envvar_name = f'MINIO_{key.upper()}'
        return getenv(envvar_name, '')

params = { k: _get_key_value(k) for k in _params_keys }