class Driver:
    def __init__(self, driver_id, position, interval_to_position_ahead, in_pit, pit_out, stopped, catching, retired):
        self.driver_id = driver_id
        self.position = position
        self.interval_to_position_ahead = interval_to_position_ahead
        self.in_pit = in_pit
        self.pit_out = pit_out
        self.stopped = stopped
        self.catching = catching
        self.retired = retired

    def __str__(self):
        return f"driver_id: {self.driver_id}, Position: {self.position}, IntervalToPositionAhead: {self.interval_to_position_ahead}, " \
               f"InPit: {self.in_pit}, PitOut: {self.pit_out}, Stopped: {self.stopped}, Catching: {self.catching}, Retired: {self.retired}"

