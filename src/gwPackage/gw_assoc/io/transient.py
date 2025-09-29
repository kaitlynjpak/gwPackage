class Transient:
    """
    Minimal representation of a transient event.
    """

    def __init__(self, ra=None, dec=None, z=None, time=None):
        self.ra = ra
        self.dec = dec
        self.z = z
        self.time = time

    def __repr__(self):
        return f"<Transient ra={self.ra}, dec={self.dec}, z={self.z}, time={self.time}>"
