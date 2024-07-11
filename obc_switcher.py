import mvf1

import driver_to_show_finder
import config
import time
from mvf1 import MultiViewerForF1


def createSortedListOfDriverIdsAndAction():
    sorted_driver_id = -1
    action_to_show = ''

    while sorted_driver_id == -1 or action_to_show == '':
        id_driver_to_overtake, id_driver_in_pit, id_driver_pit_out, id_stopped_driver, id_slow_driver = driver_to_show_finder.getDriverIdsToShow()

        driver_priority_map = {
            "stopped": id_stopped_driver,
            "slow": id_slow_driver,
            "overtake": id_driver_to_overtake,
            "in_pit": id_driver_in_pit,
            "pit_out": id_driver_pit_out
        }

        # sort drivers based on priorities
        drivers_with_priorities = [(priority, driver_priority_map[priority]) for priority in config.PRIORITIES]
        drivers_with_priorities.sort(key=lambda x: config.PRIORITIES.index(x[0]))
        sorted_driver_ids = [driver_with_priority for priority, driver_with_priority in drivers_with_priorities]

        print(sorted_driver_ids)

        # strip driver id list of -1 values and create action_to_show
        for sorted_driver_id in sorted_driver_ids:
            if sorted_driver_id != -1:
                action_to_show = config.PRIORITIES[sorted_driver_ids.index(sorted_driver_id)]
                return sorted_driver_id, action_to_show


def showDriver(shown_driver_id, shown_action):
    while True:
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

        print(f"{shown_driver_id} - {shown_action} - {min_time_to_switch}s - {max_time_to_switch}s")
        switchStream(shown_driver_id)

        if min_time_to_switch != -1:
            time.sleep(min_time_to_switch)

        start_time = time.time()
        check_interval = 0.1  # interval to check for higher priority action
        time_to_check = max_time_to_switch - min_time_to_switch

        found_action_during_interval = False  # flag to check if the action was found

        while time.time() - start_time < time_to_check:
            new_driver_id, new_shown_action = createSortedListOfDriverIdsAndAction()
            shown_action_priority = config.PRIORITIES.index(shown_action)
            new_shown_action_priority = config.PRIORITIES.index(new_shown_action)

            if shown_action_priority >= new_shown_action_priority and (shown_driver_id != new_driver_id or shown_action != new_shown_action):  # new action has higher priority
                print('Higher priority action found, switching driver.')
                shown_driver_id = new_driver_id
                shown_action = new_shown_action
                found_action_during_interval = True
                break

            time.sleep(check_interval)  # Sleep briefly to prevent busy waiting

        if time.time() - start_time >= time_to_check and not found_action_during_interval:
            # Max time reached, switch to next available action regardless of priority
            print('Max time to switch reached, changing to another action.')
            new_driver_id, new_shown_action = createSortedListOfDriverIdsAndAction()
            shown_driver_id = new_driver_id
            shown_action = new_shown_action


def switchStream(new_driver_id: str, old_driver_id: str):
    global obc_stream_player
    if new_driver_id == str(obc_stream_player.driver_data['driverNumber']):
        return
    obc_stream_player.switch_stream(config.DRIVERS_IDS_TLA_DICT[new_driver_id])  # TODO: first create on same position new stream, assign obc_stream_player to new stream then delete the old stream
    obc_stream_player = findPlayerByDriverId(new_driver_id)
    multi_viewer.player_sync_to_commentary()


def findPlayerByDriverId(needed_driver_id: str) -> mvf1.Player:
    players = multi_viewer.players
    for p in players:
        if p.driver_data and p.driver_data['driverNumber'] == int(needed_driver_id):
            return p


multi_viewer = MultiViewerForF1()
open_players = multi_viewer.players
live_stream_player = mvf1.Player
obc_stream_player = mvf1.Player

for player in open_players:
    if player.channel_id in [config.F1_LIVE_CHANNEL_ID, config.INTERNATIONAL_CHANNEL_ID]:
        live_stream_player = player
    else:
        if player.driver_data:
            obc_stream_player = player

if live_stream_player:
    # Initial call to start the process
    driver_id, action = createSortedListOfDriverIdsAndAction()
    showDriver(driver_id, action)
