import logging
import multiprocessing


from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)
from utils import CITIES, CITIES_DATA_FILE, API_DATA_FILE

logger = logging.getLogger(__name__)


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    try:
        DataFetchingTask.api_data_to_file(CITIES, filename=API_DATA_FILE)
    except Exception:
        raise Exception('Ошибка при получении данных из API')
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    process_producer = DataCalculationTask(queue, filename=API_DATA_FILE)
    process_consumer = DataAggregationTask(queue, filename=CITIES_DATA_FILE)
    process_producer.start()
    process_producer.join()
    process_consumer.start()
    process_consumer.join()
    DataAnalyzingTask.rating_analysis(filename=CITIES_DATA_FILE)


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    forecast_weather()
