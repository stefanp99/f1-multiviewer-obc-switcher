class CarData:
    def __init__(self, driver_id, drs, speed_list):
        self.driver_id = driver_id
        self.drs = drs
        self.speed_list = speed_list

    def __str__(self):
        return f"driver_id: {self.driver_id}, DRS: {self.drs}, Speeds: {self.speed_list}"
