#!/usr/bin/env python
from rgbmatrix import graphics
from samplebase import SampleBase
from datetime import *
import math
from constants import Constants
import time
from typing import Dict, Mapping

class MoonPhase(SampleBase):

    CYCLE_DAYS = [
        '2021-04-11',
        '2021-04-12',
        '2021-04-13',
        '2021-04-14',
        '2021-04-15',
        '2021-04-16',
        '2021-04-17',
        '2021-04-18',
        '2021-04-19',
        '2021-04-20',
        '2021-04-21',
        '2021-04-22',
        '2021-04-23',
        '2021-04-24',
        '2021-04-25',
        '2021-04-26',
        '2021-04-27',
        '2021-04-28',
        '2021-04-29',
        '2021-04-30',
        '2021-04-01',
        '2021-04-02',
        '2021-04-03',
        '2021-04-04',
        '2021-04-05',
        '2021-04-06',
        '2021-04-07',
        '2021-04-08',
        '2021-04-09',
        '2021-04-10',
    ]

    LEFT = 'left'
    RIGHT = 'right'
    PHASE_NAME = 'phase_name'
    PERCENT = 'percent'
    WAXING = 'waxing'
    WANING = 'waning'
    FIRST = 'first'

    MILESTONES = {
        'New Moon': "New",
        'Full Moon': "Full",
        'First Quarter': "First",
        'Last Quarter': "Last",
    }

    def __init__(self, *args, **kwargs):
        super(MoonPhase, self).__init__(*args, **kwargs)
        self.constants = Constants()

    def run(self) -> None:
        self.__init_defaults()
        self.__run_normal()
        #self.__run_cycle()

    def __init_defaults(self) -> None:
        self.canvas = self.matrix.CreateFrameCanvas()
        self.base_mid_x: int = math.floor(self.matrix.width / 2)
        self.mid_y: int = math.floor((self.canvas.height / 2)) - 3
        self.radius: int = 12

    def __run_normal(self, date: str = None) -> None:
        is_cycle_run = False if date is None else True
        current_date = date if date is not None else self.__get_date()

        while True:
            new_date = self.__get_date()
            if not is_cycle_run and self.__did_date_change_since_last_check(current_date, new_date):
                current_date = new_date
                self.canvas.Clear()

            date = current_date

            phase_data = self.constants.getData(date)
            phase_name = phase_data[self.PHASE_NAME]
            percent = float(phase_data[self.PERCENT])

            num_columns_to_fill = self.__get_num_columns_to_fill(percent)
            if num_columns_to_fill == 0 or percent > 50:
                self.__draw_circle(self.__get_circle_boundaries(self.base_mid_x, self.mid_y))

            if percent == 50:
                self.__draw_and_fill_half_moon(phase_name)
                self.__draw_text(phase_name, percent)

                self.matrix.SwapOnVSync(self.canvas)
                if is_cycle_run:
                    time.sleep(2)
                    break

                continue

            self.__draw_second_circle(phase_name, percent)

            if percent < 50:
                self.__file_in_early_moon()
            elif percent > 50:
                self.__fill_in_late_moon()

            self.__draw_text(phase_name, percent)

            self.matrix.SwapOnVSync(self.canvas)

            if is_cycle_run:
                time.sleep(2)
                break

            time.sleep(900)

    def __run_cycle(self) -> None:
        for date in self.CYCLE_DAYS:
            self.canvas.Clear()
            self.__run_normal(date)
            time.sleep(1)

    def __draw_second_circle(self, phase_name: str, percent: float) -> None:
        num_columns_to_fill = self.__get_num_columns_to_fill(percent)
        second_circle_direction = self.__get_second_circle_direction(phase_name, percent)
        if second_circle_direction == self.LEFT:
            self.second_mid_x: int = self.base_mid_x - num_columns_to_fill
        else:
            self.second_mid_x: int = self.base_mid_x + num_columns_to_fill

        second_circle_boundaries = self.__get_circle_boundaries(self.second_mid_x, self.mid_y)
        self.__draw_circle(second_circle_boundaries, True)

    def __is_within_canvas(self, x: float, y: float) -> bool:
        if (x >= 0 and x < self.matrix.width) and (y >= 0 and y < self.canvas.height):
            return True

        return False

    def __is_early_waxing(self, phase_name: str, percent: float) -> bool:
        return percent < 50 and self.WAXING in phase_name.lower()

    def __is_late_waning(self, phase_name: str, percent: float) -> bool:
        return percent > 50 and self.WANING in phase_name.lower()

    def __is_within_base_circle(self, x: float, y: float) -> bool:
        return math.pow(x - self.base_mid_x, 2) + math.pow(y - self.mid_y, 2) < math.pow(self.radius, 2)

    def __is_within_second_circle(self, x: int, y: int) -> bool:
        return math.pow(x - self.second_mid_x, 2) + math.pow(y - self.mid_y, 2) < math.pow(self.radius, 2)

    def __is_outside_second_circle(self, x: int, y: int) -> bool:
        return math.pow(x - self.second_mid_x, 2) + math.pow(y - self.mid_y, 2) > math.pow(self.radius, 2)

    def __is_outside_base_circle(self, x: int, y: int) -> bool:
        return math.pow(x - self.base_mid_x, 2) + math.pow(y - self.mid_y, 2) < math.pow(self.radius, 2)

    def __did_date_change_since_last_check(self, current_date: str, new_date: str) -> bool:
        return new_date != current_date

    def __get_circle_boundaries(self, mid_x: int, mid_y: int) -> Dict[str, int]:
        x = self.radius
        y = 0
        radius_error = 1 - x
        coordinate_dictionary = {}

        while y <= x:
            key = '{0}|{1}'.format(float(x + mid_x), float(y + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(y + mid_x), float(x + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-x + mid_x), float(y + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-y + mid_x), float(x + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-x + mid_x), float(-y + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-y + mid_x), float(-x + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(x + mid_x), float(-y + mid_y))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(y + mid_x), float(-x + mid_y))
            coordinate_dictionary[key] = 0
            y += 1

            if radius_error < 0:
                radius_error += 2 * y + 1
            else:
                x -= 1
                radius_error += 2 * (y -x + 1)

        return coordinate_dictionary

    def __get_second_circle_direction(self, phase_name: str, percent: float) -> str:
        if self.__is_early_waxing(phase_name, percent) or self.__is_late_waning(phase_name, percent):
            return self.LEFT

        return self.RIGHT

    def __get_text_and_starting_point(self, phase_name: str, percent: float) -> Mapping:
        if self.MILESTONES.get(phase_name) != None:
            text = self.MILESTONES.get(phase_name)
            x_point = 7
        else:
            text = "{0}%".format(percent)
            if percent < 10:
                x_point = 7
            else:
                x_point = 4

        return {
            'text': text,
            'startingPoint': x_point,
        }

    def __get_num_columns_to_fill(self, percent: float) -> int:
        num_columns = self.radius * 2
        if percent < 50:
            num_columns_to_fill = math.floor((percent / 100) * num_columns)
        else:
            actualized_percent = 100 - percent
            num_columns_to_fill = math.floor((actualized_percent / 100) * num_columns)

        return num_columns_to_fill

    def __get_date(self) -> str:
        date = datetime.now()
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        year = date.year
        return '{0}-{1}-{2}'.format(year, month, day)

    def __draw_and_fill_half_moon(self, phase_name: str) -> None:
        if self.FIRST in phase_name.lower():
            x_start_range = self.base_mid_x
            x_end_range = self.matrix.width
        else:
            x_start_range = 0
            x_end_range = self.base_mid_x

        for x in range(x_start_range, x_end_range):
            for y in range(0, self.canvas.height):
                if self.__is_within_base_circle(x, y):
                    self.canvas.SetPixel(x, y, 255, 255, 255)

    def __draw_circle(self, boundaries: Dict[str, int], is_second_circle: bool = False) -> None:
        for coordinateString in boundaries.keys():
            coordinates = coordinateString.split('|')

            x = float(coordinates[0])
            y = float(coordinates[1])

            if self.__is_within_canvas(x, y):
                if is_second_circle:
                    if self.__is_within_base_circle(x, y):
                        self.canvas.SetPixel(x, y, 255, 255, 255)
                else:
                    self.canvas.SetPixel(x, y, 255, 255, 255)

    def __draw_text(self, phase_name: str, percent: float) -> None:
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x7.bdf")
        text_color = graphics.Color(255, 255, 255)
        text_data = self.__get_text_and_starting_point(phase_name, percent)

        graphics.DrawText(
            self.canvas,
            font,
            text_data['startingPoint'],
            self.canvas.height,
            text_color,
            text_data['text']
        )

    def __file_in_early_moon(self) -> None:
        for x in range(0, self.matrix.width):
            for y in range(0, self.canvas.height):
                if self.__is_within_base_circle(x, y) and self.__is_outside_second_circle(x, y):
                    self.canvas.SetPixel(x, y, 255, 255, 255)

    def __fill_in_late_moon(self) -> None:
        for x in range(0, self.matrix.width):
            for y in range(0, self.canvas.height):
                if self.__is_within_second_circle(x, y) and self.__is_within_base_circle(x, y):
                    self.canvas.SetPixel(x, y, 255, 255, 255)

# Main function
if __name__ == "__main__":
    MOON_PHASE = MoonPhase()
    if not MOON_PHASE.process():
        MOON_PHASE.print_help()
