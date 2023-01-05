import json
import logging

logger = logging.getLogger(__name__)

CITIES = {
    "MOSCOW": "https://code.s3.yandex.net/async-module/moscow-response.json",
    "PARIS": "https://code.s3.yandex.net/async-module/paris-response.json",
    "LONDON": "https://code.s3.yandex.net/async-module/london-response.json",
    "BERLIN": "https://code.s3.yandex.net/async-module/berlin-response.json",
    "BEIJING": "https://code.s3.yandex.net/async-module/beijing-response.json",
    "KAZAN": "https://code.s3.yandex.net/async-module/kazan-response.json",
    "SPETERSBURG": "https://code.s3.yandex.net/async-module/spetersburg-response.json",
    "VOLGOGRAD": "https://code.s3.yandex.net/async-module/volgograd-response.json",
    "NOVOSIBIRSK": "https://code.s3.yandex.net/async-module/novosibirsk-response.json",
    "KALININGRAD": "https://code.s3.yandex.net/async-module/kaliningrad-response.json",
    "ABUDHABI": "https://code.s3.yandex.net/async-module/abudhabi-response.json",
    "WARSZAWA": "https://code.s3.yandex.net/async-module/warszawa-response.json",
    "BUCHAREST": "https://code.s3.yandex.net/async-module/bucharest-response.json",
    "ROMA": "https://code.s3.yandex.net/async-module/roma-response.json",
    "CAIRO": "https://code.s3.yandex.net/async-module/cairo-response.json",
}
ERR_MESSAGE_TEMPLATE = "Something wrong. Please contact with mentor."

MIN_MAJOR_PYTHON_VER = 3
MIN_MINOR_PYTHON_VER = 9

# time limit
MIN_HOUR = 9
MAX_HOUR = 19

# json files
CITIES_DATA_FILE = 'result_cities_data.json'
API_DATA_FILE = 'saved_data_from_api.json'


def read_json_data_from_file(filename: str = None) -> json:
    try:
        with open(filename, 'r') as f:
            data = json.loads(f.read())
    except FileNotFoundError:
        raise Exception(f'Файл {filename} не существует')
    return data


def save_json_data_to_file(json_data: dict = None, filename: str = None):
    with open(filename, 'w') as f:
        json.dump(json_data, f, sort_keys=True, indent=4)


GOOD_WEATHER = [
    'clear',
    'partly-cloudy',
    'cloudy',
    'overcast',
]


def check_python_version():
    import sys

    if (
            sys.version_info.major < MIN_MAJOR_PYTHON_VER
            or sys.version_info.minor < MIN_MINOR_PYTHON_VER
    ):
        raise Exception(
            "Please use python version >= {}.{}".format(
                MIN_MAJOR_PYTHON_VER, MIN_MINOR_PYTHON_VER
            )
        )
