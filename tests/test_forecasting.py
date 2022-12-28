import logging
import multiprocessing
import os
from multiprocessing import Queue

import pytest
import requests

from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask
)

from utils import (
    CITIES,
    API_DATA_FILE,
    read_json_data_from_file,
    CITIES_DATA_FILE
)

logger = logging.getLogger(__name__)

TEST_CITIES = {
    'ABUDHABI': CITIES['ABUDHABI'],
    'SPETERSBURG': CITIES['SPETERSBURG']
}
TEST_API_DATA_FILE = f'TEST_{API_DATA_FILE}'
TEST_DATA_JSON_FILE = 'tests/tests_data/data.json'
TEST_CITIES_DATA_FILE = 'tests/tests_data/cities_data.json'


@pytest.fixture(scope="session")
def queue() -> Queue:
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    yield queue


def test_api_url():
    for city, city_url in CITIES.items():
        response = requests.get(city_url)
        assert response.ok, f'{city} ответ из API - ERROR!'
        logger.info(f'{city} ответ из API - OK!')


def test_tasks(queue):
    DataFetchingTask.api_data_to_file(TEST_CITIES, filename=TEST_API_DATA_FILE)
    assert read_json_data_from_file(filename=TEST_API_DATA_FILE) == \
           read_json_data_from_file(TEST_DATA_JSON_FILE), "Сохраненные данные не верны - ERROR!"
    logger.info('Сохраненные данные верны - OK!')

    DataCalculationTask(queue, filename=TEST_API_DATA_FILE)

    assert read_json_data_from_file(filename=TEST_DATA_JSON_FILE) == \
           read_json_data_from_file(TEST_API_DATA_FILE), "Сохраненные данные не верны - ERROR!"
    logger.info('Сохраненные данные верны - OK!')

    DataAggregationTask(queue, filename=TEST_CITIES_DATA_FILE)

    best_cities = DataAnalyzingTask.rating_analysis(filename=TEST_CITIES_DATA_FILE)
    best_first_city = best_cities[0]
    for best_city in best_cities:
        assert best_city[2] >= best_first_city[2], \
            f'Для города {best_city[0]} средняя температура за период ниже, чем {best_first_city[0]} - ERROR'
        logger.info('Рейтинг составлен верно - OK!')

    os.remove(TEST_API_DATA_FILE)
