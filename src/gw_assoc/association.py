from .io.skymap import load_gw_skymap
from .io.transient import Transient
from .analysis.odds import compute_posterior_odds
from .plotting.skymap import plot_skymap


class Association:
    """
    High-level wrapper for evaluating GW–EM associations.
    """

    def __init__(self, gw_file: str, transient_info: dict):
        """
        Parameters
        ----------
        gw_file : str
            Path to the GW skymap FITS file.
        transient_info : dict
            Dictionary with transient properties, e.g.
            {
                "ra": float (deg),
                "dec": float (deg),
                "z": float,
                "time": float (MJD or GPS)
            }
        """
        self.gw = load_gw_skymap(gw_file)
        self.transient = Transient(**transient_info)

    def compute_odds(self, **kwargs):
        """
        Compute posterior odds for association.

        Returns
        -------
        dict
            Results with spatial/temporal overlap and odds ratio.
        """
        return compute_posterior_odds(self.gw, self.transient, **kwargs)

    def plot_skymap(self, out_file: str = "skymap.png"):
        """
        Save a skymap plot with transient position overlay.
        """
        plot_skymap(self.gw, self.transient, out_file)
        print(f"[gw-assoc] Skymap saved to {out_file}")

