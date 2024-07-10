class DriverLastIntervals:
    def __init__(self, driverId):
        self.driverId = driverId
        self.last_intervals = []

    def addInterval(self, interval):
        if len(self.last_intervals) >= 10:
            self.last_intervals = []
        self.last_intervals.append(interval)

    def __str__(self):
        return f"DriverId: {self.driverId}, Last Intervals: {self.last_intervals}"

