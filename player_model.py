class Player:
    def __init__(self, player_id, player_type, state, driver_data, stream_data, bounds, fullscreen, always_on_top,
                 maintain_aspect_ratio):
        self.player_id = player_id
        self.player_type = player_type
        self.state = state
        self.driver_data = driver_data
        self.stream_data = stream_data
        self.bounds = bounds
        self.fullscreen = fullscreen
        self.always_on_top = always_on_top
        self.maintain_aspect_ratio = maintain_aspect_ratio

    def __str__(self):
        return f"Player(id={self.player_id}, type={self.player_type}, state={self.state}, driver_data={self.driver_data}, " \
               f"stream_data={self.stream_data}, bounds={self.bounds}, fullscreen={self.fullscreen}, always_on_top={self.always_on_top}, " \
               f"maintain_aspect_ratio={self.maintain_aspect_ratio})"
