import driver_renderer
from collections import Counter
import config


def findCarDataByDriverId(car_datas: list, driver_id):
    for car_data in car_datas:
        if car_data.driver_id == driver_id:
            return car_data


def isDriverStopped(speed_list: list):
    return all(speed == 0 for speed in speed_list)


def isDriverSlow(speed_list: list, rainfall):
    if len(speed_list) == 0 or sum(speed_list) / len(speed_list) == 0:
        return False
    if rainfall > 0:
        return sum(speed_list) / len(speed_list) < config.THRESHOLD_RAIN_SLOW_DRIVER_SPEED
    else:
        return sum(speed_list) / len(speed_list) < config.THRESHOLD_DRY_SLOW_DRIVER_SPEED


def isDriverOvertaking(interval: float, drs):
    if interval <= config.THRESHOLD_OVERTAKE_FOR_INTERVAL_WITH_DRS:
        if drs in [8, 10, 11, 12]:  # drs detected, eligible in activation zone or drs on
            return True
        elif interval <= config.THRESHOLD_OVERTAKE_FOR_INTERVAL_WITHOUT_DRS:
            return True
        return False
    return False


def findSlowDriversInLastIterations(drivers_ids_list: list):
    count = Counter(drivers_ids_list)
    slow_drivers = [element for element, freq in count.items() if freq == config.FREQUENCY_NR_FOR_SLOW_DRIVER]
    for slow_driver in slow_drivers:
        drivers_ids_list = [driver_id for driver_id in drivers_ids_list if
                            driver_id != slow_driver]  # remove all occurrences of slow driver
    return slow_drivers


def getDriverIdsToShow():
    drivers, track_status, session_status, rain, car_data_list = driver_renderer.get_drivers()

    min_position_driver_to_overtake = 100
    id_driver_to_overtake = -1

    min_position_driver_in_pit = 100
    id_driver_in_pit = -1

    min_position_driver_pit_out = 100
    id_driver_pit_out = -1

    min_position_stopped_driver = 100
    id_stopped_driver = -1

    min_position_slow_driver = 100
    id_slow_driver = -1
    if session_status == 'Started':
        for driver in drivers:
            if not (driver.retired or driver.stopped):

                driver_car_data = findCarDataByDriverId(car_data_list, driver.driver_id)

                if driver.in_pit:
                    if min_position_driver_in_pit > int(driver.position):
                        min_position_driver_in_pit = int(driver.position)
                        id_driver_in_pit = driver.driver_id

                if driver.pit_out:
                    if min_position_driver_pit_out > int(driver.position):
                        min_position_driver_pit_out = int(driver.position)
                        id_driver_pit_out = driver.driver_id

                if isDriverStopped(driver_car_data.speed_list) and not driver.stopped and not driver.in_pit and not driver.retired:  # and not yet changed in the api to stopped and not in pit
                    id_stopped_driver = driver.driver_id
                    if min_position_stopped_driver > int(driver.position):
                        min_position_stopped_driver = int(driver.position)
                        id_stopped_driver = driver.driver_id

                if track_status <= 3:  # meaning green, yellow
                    if driver.interval_to_position_ahead and driver.interval_to_position_ahead[0] == '+':
                        float_interval = float(driver.interval_to_position_ahead[1:])

                        if isDriverOvertaking(float_interval, driver_car_data.drs) and not driver.in_pit:
                            if min_position_driver_to_overtake > int(driver.position):
                                min_position_driver_to_overtake = int(driver.position)
                                id_driver_to_overtake = driver.driver_id

                    if isDriverSlow(driver_car_data.speed_list,
                                    rain) and not driver.stopped and not driver.in_pit and not driver.pit_out:
                        id_slow_driver = driver.driver_id
                        if min_position_slow_driver > int(driver.position):
                            min_position_slow_driver = int(driver.position)
                            id_slow_driver = driver.driver_id

    return id_driver_to_overtake, id_driver_in_pit, id_driver_pit_out, id_stopped_driver, id_slow_driver
