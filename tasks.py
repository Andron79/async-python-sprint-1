import logging
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue, Process
from operator import itemgetter
from typing import Optional, Any
from pydantic import parse_obj_as
from api_client import YandexWeatherAPI
from models import ForecastsDetailModel
from utils import (
    MIN_HOUR,
    MAX_HOUR,
    GOOD_WEATHER,
    save_json_data_to_file,
    read_json_data_from_file
)

logger = logging.getLogger(__name__)


class DataFetchingTask:
    @staticmethod
    def _fetch_data(city_name: str) -> dict[Any, Any]:
        yw_api = YandexWeatherAPI()
        result = parse_obj_as(ForecastsDetailModel, yw_api.get_forecasting(city_name))
        return {city_name: result.dict()}

    @staticmethod
    def api_data_to_file(city_data: dict = None, filename: str = None):
        """
        Сохранение данных, полученных из API в файл
        """
        # cities = city_data.keys()
        json_data = {}
        with ThreadPoolExecutor() as executor:
            futures = executor.map(DataFetchingTask._fetch_data, city_data)
            for city in futures:
                json_data.update(city)
        logger.info('Данные из API успешно получены')
        save_json_data_to_file(json_data=json_data, filename=filename)
        logger.info(f'Данные по городам сохранены в файл {filename}')


class DataCalculationTask(Process):
    def __init__(self, queue: Optional[Queue] = None, filename: str = None):
        super().__init__()
        self.queue = queue
        self.filename = filename

    @staticmethod
    def get_weather_condition(weather_condition: str) -> bool:
        return weather_condition in GOOD_WEATHER

    @staticmethod
    def day_temperature_and_condition_calc(data) -> dict:
        """
        Вычисление средней температуры и благоприятных часов по каждому дню
        """
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
                                'day_avg_temp': avg_temp,
                                'day_comfort_hours': comfort_hours
                            }
                    }
                )
        return {
            city: data_context
        }

    def run(self):
        data = read_json_data_from_file(filename=self.filename)
        cities = data.keys()
        for city in cities:
            city_data = {city: data[city]['forecasts']}
            result = self.day_temperature_and_condition_calc(city_data)
            if self.queue:
                self.queue.put(result)
            else:
                return result


class DataAggregationTask(Process):
    def __init__(self, queue: Optional[Queue] = None, filename: str = None):
        super().__init__()
        self.queue = queue
        self.filename = filename

    @staticmethod
    def aggregation_city_data(city_data: dict) -> dict:
        """
        Агрегация средней температуры и благоприятных дней к каждому городу за все дни
        """
        day_count = 0
        total_avg_temp = 0
        total_comfort_hors = 0
        for dates in city_data.values():
            for date in dates.values():
                day_count += 1
                total_avg_temp += date['day_avg_temp']
                total_comfort_hors += date['day_comfort_hours']
        city_data[list(city_data.keys())[0]]['total_avg_temp'] = round(total_avg_temp / day_count, 2)
        city_data[list(city_data.keys())[0]]['total_comfort_hors'] = total_comfort_hors
        return city_data

    def run(self):
        all_cities_data = {}
        while True:
            if self.queue.empty():
                save_json_data_to_file(
                    json_data=all_cities_data,
                    filename=self.filename
                )
                logger.info(f'Данные по городам сохранены в файл {self.filename}')
                break
            city_data = self.queue.get()
            all_cities_data.update(self.aggregation_city_data(city_data))


class DataAnalyzingTask:
    @staticmethod
    def rating_analysis(filename: str = None):
        """
        Вычисление и вывод рейтинга по городам
        """
        cities_data = read_json_data_from_file(filename=filename)
        total_cities_list = [
            (city, city_data['total_comfort_hors'], city_data['total_avg_temp'],)
            for city, city_data in cities_data.items()
        ]
        rating_all_cities = sorted(total_cities_list, key=itemgetter(2), reverse=True)
        best_city = rating_all_cities[0]
        matching_rating_cities_list = []
        for city in rating_all_cities:
            if city[1] >= best_city[1] and city[2] >= best_city[2]:
                matching_rating_cities_list.append(city)
                print(f'Победитель рейтинга {city[0]} средняя температура за период составила {city[2]} градуса, '
                      f'кол-во благоприятных дней: {city[1]}')
        return matching_rating_cities_list
