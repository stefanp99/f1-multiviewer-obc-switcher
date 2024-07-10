import driver_renderer
from collections import defaultdict


def findCarDataByDriverId(car_datas: list, driver_id):
    for car_data in car_datas:
        if car_data.driver_id == driver_id:
            return car_data


def isDriverStopped(speed_list: list):
    return all(speed == 0 for speed in speed_list)


def isDriverSlow(speed_list: list, rainfall):
    return all(speed < 50 for speed in speed_list)


driver_last_intervals_dict = defaultdict(set)

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

        slow_drivers = 0
        id_slow_driver = -1
        min_position_slow_driver = 100
        for driver in drivers:
            driver_car_data = findCarDataByDriverId(car_data_list, driver.driver_id)

            if driver.interval_to_position_ahead and driver.interval_to_position_ahead[0] == '+':
                int_interval = float(driver.interval_to_position_ahead[1:])

                if int_interval < 1:
                    if min_position_driver_to_overtake > int(driver.position):
                        min_position_driver_to_overtake = int(driver.position)
                        id_driver_to_overtake = driver.driver_id

                driver_last_intervals_dict[driver.driver_id].add(int_interval)
                if len(driver_last_intervals_dict[driver.driver_id]) > 10:
                    elements_list = list(driver_last_intervals_dict[driver.driver_id])
                    elements_list.pop(0)
                    driver_last_intervals_dict[driver.driver_id] = set(elements_list)

            if driver.in_pit:
                if min_position_driver_in_pit > int(driver.position):
                    min_position_driver_in_pit = int(driver.position)
                    id_driver_in_pit = int(driver.driver_id)

            if driver.pit_out:
                if min_position_driver_pit_out > int(driver.position):
                    min_position_driver_pit_out = int(driver.position)
                    id_driver_pit_out = int(driver.driver_id)

            if track_status <= 2:
                if isDriverStopped(driver_car_data.speed_list) and not driver.stopped and not driver.in_pit \
                        and not driver.pit_out:  # and not yet changed in the api to stopped and not in pit
                    stopped_drivers += 1
                    id_stopped_driver = int(driver.driver_id)
                    if min_position_stopped_driver > int(driver.position):
                        min_position_stopped_driver = int(driver.position)
                        id_stopped_driver = driver.driver_id

                if isDriverSlow(driver_car_data.speed_list, rain) and not driver.stopped and not driver.in_pit and not driver.pit_out:
                    id_slow_driver = int(driver.driver_id)
                    slow_drivers += 1
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

        if id_slow_driver != -1 and slow_drivers <= 2:
            print(f"!!!DRIVER {str(id_slow_driver)} is driving slow!!!")
