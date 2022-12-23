import logging
import multiprocessing
import os
# import threading
# import subprocess
# import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import Queue, current_process
from multiprocessing.dummy import Pool

from tasks import (
    DataFetchingTask,
    DataCalculationTask,
    DataAggregationTask,
    DataAnalyzingTask,
)
from utils import CITIES

logger = logging.getLogger(__name__)


def forecast_weather():
    """
    Анализ погодных условий по городам
    """
    try:
        DataFetchingTask.save_data_to_file(CITIES)
    except Exception:
        raise Exception('Ошибка при получении данных из API')
    # workers_cpu = multiprocessing.cpu_count() - 1
    # logger.info(f"Количество pool workers {workers_cpu}")
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    process_producer = DataCalculationTask(queue)
    process_consumer = DataAggregationTask(queue)
    process_producer.start()
    process_producer.join()
    process_consumer.start()
    process_consumer.join()

    # with Pool(processes=workers_cpu) as pool:
    #     tasks_timeout = len(cities)
    #     calculation_result = pool.starmap(calculation.run, data)
    #     # aggregation_result = pool.apply_async(aggregation.run)
    #     calculation_result.wait(timeout=tasks_timeout)

    # if not calculation_result.ready():
    #     logger.error("f'Tasks calculation doesnt completed after timeout={tasks_timeout} seconds")
    #     raise TimeoutError
    # queue.put(None)
    # aggregation.wait()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    forecast_weather()
