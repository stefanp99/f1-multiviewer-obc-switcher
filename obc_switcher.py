import driver_to_show_finder
import config
import time


def createSortedListOfDriverIdsAndAction(priority_map):
    drivers_with_priorities = [(priority, priority_map[priority]) for priority in config.PRIORITIES]
    drivers_with_priorities.sort(key=lambda x: config.PRIORITIES.index(x[0]))
    sorted_driver_ids = [driver_id for priority, driver_id in drivers_with_priorities]

    print(sorted_driver_ids)

    sorted_stripped_driver_ids = []

    for sorted_driver_id in sorted_driver_ids:
        if sorted_driver_id != -1:
            action_to_show = config.PRIORITIES[sorted_driver_ids.index(sorted_driver_id)]
            sorted_stripped_driver_ids.append(sorted_driver_id)
            return sorted_stripped_driver_ids, action_to_show


def showDriver(driver_id, shown_action):
    print(f"{driver_id} - {shown_action}")
    min_time_to_switch = -1
    max_time_to_switch = -1
    if shown_action == 'stopped':
        min_time_to_switch = config.MIN_TIME_SWITCH_STOPPED
        max_time_to_switch = config.MAX_TIME_SWITCH_STOPPED
    elif shown_action == 'slow':
        min_time_to_switch = config.MIN_TIME_SWITCH_SLOW
        max_time_to_switch = config.MAX_TIME_SWITCH_SLOW
    elif shown_action == 'overtake':
        min_time_to_switch = config.MIN_TIME_SWITCH_OVERTAKE
        max_time_to_switch = config.MAX_TIME_SWITCH_OVERTAKE
    elif shown_action == 'in_pit':
        min_time_to_switch = config.MIN_TIME_SWITCH_IN_PIT
        max_time_to_switch = config.MAX_TIME_SWITCH_IN_PIT
    elif shown_action == 'pit_out':
        min_time_to_switch = config.MIN_TIME_SWITCH_PIT_OUT
        max_time_to_switch = config.MAX_TIME_SWITCH_PIT_OUT

    if min_time_to_switch != -1:
        time.sleep(min_time_to_switch)


while True:
    id_driver_to_overtake, id_driver_in_pit, id_driver_pit_out, id_stopped_driver, id_slow_driver = driver_to_show_finder.getDriverIdsToShow()

    driver_priority_map = {
        "stopped": id_stopped_driver,
        "slow": id_slow_driver,
        "overtake": id_driver_to_overtake,
        "in_pit": id_driver_in_pit,
        "pit_out": id_driver_pit_out
    }

    driver_ids, action = createSortedListOfDriverIdsAndAction(driver_priority_map)
    if len(driver_ids) > 0:
        id_driver_to_show = driver_ids[0]
        showDriver(id_driver_to_show, action)
