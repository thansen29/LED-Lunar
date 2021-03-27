#!/usr/bin/env python
from samplebase import SampleBase
from datetime import *
import math
from constants import Constants
import time
from rgbmatrix import graphics
from typing import Dict

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

    def initDefaults(self) -> None:
        self.canvas = self.matrix.CreateFrameCanvas()
        self.baseMidX: int = math.floor(self.matrix.width / 2)
        self.midY: int = math.floor((self.canvas.height / 2)) - 3
        self.radius: int = 12

    def run(self) -> None:
        self.initDefaults()
        self.runNormal()
        #self.runCycle()

    def runNormal(self, date: str = None) -> None:
        isCycleRun = False if date == None else True
        currentDate = date if date != None else self.getDate()

        while True:
            newDate = self.getDate()
            if isCycleRun == False and self.didDateChangeSinceLastCheck(currentDate, newDate):
               currentDate = newDate
               self.canvas.Clear()

            date = currentDate

            phase_data = self.constants.getData(date)
            phaseName = phase_data[self.PHASE_NAME]
            percent = float(phase_data[self.PERCENT])

            numColumnsToFill = self.getNumColumnsToFill(percent)
            if numColumnsToFill == 0 or percent > 50:
                self.drawCircle(self.getCircleBoundaries(self.baseMidX, self.midY))

            if percent == 50:
                self.drawAndFillHalfMoon(phaseName)
                self.drawText(phaseName, percent)

                canvas = self.matrix.SwapOnVSync(self.canvas)
                if isCycleRun:
                    time.sleep(2)
                    break

                continue

            self.drawSecondCircle(phaseName, percent)

            if percent < 50:
                self.fillInEarlyMoon()
            elif percent > 50:
                self.fillInLateMoon()

            self.drawText(phaseName, percent)

            canvas = self.matrix.SwapOnVSync(self.canvas)

            if isCycleRun:
                time.sleep(2)
                break

            time.sleep(900)

    def runCycle(self) -> None:
        self.initDefaults()

        for date in self.CYCLE_DAYS:
            self.canvas.Clear()
            self.runNormal(date)
            time.sleep(1)

    def drawSecondCircle(self, phaseName: str, percent: float) -> None:
        numColumnsToFill = self.getNumColumnsToFill(percent)
        secondCircleDirection = self.getSecondCircleDirection(phaseName, percent)
        if secondCircleDirection == self.LEFT:
            self.secondMidX: int = self.baseMidX - numColumnsToFill
        else:
            self.secondMidX: int = self.baseMidX + numColumnsToFill

        secondCircleBoundaries = self.getCircleBoundaries(self.secondMidX, self.midY)
        self.drawCircle(secondCircleBoundaries, True)

    def isWithinCanvas(self, x: int, y: int) -> bool:
        if (x >= 0 and x < self.matrix.width) and (y >= 0 and y < self.canvas.height):
            return True

        return False

    def isEarlyWaxing(self, phaseName: str, percent: float) -> bool:
        return percent < 50 and self.WAXING in phaseName.lower()

    def isLateWaning(self, phaseName: str, percent: bool) -> bool:
        return percent > 50 and self.WANING in phaseName.lower()

    def isWithinBaseCircle(self, x: int, y: int) -> bool:
        return math.pow(x - self.baseMidX, 2) + math.pow(y - self.midY, 2) < math.pow(self.radius, 2)

    def isWithinSecondCircle(self, x: int, y: int) -> bool:
        return math.pow(x - self.secondMidX, 2) + math.pow(y - self.midY, 2) < math.pow(self.radius, 2)

    def isOutsideSecondCircle(self, x: int, y: int) -> bool:
        return math.pow(x - self.secondMidX, 2) + math.pow(y - self.midY, 2) > math.pow(self.radius, 2)

    def isOutsideBaseCircle(self, x: int, y: int) -> bool:
        return math.pow(x - self.baseMidX, 2) + math.pow(y - self.midY, 2) < math.pow(self.radius, 2)

    def didDateChangeSinceLastCheck(self, currentDate: str, newDate: str) -> bool:
        return newDate != currentDate

    def getCircleBoundaries(self, midX: int, midY: int) -> Dict[str, int]:
        x = self.radius
        y = 0
        radiusError = 1 - x
        coordinate_dictionary = {}

        while y <= x:
            key = '{0}|{1}'.format(float(x + midX), float(y + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(y + midX), float(x + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-x + midX), float(y + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-y + midX), float(x + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-x + midX), float(-y + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(-y + midX), float(-x + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(x + midX), float(-y + midY))
            coordinate_dictionary[key] = 0

            key = '{0}|{1}'.format(float(y + midX), float(-x + midY))
            coordinate_dictionary[key] = 0
            y += 1

            if radiusError < 0:
                radiusError += 2 * y + 1
            else:
                x -= 1
                radiusError += 2 * (y -x + 1)

        return coordinate_dictionary

    def getSecondCircleDirection(self, phaseName: str, percent: str) -> str:
        if self.isEarlyWaxing(phaseName, percent) or self.isLateWaning(phaseName, percent):
            return self.LEFT

        return self.RIGHT

    def getTextAndStartingPoint(self, phaseName: str, percent: float) -> Dict:
        if self.MILESTONES.get(phaseName) != None:
            text = self.MILESTONES.get(phaseName)
            xPoint = 7
        else:
            text = "{0}%".format(percent)
            if percent < 10:
                xPoint = 7
            else:
                xPoint = 4

        return {
            'text': text,
            'startingPoint': xPoint,
        }

    def getNumColumnsToFill(self, percent: float) -> int:
        numColumns = self.radius * 2
        if percent < 50:
            numColumnsToFill = math.floor((percent / 100 ) * numColumns)
        else:
            actualizedPercent = 100 - percent
            numColumnsToFill = math.floor((actualizedPercent / 100 ) * numColumns)

        return numColumnsToFill

    def getDate(self) -> str:
        date = datetime.now()
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        year = date.year
        return '{0}-{1}-{2}'.format(year, month, day)

    def drawAndFillHalfMoon(self, phaseName: str) -> None:
        if self.FIRST in phaseName.lower():
            xStartRange = self.baseMidX
            xEndRange = self.matrix.width
        else:
            xStartRange = 0
            xEndRange = self.baseMidX

        for x in range(xStartRange, xEndRange):
            for y in range(0, self.canvas.height):
                if self.isWithinBaseCircle(x, y):
                    self.canvas.SetPixel(x, y, 255, 255, 255)

    def drawCircle(self, boundaries: Dict[str, float], isSecondCircle: bool = False) -> None:
        for coordinateString in boundaries.keys():
            coordinates = coordinateString.split('|')

            x = float(coordinates[0])
            y = float(coordinates[1])

            if self.isWithinCanvas(x, y):
                if isSecondCircle:
                    if self.isWithinBaseCircle(x, y):
                        self.canvas.SetPixel(x, y, 255, 255, 255)
                else:
                    self.canvas.SetPixel(x, y, 255, 255, 255)

    def drawText(self, phaseName: str, percent: float) -> None:
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x7.bdf")
        textColor = graphics.Color(255, 255, 255)
        textData = self.getTextAndStartingPoint(phaseName, percent)

        graphics.DrawText(self.canvas, font, textData['startingPoint'], self.canvas.height, textColor, textData['text'])

    def fillInEarlyMoon(self) -> None:
        for x in range(0, self.matrix.width):
            for y in range(0, self.canvas.height):
                if self.isWithinBaseCircle(x, y) and self.isOutsideSecondCircle(x, y):
                    self.canvas.SetPixel(x, y, 255, 255, 255)

    def fillInLateMoon(self) -> None:
        for x in range(0, self.matrix.width):
            for y in range(0, self.canvas.height):
                if self.isWithinSecondCircle(x, y) and self.isWithinBaseCircle(x, y):
                    self.canvas.SetPixel(x, y, 255, 255, 255)

# Main function
if __name__ == "__main__":
    moon_phase = MoonPhase()
    if (not moon_phase.process()):
        moon_phase.print_help()
