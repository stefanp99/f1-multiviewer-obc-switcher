BASE_URL = 'http://localhost:10101/api/graphql'
REQUEST_BODY_DRIVER_INFO = '''{
      f1LiveTimingState {
        TimingData
        TrackStatus
        SessionStatus
        WeatherData
        CarData
      }
    }'''
REQUEST_BODY_PLAYERS = '''{
  players {
    id
    type
    state {
      ts
      paused
      muted
      volume
      live
      currentTime
      interpolatedCurrentTime
    }
    driverData {
      driverNumber
      tla
      firstName
      lastName
      teamName
    }
    streamData {
      contentId
      meetingKey
      sessionKey
      channelId
      title
    }
    bounds {
      x
      y
      width
      height
    }
    fullscreen
    alwaysOnTop
    maintainAspectRatio
    
  }
}'''
REQUEST_BODY_CREATE_PLAYER = '''mutation PlayerCreate($input: PlayerCreateInput!) {
  playerCreate(input: $input)
}
'''
REQUEST_BODY_PLAYERS_SYNC = '''mutation PlayerSync($playerSyncId: ID!) {
  playerSync(id: $playerSyncId)
}'''
REQUEST_BODY_DELETE_PLAYER = '''mutation PlayerDelete($playerDeleteId: ID!) {
  playerDelete(id: $playerDeleteId)
}'''
REQUEST_BODY_ALWAYS_ON_TOP = '''mutation PlayerSetAlwaysOnTop($playerSetAlwaysOnTopId: ID!, $alwaysOnTop: Boolean) {
  playerSetAlwaysOnTop(id: $playerSetAlwaysOnTopId, alwaysOnTop: $alwaysOnTop)
}'''
REQUEST_BODY_DRIVER_HEADER_MODE = '''mutation PlayerSetDriverHeaderMode($playerSetDriverHeaderModeId: ID!, $mode: DriverHeaderMode!) {
  playerSetDriverHeaderMode(id: $playerSetDriverHeaderModeId, mode: $mode)
}'''


THRESHOLD_RAIN_SLOW_DRIVER_SPEED = 50
THRESHOLD_DRY_SLOW_DRIVER_SPEED = 80
FREQUENCY_NR_FOR_SLOW_DRIVER = 3
THRESHOLD_OVERTAKE_FOR_INTERVAL_WITH_DRS = 0.6
THRESHOLD_OVERTAKE_FOR_INTERVAL_WITHOUT_DRS = 0.3
MIN_TIME_SWITCH_OVERTAKE = 10  # minimum period of time after which we can change the camera to a higher priority action
MAX_TIME_SWITCH_OVERTAKE = 20  # maximum period of time after which we must change the camera to any action
MIN_TIME_SWITCH_IN_PIT = 10
MAX_TIME_SWITCH_IN_PIT = 20
MIN_TIME_SWITCH_PIT_OUT = 5
MAX_TIME_SWITCH_PIT_OUT = 15
MIN_TIME_SWITCH_STOPPED = 5
MAX_TIME_SWITCH_STOPPED = 15
MIN_TIME_SWITCH_SLOW = 10
MAX_TIME_SWITCH_SLOW = 25
PRIORITIES = ["stopped", "slow", "overtake", "in_pit", "pit_out"]
F1_LIVE_CHANNEL_ID = 1033
INTERNATIONAL_CHANNEL_ID = 1025
DRIVERS_IDS_TLA_DICT = {"1": "VER", "11": "PER", "44": "HAM", "63": "RUS", "16": "LEC", "55": "SAI", "4": "NOR",
                        "81": "PIA", "14": "ALO", "18": "STR", "31": "OCO", "10": "GAS", "23": "ALB", "2": "SAR", "3": "RIC",
                        "22": "TSU", "77": "BOT", "24": "ZHO", "20": "MAG", "27": "HUL"}
TIME_RELATIVE_SEEK_BEHIND_AFTER_SWITCH = -5
DRIVER_HEADER_MODE = "DRIVER_HEADER"  # can be DRIVER_HEADER, NONE or OBC_LIVE_TIMING
