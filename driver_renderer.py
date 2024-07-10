import requests
import driver_model
import car_data


def get_drivers():
    url = 'http://localhost:10101/api/graphql'
    body = '''{
      f1LiveTimingState {
        TimingData
        TrackStatus
        SessionStatus
        WeatherData
        CarData
      }
    }'''

    response = requests.post(url=url, json={"query": body})

    drivers = []
    track_status = -1
    session_status = ''
    rain = -1
    cars = {}
    car_data_list = []

    if response.status_code == 200:
        data = response.json()

        drivers_data = data['data']['f1LiveTimingState']['TimingData']['Lines']

        track_status = int(data['data']['f1LiveTimingState']['TrackStatus']['Status'])

        session_status = data['data']['f1LiveTimingState']['SessionStatus']['Status']

        rain = int(data['data']['f1LiveTimingState']['WeatherData']['Rainfall'])

        car_entries = data['data']['f1LiveTimingState']['CarData']['Entries']

        for driver_id, info in drivers_data.items():
            interval_to_position_ahead = info['IntervalToPositionAhead']['Value']
            in_pit = info['InPit']
            pit_out = info['PitOut']
            catching = info['IntervalToPositionAhead']['Catching']
            position = info['Position']
            stopped = info['Stopped']
            driver = driver_model.Driver(driver_id=driver_id,
                                         position=position,
                                         interval_to_position_ahead=interval_to_position_ahead,
                                         in_pit=in_pit,
                                         pit_out=pit_out,
                                         stopped=stopped,
                                         catching=catching)
            drivers.append(driver)

        driver_speeds = {}
        for entry in car_entries:
            cars = entry['Cars']
            for driverId, car_datas in cars.items():
                speed = car_datas['Channels']['2']
                if driverId not in driver_speeds:
                    driver_speeds[driverId] = []
                driver_speeds[driverId].append(speed)

        for driverId, speeds in driver_speeds.items():
            drs = cars[driverId]['Channels'].get('45', 0)
            car_data_list.append(car_data.CarData(driverId, drs, speeds))

    return drivers, track_status, session_status, rain, car_data_list
