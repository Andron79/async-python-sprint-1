import requests

from api_client import YandexWeatherAPI


class DataFetchingTask:

    def __int__(self, url):
        self.url = url

    def fetch_data(self):
        # response = requests.get(self.url)
        # data = response.content

        city_name = "MOSCOW"
        ywAPI = YandexWeatherAPI()
        resp = ywAPI.get_forecasting(city_name)


class DataCalculationTask:
    pass


class DataAggregationTask:
    pass


class DataAnalyzingTask:
    pass
