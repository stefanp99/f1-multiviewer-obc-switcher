import requests
import driver_to_show_finder
import config
import time
import player_model


def buildPlayersList():
    body = config.REQUEST_BODY_PLAYERS
    response = requests.post(url=url, json={"query": body})

    players_list = []

    if response.status_code == 200:
        data = response.json()
        players_data = data['data']['players']

        for player_data in players_data:
            p = player_model.Player(
                player_id=player_data['id'],
                player_type=player_data['type'],
                state=player_data['state'],
                driver_data=player_data.get('driverData'),
                stream_data=player_data['streamData'],
                bounds=player_data['bounds'],
                fullscreen=player_data['fullscreen'],
                always_on_top=player_data['alwaysOnTop'],
                maintain_aspect_ratio=player_data['maintainAspectRatio']
            )
            players_list.append(p)
    return players_list


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

            if shown_action_priority >= new_shown_action_priority and (
                    shown_driver_id != new_driver_id or shown_action != new_shown_action):  # new action has higher priority
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
            while new_driver_id == shown_driver_id:
                new_driver_id, new_shown_action = createSortedListOfDriverIdsAndAction()
            shown_driver_id = new_driver_id
            shown_action = new_shown_action


def switchStream(new_driver_id: str):
    global obc_player
    if new_driver_id == obc_player.driver_data['driverNumber']:
        return

    response_create_player = createPlayer(new_driver_id).json()

    old_obc_player_id = obc_player.player_id

    obc_player.player_id = response_create_player['data']['playerCreate']

    player_sync_ok = bool(syncPlayers().json()['data']['playerSync'])
    if not player_sync_ok:
        print('Not synced correctly')

    if config.DRIVER_HEADER_MODE != 'OBC_LIVE_TIMING':
        set_driver_header_mode_ok = bool(setDriverHeaderMode(obc_player.player_id, config.DRIVER_HEADER_MODE).json()['data']['playerSetDriverHeaderMode'])
        if not set_driver_header_mode_ok:
            print('Not set driver header mode correctly')

    set_always_on_top_ok = bool(setAlwaysOnTop(obc_player.player_id, True).json()['data']['playerSetAlwaysOnTop'])
    if not set_always_on_top_ok:
        print('Not set on top correctly')

    delete_player_ok = bool(deletePlayer(old_obc_player_id).json()['data']['playerDelete'])
    if not delete_player_ok:
        print('Not deleted correctly')


def createPlayer(new_driver_id):
    global obc_player
    new_player_dict = {"alwaysOnTop": False, "bounds": obc_player.bounds,
                       "contentId": obc_player.stream_data['contentId'], "driverNumber": int(new_driver_id),
                       "driverTla": config.DRIVERS_IDS_TLA_DICT[new_driver_id],
                       "fullscreen": obc_player.fullscreen, "maintainAspectRatio": obc_player.maintain_aspect_ratio,
                       "streamTitle": config.DRIVERS_IDS_TLA_DICT[new_driver_id]}

    obc_player.driver_data['driverNumber'] = new_driver_id
    obc_player.driver_data['tla'] = config.DRIVERS_IDS_TLA_DICT[new_driver_id]

    variables = {"input": new_player_dict}
    response = requests.post(url, json={"query": config.REQUEST_BODY_CREATE_PLAYER, "variables": variables})
    return response


def syncPlayers():  # Watch out if player is not created in time. Check while True loop in previous commits
    global additional_player
    variables = {"playerSyncId": additional_player.player_id}
    response = requests.post(url, json={"query": config.REQUEST_BODY_PLAYERS_SYNC, "variables": variables})
    return response


def deletePlayer(old_obc_player_id):
    variables = {"playerDeleteId": old_obc_player_id}
    response = requests.post(url, json={"query": config.REQUEST_BODY_DELETE_PLAYER, "variables": variables})
    return response


def setAlwaysOnTop(player_id, always_on_top: bool):
    variables = {"playerSetAlwaysOnTopId": str(player_id), "alwaysOnTop": always_on_top}
    response = requests.post(url, json={"query": config.REQUEST_BODY_ALWAYS_ON_TOP, "variables": variables})
    return response


def setDriverHeaderMode(player_id, header_mode):
    variables = {"playerSetDriverHeaderModeId": str(player_id), "mode": header_mode}
    response = requests.post(url, json={"query": config.REQUEST_BODY_DRIVER_HEADER_MODE, "variables": variables})
    return response


url = config.BASE_URL
players = buildPlayersList()
additional_player = player_model.Player
obc_player = player_model.Player
for player in players:
    if player.player_type == 'ADDITIONAL':  # F1 LIVE or INTERNATIONAL
        additional_player = player
    if player.player_type == 'OBC':
        obc_player = player
        obc_player.always_on_top = True

if additional_player and obc_player:
    # Initial call to start the process
    driver_id, action = createSortedListOfDriverIdsAndAction()
    showDriver(driver_id, action)
