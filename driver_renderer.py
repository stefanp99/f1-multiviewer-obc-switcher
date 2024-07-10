import requests
import driver_model


def get_drivers():
    url = 'http://localhost:10101/api/graphql'
    body = '''{
      f1LiveTimingState {
        TimingData
        TrackStatus
        Position
        SessionStatus
        WeatherData
      }
    }'''

    response = requests.post(url=url, json={"query": body})

    drivers = []
    track_status = -1
    drivers_positions = {}
    timestamp = ''
    session_status = ''
    rain = -1

    if response.status_code == 200:
        data = response.json()

        drivers_data = data['data']['f1LiveTimingState']['TimingData']['Lines']

        track_status = int(data['data']['f1LiveTimingState']['TrackStatus']['Status'])

        positions = data['data']['f1LiveTimingState']['Position']['Position'][0]["Entries"]

        timestamp = data['data']['f1LiveTimingState']['Position']['Position'][0]['Timestamp']

        session_status = data['data']['f1LiveTimingState']['SessionStatus']['Status']

        rain = int(data['data']['f1LiveTimingState']['WeatherData']['Rainfall'])

        for driver_id, info in drivers_data.items():
            interval_to_position_ahead = info['IntervalToPositionAhead']['Value']
            in_pit = info['InPit']
            pit_out = info['PitOut']
            catching = info['IntervalToPositionAhead']['Catching']
            position = info['Position']
            stopped = info['Stopped']
            driver = driver_model.Driver(driverId=driver_id,
                                         position=position,
                                         interval_to_position_ahead=interval_to_position_ahead,
                                         in_pit=in_pit,
                                         pit_out=pit_out,
                                         stopped=stopped,
                                         catching=catching)
            drivers.append(driver)

        for driver_id, position in positions.items():
            drivers_positions[driver_id] = {
                "x": position["X"],
                "y": position["Y"],
                "z": position["Z"]
            }

    return drivers, track_status, drivers_positions, timestamp, session_status, rain
