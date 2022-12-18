import json
import logging
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue, Process
from pprint import pprint
from typing import Optional, Any

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
        logger.info('Данные из API успешно получены')
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
    def day_temperature_and_condition_calc(data) -> dict:
        temperature_by_hour = []
        data_context = {}
        city = list(data.keys())[0]
        for value in data.values():
            for date in range(len(value)):
                forecast_date = value[date]['date']
                comfort_hours = 0
                for hour in range(len(value[date]['hours'])):
                    if MIN_HOUR <= int(value[date]['hours'][hour]['hour']) < MAX_HOUR:
                        temp = value[date]['hours'][hour]['temp']
                        temperature_by_hour.append(temp)
                        if DataCalculationTask.get_weather_condition(value[date]['hours'][hour]['condition']):
                            comfort_hours += 1
                avg_temp = sum(temperature_by_hour) / len(temperature_by_hour)
                data_context.update(
                    {
                        forecast_date:
                            {
                                'avg_temp': avg_temp,
                                'comfort_hours': comfort_hours
                            }
                    })
        context = {city: data_context}
        return context

    def run(self):
        data = DataFetchingTask.get_data()
        cities = data.keys()
        for city in cities:
            city_data = {city: data[city]['forecasts']}
            result = self.day_temperature_and_condition_calc(city_data)
            if self.queue:
                self.queue.put(result)
            else:
                return result


class DataAggregationTask(Process):
    def __init__(self, queue: Optional[Queue] = None):
        super().__init__()
        self.queue = queue

    def run(self):
        while True:
            if self.queue.empty():
                logger.info('Очередь пуста')
                self.queue.join()
            if self.queue.full():
                logger.info('Очередь заполнена')
            item = self.queue.get()
            pprint(item)
            # logger.info(item)


class DataAnalyzingTask:
    pass
