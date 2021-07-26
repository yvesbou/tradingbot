import sys
import getopt
import urllib3
import time
from datetime import datetime

from botchart import BotChart
from botstrategy import BotStrategy
from botcandlestick import BotCandlestick
from botanimation import BotAnimation
from botlog import BotLog
from APIs import API
import numpy as np
from botchecker import BotChecker


def main(argv):
    # default:
    period = 300
    backTest = False
    animation = False
    csvName = "defaultLog.csv"
    platform = 'poloniex'

    try:
        # getopt.getopt returns two elements, opts which consists of pairs (options and values)
        # the second (args) is the list of program arguments left after the option list was stripped
        # (this is a trailing slice of args)
        opts, args = getopt.getopt(argv, "p:c:n:s:e:bha", ["period=", "currency=", "points=", "name="
                                                                                              "startTime=", "endTime=",
                                                           "platform=", "backTest",
                                                           "animation", "help"])
    except getopt.GetoptError:
        print("Start3.py -p <period> -c <currency pairs> -n <period of moving average> -s <startTime> -e <endTime>")
        sys.exit(2)

    for opt, arg in opts:
        print(opt, arg)
        if opt == '-h':
            print("Start3.py -p <period> -c <currency pairs> -n <period of moving average> -s <startTime> -e <endTime>")
            sys.exit()

        elif opt in ("-c", "--currency"):
            pairs = arg.split(",")
        elif opt in ("-n", "--points"):
            lengthofMA = int(arg)

        elif opt in ("-b", "--backTest"):
            backTest = True
        elif opt in ("-s", "--startTime"):
            startTime_datetime = datetime.strptime(arg, '%Y-%m-%d')
            startTime_timestamp = datetime.timestamp(startTime_datetime)
        elif opt in ("-e", "--endTime"):
            endTime_datetime = datetime.strptime(arg, '%Y-%m-%d')
            endTime_timestamp = datetime.timestamp(endTime_datetime)
        elif opt in ("-a", "--animation"):
            animation = True
        elif opt in ("-b", "--backTest"):
            backTest = True
        elif opt in ("--name"):
            csvName = arg
        elif opt == "--platform":
            print(arg)
            if arg in ['poloniex', 'binance']:
                platform = arg

            else:
                print("please enter a valid platform")
                sys.exit(2)
        elif opt in ("-p", "--period"):

            if arg in ["60", "180", "300", "900", "1800", "3600", "7200", "14400", "21600", "28800", "43200", "86400",
                       "259200", "1209600"]:
                period = int(arg)
            elif arg in ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"]:
                period_dict = {"1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, \
                               "2h": 7200, "4h": 14400, "6h": 21600, "8h": 28800, "12h": 43200, "1d": 86400, \
                               "3d": 259200, "1w": 1209600}
                period = period_dict[arg]
            else:
                print("Binance requires periods in 60,180,300, 900, 1800, 3600, 7200, 14400, 21600,28800,43200,86400,259200,1209600 or\
                  1m,3m,5m,15m,30m,1h,2h,4h,6h,8h,12h,1d,3d,1w,1M and Poloniex in 300,900,1800,7200,14400 or 86400 seconds")
                sys.exit(2)

    print(period)
    api = API(platform)
    checker = BotChecker(platform=platform)
    pairs = checker.pairs
    if backTest:
        log = BotLog()
        log.logToCsv(csvName)
        chart = BotChart(period=period, log=log, api=api, checker=checker)
        history, timestamps = chart.loadHistory(startTime_timestamp=startTime_timestamp,
                                                endTime_timestamp=endTime_timestamp)
        strategy = BotStrategy(api=api, period=period, log=log, checker=checker, stopLoss=0, startBalance=100)
        timestamps.pop(0)  # first timestamp in poloniex has 0 volume
        for timestamp in timestamps:
            strategy.tick(history, timestamp, initialize_live=False, duration=None)
            print("{} days passed".format((timestamp - timestamps[0]) / 86400))
            # log.tick()
        # logging to csv
        log.csvLog()
        log.histogram()
        log.scatter()

    else:
        log = BotLog()
        chart = BotChart(period=period, log=log, api=api, checker=checker)
        strategy = BotStrategy(api=api, period=period, log=log, checker=checker, stopLoss=0, startBalance=100)
        intermediateStep = time.time()
        data, timestamps = chart.loadHistory(startTime_timestamp=intermediateStep - 86400 * 15, endTime_timestamp=intermediateStep,
                                             firstTime=True, duringLive=False)
        duration = len(timestamps)
        counter = 0
        for timestamp in timestamps:  # loading history into BotStrategy (past indicators etc.)
            strategy.tick(data, timestamp, initialize_live=True)
            counter += 1
            if ((counter / duration) * 100 % 5) == 0:
                print(f"{(counter / duration) * 100} % progress of preloading the 15 days, "
                      f"since starting loading 15 days at: {intermediateStep}, {(time.time() - intermediateStep) / 60} minutes are over")
        # load data that is missing since the first part of loading history takes very long
        beginning = time.time()
        data, timestamps = chart.loadHistory(startTime_timestamp=intermediateStep, endTime_timestamp=beginning,
                                             firstTime=False, duringLive=False)
        for timestamp in timestamps:
            strategy.tick(data, timestamp, initialize_live=True)
        print(f"The second loading took {time.time() - beginning} seconds")
        # starting creating candlesticks and liveTrading
        if not animation:
            liveData = {}
            developingCandlestick = BotCandlestick(period=period, log=log, checker=checker)
            check = 0
            while True:
                startCandlestick = time.time()
                candlestickClosed = False
                print("!!!! NEXT ROUND !!!!")
                check = 0
                for pair in pairs:
                    developingCandlestick.tick(pair, chart.getCurrentTicker())
                    print("The pair: ", pair, "has ", developingCandlestick.counter[pair], " number of ticks")
                    if developingCandlestick.isClosed(pair):
                        check += 1
                print(f"counter is: {check}, len pairs is: {len(pairs)}, if equal the candlestick gets closed")
                if check == len(pairs):  # meaning all are closed
                    candlestickClosed = True
                    time_of_closed_candlestick = time.time()
                    liveData[time_of_closed_candlestick] = {}
                    time.sleep(5)
                    data, timestamps = chart.loadHistory(startTime_timestamp=startCandlestick-period,
                                                         endTime_timestamp=time_of_closed_candlestick, firstTime=False,
                                                         duringLive=True)

                    for pair in pairs:  # add the self made candlestick to the dictionary with the past data
                        liveData[time_of_closed_candlestick][pair] = developingCandlestick.candlestick[pair]
                        liveData[time_of_closed_candlestick][pair]['volume'] = data[timestamps[-1]][pair]['volume']  # assigning 1 tick old volume

                    strategy.tick(liveData, time_of_closed_candlestick, initialize_live=False)
                    # create new candlestick
                    developingCandlestick = BotCandlestick(period, log, checker)
                if not candlestickClosed:
                    time_used = time.time() - startCandlestick
                    try:
                        time.sleep(np.ceil(30 - time_used))
                    except:
                        pass

        #if animation:
           # BotAnimation(chart, strategy, developingCandlestick, BotCandlestick, period)


if __name__ == "__main__":
    main(sys.argv[1:])
