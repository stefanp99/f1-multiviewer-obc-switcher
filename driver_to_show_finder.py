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
    if rainfall > 0:
        return sum(speed_list) / len(speed_list) < config.THRESHOLD_RAIN_SLOW_DRIVER_SPEED
    else:
        return sum(speed_list) / len(speed_list) < config.THRESHOLD_DRY_SLOW_DRIVER_SPEED


def isDriverOvertaking(interval: float, drs):
    if interval <= config.THRESHOLD_OVERTAKE_FOR_INTERVAL_WITH_DRS:
        if drs == '8':  # drs detected, eligible in activation zone
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


iteration_nr = 0

while True:
    drivers, track_status, session_status, rain, car_data_list = driver_renderer.get_drivers()

    if session_status == 'Started':

        min_position_driver_to_overtake = 100
        id_driver_to_overtake = -1

        min_position_driver_in_pit = 100
        id_driver_in_pit = -1

        min_position_driver_pit_out = 100
        id_driver_pit_out = -1

        stopped_drivers = 0
        id_stopped_driver = -1
        min_position_stopped_driver = 100

        id_slow_driver = -1
        min_position_slow_driver = 100
        for driver in drivers:
            driver_car_data = findCarDataByDriverId(car_data_list, driver.driver_id)

            if driver.interval_to_position_ahead and driver.interval_to_position_ahead[0] == '+':
                float_interval = float(driver.interval_to_position_ahead[1:])

                if isDriverOvertaking(float_interval, driver_car_data.drs):
                    if min_position_driver_to_overtake > int(driver.position):
                        min_position_driver_to_overtake = int(driver.position)
                        id_driver_to_overtake = driver.driver_id

            if driver.in_pit:
                if min_position_driver_in_pit > int(driver.position):
                    min_position_driver_in_pit = int(driver.position)
                    id_driver_in_pit = int(driver.driver_id)

            if driver.pit_out:
                if min_position_driver_pit_out > int(driver.position):
                    min_position_driver_pit_out = int(driver.position)
                    id_driver_pit_out = int(driver.driver_id)

            if track_status <= 3:  # meaning green, yellow, double yellow flag
                if isDriverStopped(driver_car_data.speed_list) and not driver.stopped and not driver.in_pit \
                        and not driver.pit_out:  # and not yet changed in the api to stopped and not in pit
                    stopped_drivers += 1
                    id_stopped_driver = int(driver.driver_id)
                    if min_position_stopped_driver > int(driver.position):
                        min_position_stopped_driver = int(driver.position)
                        id_stopped_driver = driver.driver_id

                if isDriverSlow(driver_car_data.speed_list,
                                rain) and not driver.stopped and not driver.in_pit and not driver.pit_out:
                    id_slow_driver = int(driver.driver_id)
                    if min_position_slow_driver > int(driver.position):
                        min_position_slow_driver = int(driver.position)
                        id_slow_driver = driver.driver_id

        if id_driver_to_overtake != -1:
            print(f'driver to overtake: {str(id_driver_to_overtake)}')

        if id_driver_in_pit != -1:
            print('driver in pit: ' + str(id_driver_in_pit))

        if id_driver_pit_out != -1:
            print('driver pit out: ' + str(id_driver_pit_out))

        if id_stopped_driver != -1 and stopped_drivers <= 2:  # in case the stream is paused last driver will be shown:
            print(f"!!!DRIVER {str(id_stopped_driver)} is stopped!!!")

        if id_slow_driver != -1:
            print(f"!!!DRIVER {str(id_slow_driver)} is driving slow!!!")

    iteration_nr += 1
