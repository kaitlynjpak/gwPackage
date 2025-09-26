#spatial overlap calculations (KDE, GP)

def skymap_overlap_integral(gw_skymap, ext_skymap=None,
                            ra=None, dec=None,
                            gw_nested=True, ext_nested=True):
    """Sky map overlap integral between two sky maps.

    This method was originally developed in:
        doi.org/10.3847/1538-4357/aabfd2
    while the flattened sky map version was mentioned in:
        https://git.ligo.org/brandon.piotrzkowski/raven-paper

    Either a multi-ordered (MOC) GW sky map with UNIQ ordering,
    or a flattened sky map with Nested or Ring ordering can be used.
    Either a mutli-ordered (MOC) external sky map with UNIQ ordering,
    flattened sky map with Nested or Ring ordering,
    or a position indicated by RA/DEC can be used.

    Parameters
    ----------
    gw_skymap: array or Table
        Array containing either GW sky localization probabilities
        if using nested or ring ordering,
        or probability density if using UNIQ ordering
    ext_skymap: array or Table
        Array containing either external sky localization probabilities
        if using nested or ring ordering,
        or probability density if using UNIQ ordering
    ra: float
        Right ascension of external localization in degrees
    dec: float
        Declination of external localization in degrees
    gw_nested: bool
        If True, assumes GW sky map uses nested ordering, otherwise
        assumes ring ordering
    ext_nested: bool
        If True, assumes external sky map uses nested ordering, otherwise
        assumes ring ordering

    """
    # Set initial variables
    gw_skymap_uniq = None
    gw_skymap_prob = None
    ext_skymap_uniq = None
    ext_skymap_prob = None

    # Determine MOC or flattened
    gw_moc = is_skymap_moc(gw_skymap)
    # Set default value now, overwrite later if ext_skymap exists
    ext_moc = False

    # Load sky map arrays
    if gw_moc:
        gw_skymap_uniq = gw_skymap['UNIQ']
        try:
            gw_skymap_prob = gw_skymap['PROBDENSITY']
        except KeyError:
            gw_skymap_prob = gw_skymap['PROB']

    if ext_skymap is not None:
        ext_moc = is_skymap_moc(ext_skymap)
        if ext_moc:
            ext_skymap_uniq = ext_skymap['UNIQ']
            try:
                ext_skymap_prob = ext_skymap['PROBDENSITY']
            except KeyError:
                ext_skymap_prob = ext_skymap['PROB']

    # Set ordering
    se_order = 'nested' if gw_nested or gw_moc else 'ring'
    ext_order = 'nested' if ext_nested or ext_moc else 'ring'

    # Set negative values to zero to disclude them
    if gw_moc:
        np.clip(gw_skymap_prob, a_min=0., a_max=None)
    else:
        np.clip(gw_skymap, a_min=0., a_max=None)
    if ext_skymap is not None:
        if ext_moc:
            np.clip(ext_skymap_prob, a_min=0., a_max=None)
        else:
            np.clip(ext_skymap, a_min=0., a_max=None)

    if ext_skymap is None and not (ra is not None and dec is not None):
        # Raise error if external info not given
        raise ValueError("Please provide external sky map or ra/dec")

    # Use multi-ordered GW sky map
    if gw_moc:
        # gw_skymap is the probability density instead of probability
        # convert GW sky map uniq to ra and dec
        level, ipix = ah.uniq_to_level_ipix(gw_skymap_uniq)
        nsides = ah.level_to_nside(level)
        areas = ah.nside_to_pixel_area(nsides)
        ra_gw, dec_gw = \
            ah.healpix_to_lonlat(ipix, nsides,
                                 order='nested')
        sky_prior = 1 / (4 * np.pi * u.sr)
        se_norm = np.sum(gw_skymap_prob * areas)

        if ext_moc:
            # Use two multi-ordered sky maps
            gw_sky_hpmoc = PartialUniqSkymap(
                               gw_skymap_prob, gw_skymap_uniq,
                               name="PROBDENSITY")
            ext_sky_hpmoc = PartialUniqSkymap(
                                    ext_skymap_prob, ext_skymap_uniq,
                                    name="PROBDENSITY")
            ext_norm = np.sum(ext_sky_hpmoc.s * ext_sky_hpmoc.area())

            # Take product of sky maps and then sum to get inner product
            # Note that this method uses the highest depth grid of each sky map
            comb_sky_hpmoc = gw_sky_hpmoc * ext_sky_hpmoc
            return np.sum(comb_sky_hpmoc.s * comb_sky_hpmoc.area() /
                          sky_prior / se_norm / ext_norm).to(1).value

        elif ra is not None and dec is not None:
            # Use multi-ordered gw sky map and one external point
            # Relevant for very well localized experiments
            # such as Swift
            c = SkyCoord(ra=ra*u.degree, dec=dec*u.degree)
            catalog = SkyCoord(ra=ra_gw, dec=dec_gw)
            ind, d2d, d3d = c.match_to_catalog_sky(catalog)

            return (gw_skymap_prob[ind] / u.sr /
                    sky_prior / se_norm).to(1).value

        elif ext_skymap is not None:
            # Use multi-ordered gw sky map and flat external sky map
            # Find matching external sky map indices using GW ra/dec
            ext_nside = ah.npix_to_nside(len(ext_skymap))
            ext_ind = \
                ah.lonlat_to_healpix(ra_gw, dec_gw, ext_nside,
                                     order=ext_order)

            ext_norm = np.sum(ext_skymap)

            return np.sum(gw_skymap_prob * areas * ext_skymap[ext_ind] /
                          ah.nside_to_pixel_area(ext_nside) /
                          sky_prior / se_norm / ext_norm).to(1).value

    # Use flat GW sky map
    else:
        if ra is not None and dec is not None:
            # Use flat gw sky and one external point
            se_nside = ah.npix_to_nside(len(gw_skymap))
            ind = ah.lonlat_to_healpix(ra * u.deg, dec * u.deg, se_nside,
                                       order=se_order)
            se_norm = sum(gw_skymap)
            return gw_skymap[ind] * len(gw_skymap) / se_norm

        elif ext_skymap is not None:
            if gw_nested != ext_nested:
                raise ValueError("Sky maps must both use nested or ring "
                                 "ordering")
            # Use two flat sky maps
            nside_s = hp.npix2nside(len(gw_skymap))
            nside_e = hp.npix2nside(len(ext_skymap))
            if nside_s > nside_e:
                ext_skymap = hp.ud_grade(ext_skymap,
                                         nside_out=nside_s,
                                         order_in=('NESTED' if ext_nested
                                                   else 'RING'))
            else:
                gw_skymap = hp.ud_grade(gw_skymap,
                                        nside_out=nside_e,
                                        order_in=('NESTED' if gw_nested
                                                  else 'RING'))
            se_norm = gw_skymap.sum()
            exttrig_norm = ext_skymap.sum()
            if se_norm > 0 and exttrig_norm > 0:
                return (np.dot(gw_skymap, ext_skymap) / se_norm /
                        exttrig_norm * len(gw_skymap))
            raise ValueError("RAVEN: ERROR: At least one sky map has a "
                             "probability density that sums to zero or less.")

    raise ValueError("Please provide both GW and external sky map info")
