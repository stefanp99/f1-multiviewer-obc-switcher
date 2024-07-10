import driver_renderer
from collections import defaultdict
import math
from dateutil import parser


def isDriverLosingTime(driver_last_intervals: set):
    if len(driver_last_intervals) < 5:
        return False

    driver_last_intervals_list = list(driver_last_intervals)

    if driver_last_intervals_list[-1] - driver_last_intervals_list[-2] >= 1 \
            and driver_last_intervals_list[-2] - driver_last_intervals_list[-3] >= 1 and \
            driver_last_intervals_list[-3] - driver_last_intervals_list[-4] >= 1 and \
            driver_last_intervals_list[-4] - driver_last_intervals_list[-5] >= 1:
        return True


def getDistanceCovered(point1, point2):
    return math.sqrt(
        (point2['x'] - point1['x']) ** 2 + (point2['y'] - point1['y']) ** 2)


def getTimePassed(time1, time2):
    dt1 = parser.isoparse(time1)
    dt2 = parser.isoparse(time2)

    time_difference = dt2 - dt1

    time_difference_in_seconds = time_difference.total_seconds()
    return time_difference_in_seconds


def getDriverSpeed(distance, time):
    if time == 0:
        return float(0)
    return ((distance / 1000) / (time / 3600)) / 10


def isDriverStopped(last_distances_covered: list):
    if len(last_distances_covered) < 3:
        return False

    return all(x == 0 for x in last_distances_covered[-3:])


def isDriverSlow(driver_last_speeds: list, rainfall: int):
    if len(driver_last_speeds) > 3:
        if rainfall > 0:
            return all(speed < 70 for speed in driver_last_speeds[-3:]) or 0 < driver_last_speeds[-1] < 30
        else:
            return all(speed < 100 for speed in driver_last_speeds[-3:]) or 0 < driver_last_speeds[-1] < 50
    return False


driver_last_intervals_dict = defaultdict(set)
last_drivers_positions_xyz = {}
driver_last_distances_covered_dict = defaultdict(list)
driver_speeds_dict = defaultdict(list)

last_timestamp = ''
time_passed = -1
while True:
    drivers, track_status, drivers_positions_xyz, timestamp, session_status, rain = driver_renderer.get_drivers()

    if session_status == 'Started':
        if last_timestamp:
            time_passed = getTimePassed(last_timestamp, timestamp)

        last_timestamp = timestamp

        if not last_drivers_positions_xyz:
            last_drivers_positions_xyz = drivers_positions_xyz

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

            if driver.interval_to_position_ahead and driver.interval_to_position_ahead[0] == '+':
                int_interval = float(driver.interval_to_position_ahead[1:])

                if int_interval < 1:
                    if min_position_driver_to_overtake > int(driver.position):
                        min_position_driver_to_overtake = int(driver.position)
                        id_driver_to_overtake = driver.driverId

                driver_last_intervals_dict[driver.driverId].add(int_interval)
                if len(driver_last_intervals_dict[driver.driverId]) > 10:
                    elements_list = list(driver_last_intervals_dict[driver.driverId])
                    elements_list.pop(0)
                    driver_last_intervals_dict[driver.driverId] = set(elements_list)

            if driver.in_pit:
                if min_position_driver_in_pit > int(driver.position):
                    min_position_driver_in_pit = int(driver.position)
                    id_driver_in_pit = int(driver.driverId)

            if driver.pit_out:
                if min_position_driver_pit_out > int(driver.position):
                    min_position_driver_pit_out = int(driver.position)
                    id_driver_pit_out = int(driver.driverId)

            # if isDriverLosingTime(driver_last_intervals_dict[driver.driverId]) and not driver.in_pit and not driver.pit_out:
            #     print(f"!!!DRIVER {driver.driverId} is losing a lot of time!!!")

            driver_distance_covered = getDistanceCovered(last_drivers_positions_xyz[driver.driverId],
                                                         drivers_positions_xyz[driver.driverId])
            driver_last_distances_covered_dict[driver.driverId].append(driver_distance_covered)
            if len(driver_last_distances_covered_dict[driver.driverId]) >= 10:
                driver_last_distances_covered_dict[driver.driverId].pop(0)

            if track_status <= 2:
                if isDriverStopped(driver_last_distances_covered_dict[driver.driverId]) and not driver.stopped and not driver.in_pit \
                        and not driver.pit_out:  # and not yet changed in the api to stopped and not in pit
                    stopped_drivers += 1
                    id_stopped_driver = int(driver.driverId)
                    if min_position_stopped_driver > int(driver.position):
                        min_position_stopped_driver = int(driver.position)
                        id_stopped_driver = driver.driverId

                if time_passed != -1:
                    driver_speed = float(getDriverSpeed(driver_distance_covered, time_passed))
                    driver_speeds_dict[driver.driverId].append(driver_speed)
                    if len(driver_speeds_dict[driver.driverId]) >= 10:
                        driver_speeds_dict[driver.driverId].pop(0)

                if isDriverSlow(driver_speeds_dict[driver.driverId], rain) and not driver.stopped and not driver.in_pit and not driver.pit_out:
                    id_slow_driver = int(driver.driverId)
                    slow_drivers += 1
                    if min_position_slow_driver > int(driver.position):
                        min_position_slow_driver = int(driver.position)
                        id_slow_driver = driver.driverId

        last_drivers_positions_xyz = drivers_positions_xyz

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
