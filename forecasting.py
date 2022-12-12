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
    cities = CITIES.keys()
    workers = len(cities)
    logger.debug("Thread workers count %s", workers)
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = executor.map(DataFetchingTask.fetch_data, CITIES)
        data = list(futures)
    workers_cpu = multiprocessing.cpu_count() - 1
    logger.info(f"Pool workers count {workers_cpu}")
    manager = multiprocessing.Manager()
    queue = manager.Queue()
    calculation = DataCalculationTask(queue=queue)
    aggregation = DataAggregationTask(queue=queue)

    with Pool(processes=workers_cpu) as pool:
        tasks_timeout = len(cities)
        calculation_result = pool.map_async(calculation.run, data)
        aggregation_result = pool.apply_async(aggregation.run)
        calculation_result.wait(timeout=tasks_timeout)
        logger.info(aggregation_result)
        logger.info(calculation_result)
        if not calculation_result.ready():
            logger.error("f'Tasks calculation doesnt completed after timeout={tasks_timeout} seconds")
            raise TimeoutError
        queue.put(None)
        # aggregation_result.wait()


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S")
    forecast_weather()
