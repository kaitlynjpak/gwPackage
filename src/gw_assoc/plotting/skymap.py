import matplotlib.pyplot as plt

def plot_skymap(gw_data, transient, out_file="skymap.png"):
    """
    Minimal placeholder: blank plot with transient marker.
    """
    fig, ax = plt.subplots()
    ax.set_title("Skymap (stub)")
    if getattr(transient, "ra", None) is not None and getattr(transient, "dec", None) is not None:
        ax.plot(transient.ra, transient.dec, "o", label="Transient")
        ax.set_xlabel("RA [deg]")
        ax.set_ylabel("Dec [deg]")
        ax.legend()
    fig.savefig(out_file, bbox_inches="tight")
    plt.close(fig)
