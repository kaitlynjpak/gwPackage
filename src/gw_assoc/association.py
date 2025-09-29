from .io import load_gw_skymap
from .io.transient import Transient
from .analysis import compute_posterior_odds
from .plotting.skymap import plot_skymap

class Association:
    def __init__(self, gw_file: str, transient_info: dict):
        self.gw = load_gw_skymap(gw_file)
        self.transient = Transient(**transient_info)

    def compute_odds(self, **kwargs):
        return compute_posterior_odds(self.gw, self.transient, **kwargs)

    def plot_skymap(self, out_file: str = "skymap.png"):
        plot_skymap(self.gw, self.transient, out_file)
