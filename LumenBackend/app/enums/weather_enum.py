from enum import Enum


class Weather(Enum):
    CLEAR = 0
    SNOW = 0.5
    RAIN = 1

    @staticmethod
    def from_value(value: float):
        for weather in Weather:
            if weather.value == value:
                return weather
        raise ValueError("Invalid weather value")
