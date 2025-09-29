import matplotlib.pyplot as plt

def plot_skymap(gw_data, transient, out_file="skymap.png"):
    """
    Minimal stub for skymap plotting.
    Just makes a blank plot with the transient marked.
    """
    fig, ax = plt.subplots()
    ax.set_title("Skymap (stub)")
    if transient.ra is not None and transient.dec is not None:
        ax.plot(transient.ra, transient.dec, "ro", label="Transient")
        ax.legend()
    plt.savefig(out_file)
    plt.close(fig)
