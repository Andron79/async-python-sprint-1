import logging
import os

from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask
)

from utils import (
    CITIES,
    API_DATA_FILE,
    read_json_data_from_file
)

logger = logging.getLogger(__name__)

TEST_CITIES = {
    'ABUDHABI': CITIES['ABUDHABI'],
    'SPETERSBURG': CITIES['SPETERSBURG']
}
TEST_API_DATA_FILE = f'TEST_{API_DATA_FILE}'
TEST_DATA_JSON_FILE = 'tests/tests_data/data.json'
TEST_CITIES_DATA_FILE = 'tests/tests_data/cities_data.json'


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

    cities_data = read_json_data_from_file(filename=TEST_CITIES_DATA_FILE)

    cities_rating = DataAnalyzingTask.all_cities_rating(cities_data)
    assert cities_data == cities_rating, 'Ошибка добавления рейтинга - ERROR!'
    logger.info('Рейтинг добавлен верно - OK!')

    os.remove(TEST_API_DATA_FILE)
