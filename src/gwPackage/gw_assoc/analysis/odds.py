def compute_posterior_odds(gw_data, transient, **kwargs):
    """
    Minimal stub for posterior odds calculation.

    Parameters
    ----------
    gw_data : dict
        GW data object (from load_gw_skymap).
    transient : Transient
        Transient event.

    Returns
    -------
    dict
        Placeholder odds results.
    """
    return {
        "gw_file": gw_data.get("file", None),
        "transient": {
            "ra": getattr(transient, "ra", None),
            "dec": getattr(transient, "dec", None),
            "z": getattr(transient, "z", None),
            "time": getattr(transient, "time", None),
        },
        "posterior_odds": None,  # placeholder
        "note": "compute_posterior_odds not implemented yet",
    }
