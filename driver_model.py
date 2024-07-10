class Driver:
    def __init__(self, driverId, position, interval_to_position_ahead, in_pit, pit_out, stopped, catching):
        self.driverId = driverId
        self.position = position
        self.interval_to_position_ahead = interval_to_position_ahead
        self.in_pit = in_pit
        self.pit_out = pit_out
        self.stopped = stopped
        self.catching = catching


    def __str__(self):
        return f"DriverId: {self.driverId}, Position: {self.position}, IntervalToPositionAhead: {self.interval_to_position_ahead}, " \
               f"InPit: {self.in_pit}, PitOut: {self.pit_out}, Stopped: {self.stopped}, Catching: {self.catching}"

