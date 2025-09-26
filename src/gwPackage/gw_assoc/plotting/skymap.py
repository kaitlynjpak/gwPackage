def plot_skymap(skymap, cmap, label, filename="skymaps.pdf"):
    """
    Plot skymaps

    Parameters
    ----------
    skymaps : list of skymaps
    labels : list of labels
    cmaps : list of cmaps
    filename : filename
    """

    cmap = cm.get_cmap(cmap)
    levels = np.array([0.5, 0.9])

    fig = plt.figure()
    ax = plt.axes(projection='astro hours mollweide')
    ax.grid()
    contours = ax.contour_hpx((ligo.skymap.postprocess.util.find_greedy_credible_levels(skymap), 'ICRS'), levels=levels, nested=False, cmap=cmap)
    patches = mpatches.Patch(color=contours.cmap(100), label=label)
    ax.clabel(contours, inline=True, fontsize=6)
    plt.tight_layout()
    plt.title(label)
    plt.savefig(filename)
    plt.show()