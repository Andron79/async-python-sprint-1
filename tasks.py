import concurrent
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue, current_process, parent_process, Process
from pprint import pprint
from typing import Optional, Dict, Any

from pydantic import parse_obj_as

from api_client import YandexWeatherAPI
from models import CityDetailModel, ForecastsDetailModel
from utils import MIN_HOUR, MAX_HOUR, GOOD_WEATHER

logger = logging.getLogger(__name__)


class DataFetchingTask:
    @staticmethod
    def _fetch_data(city_name: str) -> dict[Any, Any]:
        ywAPI = YandexWeatherAPI()
        result = parse_obj_as(ForecastsDetailModel, ywAPI.get_forecasting(city_name))
        return {city_name: result.dict()}

    @staticmethod
    def save_data_to_file(city_data: dict = None):
        cities = city_data.keys()
        workers = len(cities)
        json_data = {}
        logger.info(f"Потоков - {workers}")
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = executor.map(DataFetchingTask._fetch_data, city_data)
            for city in futures:
                json_data.update(city)
        logger.info('Данные получены из API успешно получены')
        with open('data.json', 'w') as f:
            json.dump(json_data, f, sort_keys=True, indent=4)
            logger.info('Данные сохранены во временный файл')

    @staticmethod
    def get_data():
        with open('data.json', 'r') as f:
            data = json.loads(f.read())
        return data


class DataCalculationTask(Process):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    @staticmethod
    def get_weather_condition(weather_condition: str) -> bool:
        return weather_condition in GOOD_WEATHER

    @staticmethod
    def day_temperature_and_condition_calc(data: CityDetailModel) -> dict:

        pprint(data)
        cities = list(data)
        print(cities)
        # logger.info(forecasts['forecast']['forecasts'])
        hours = data['forecast']['forecasts'][0]['hours']
        temperature_by_hour = []
        comfort_hours = 0
        if len(hours) != 24:
            raise ValueError
        for hour in hours:
            if MIN_HOUR <= int(hour['hour']) <= MAX_HOUR:
                temperature_by_hour.append(int(hour['temp']))
                if DataCalculationTask.get_weather_condition(hour['condition']):
                    comfort_hours += 1

        context = {
            'city': data.city,
            'avg_temp': sum(temperature_by_hour) / len(temperature_by_hour),
            'comfort_hours': comfort_hours
        }
        return context

    @staticmethod
    def all_days_calc(data: CityDetailModel) -> dict:
        forecasts = data.dict()
        all_days = forecasts['forecast']['forecasts']

    # def _calc(self, data):
    #     forecasts = data.dict()
    # logger.info(forecasts['forecast']['forecasts'][0])
    # city_name = data.city
    # logger.info(forecasts)
    # logger.info(forecasts['forecast']['forecasts'][0]['date'])
    # logger.info(forecasts['forecast']['forecasts'][0]['hours'])
    # current_proc = current_process()

    # city = df([city_name, None], columns=["city"])
    # logger.info(city)
    # return forecasts

    def run(self):
        # print(data)
        data = DataFetchingTask.get_data()
        result = self.day_temperature_and_condition_calc(data)
        print(result)
        # result = self.day_temperature_and_condition_calc(data)
        # logger.info(result)
        # result = self._calc(data)
        # if self.queue:
        #     self.queue.put(result)
        #     logger.info(current_process().pid)
        # else:
        # return result


class DataAggregationTask:
    def __init__(self, filename: str = None, queue: Optional[Queue] = None):
        super().__init__()
        self.queue = queue
        # self.filename = self._check_file(filename)

    def run(self):
        df_lists = []
        while True:
            if self.queue.empty():
                logger.info('Очередь пуста')
                self.queue.join()
                # pd.DataFrame.from_dict(df_lists).to_csv('results.csv')  # noqa
                # logger.info(msg=MSG_CSV_SAVED)
                # break
            if self.queue.full():
                logger.info('Очередь заполнена')
            item = self.queue.get()
            # df_lists.extend(item['forecast']['forecasts'])

            # logger.info(item)
            # logger.info(msg=MSG_GET_ITEM_QUEUE.format(item=item))


class DataAnalyzingTask:
    pass
