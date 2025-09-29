# from __future__ import annotations

# from typing import Any, Dict, Tuple, Union

# import numpy as np
# import healpy as hp
# from astropy.io.fits import getheader
# from astropy.table import Table

# import ligo.skymap.io.fits as ligo_fits
# import ligo.skymap.postprocess.util as ligo_pp


# def is_skymap_moc(obj: Union[str, np.ndarray, Table]) -> bool:
#     """
#     Decide if a sky map is a MOC (multi-order coverage) map.

#     - If a string path: check FITS header INDXSCHM == 'EXPLICIT' (MOC).
#     - If a Table: treat as MOC.
#     - If an ndarray (HEALPix array): not MOC.
#     """
#     if isinstance(obj, str):
#         try:
#             hdr = getheader(obj, ext=1)
#             return hdr.get('INDXSCHM', '').upper() == 'EXPLICIT'
#         except Exception:
#             # If we cannot read header, assume not MOC
#             return False
#     elif isinstance(obj, Table):
#         return True
#     elif isinstance(obj, (np.ndarray, list)):
#         return False
#     else:
#         raise TypeError(f'Unsupported type for is_skymap_moc: {type(obj)}')


# def _normalize_healpix_map(arr: np.ndarray, header: dict | None) -> Dict[str, Any]:
#     """
#     Normalize HEALPix probability map returned by ligo.skymap.io.fits.read_sky_map(moc=False).
#     Returns a dict with a consistent shape used throughout the package.
#     """
#     # ligo.skymap returns a 1D array of probabilities when moc=False
#     prob = np.asarray(arr, dtype=float)
#     nside = hp.npix2nside(prob.size)
#     nested = True  # ligo.skymap uses NESTED by default

#     # We *may* not have per-pixel distance params here. Keep None if absent.
#     return dict(
#         prob=prob,
#         distmu=None,
#         distsigma=None,
#         distnorm=None,
#         nside=nside,
#         nested=nested,
#         metadata=header or {}
#     )


# def _normalize_moc_table(tab: Table, target_nside: int | None = None) -> Dict[str, Any]:
#     """
#     Convert a MOC table into a full HEALPix map by rasterizing to target_nside.

#     NOTE: For now we use the simple rasterization path via ligo.skymap utilities.
#     If target_nside is None, pick the highest resolution present in the MOC.
#     """
#     # ligo.skymap.read_sky_map(moc=True) yields an Astropy Table like:
#     #  ORDER, NPIX, PROBDENSITY (and possibly distance columns)
#     # We'll rasterize by expanding each (ORDER, NPIX) cell to the corresponding pixels.
#     order = np.asarray(tab['ORDER'], dtype=int)
#     npix_moc = np.asarray(tab['NPIX'], dtype=int)

#     # Probability density per steradian in MOC; convert to probability per pixel when rasterizing
#     probdensity = np.asarray(tab['PROBDENSITY'], dtype=float)

#     # Choose target nside
#     max_order = int(order.max()) if order.size else 0
#     if target_nside is None:
#         target_nside = 2 ** max_order

#     target_order = int(np.log2(target_nside))
#     nest = True

#     npix_target = hp.nside2npix(target_nside)
#     prob = np.zeros(npix_target, dtype=float)

#     # For each MOC cell, fill the corresponding child pixels at target_order
#     for o, n, pd in zip(order, npix_moc, probdensity):
#         # number of child pixels per parent at the target order
#         nchild = 4 ** (target_order - o)
#         # Parent pixel index in NESTED scheme:
#         # ligo.skymap MOC NPIX encodes the index at that order in NEST
#         first_child = n * nchild
#         last_child = first_child + nchild
#         # Solid angle per child pixel:
#         dOmega = hp.nside2pixarea(2 ** target_order)  # steradians
#         # Probability per child pixel = probdensity * dOmega
#         prob[first_child:last_child] = pd * dOmega

#     # Normalize to 1 just in case of rounding
#     s = prob.sum()
#     if s > 0:
#         prob /= s

#     # Distance columns if present (average them down to children — crude but functional)
#     def _maybe_expand(colname: str) -> np.ndarray | None:
#         if colname in tab.colnames:
#             vals = np.asarray(tab[colname], dtype=float)
#             out = np.zeros_like(prob)
#             for o, n, v in zip(order, npix_moc, vals):
#                 nchild = 4 ** (target_order - o)
#                 first, last = n * nchild, n * nchild + nchild
#                 out[first:last] = v
#             return out
#         return None

#     distmu = _maybe_expand('DISTMU')
#     distsigma = _maybe_expand('DISTSIGMA')
#     distnorm = _maybe_expand('DISTNORM')

#     return dict(
#         prob=prob,
#         distmu=distmu,
#         distsigma=distsigma,
#         distnorm=distnorm,
#         nside=target_nside,
#         nested=nest,
#         metadata={}  # you can carry over tab.meta if needed
#     )


# def read_skymap(filename: str, *, moc: bool | None = None, target_nside: int | None = None) -> Dict[str, Any]:
#     """
#     Read a LVK sky map from FITS and return a *normalized* dict:
#       {
#         prob: 1D np.ndarray (length = 12 * nside^2),           # probability per pixel
#         distmu: np.ndarray | None, distsigma: np.ndarray | None, distnorm: np.ndarray | None,
#         nside: int,
#         nested: bool,       # True (NESTED order)
#         metadata: dict
#       }

#     Args:
#       filename: path to FITS sky map
#       moc: force MOC path (True/False). If None, auto-detect.
#       target_nside: if provided and input is MOC, rasterize to this NSIDE.

#     Behavior:
#       - If HEALPix (not MOC): use ligo.skymap.read_sky_map(..., moc=False) and normalize.
#       - If MOC: use ligo.skymap.read_sky_map(..., moc=True) and rasterize to HEALPix.
#     """
#     # Auto-detect MOC if moc is None
#     if moc is None:
#         moc = is_skymap_moc(filename)

#     if moc:
#         tab = ligo_fits.read_sky_map(filename, moc=True)  # Astropy Table
#         return _normalize_moc_table(tab, target_nside=target_nside)
#     else:
#         arr, hdr = ligo_fits.read_sky_map(filename, moc=False)  # (array, header)
#         return _normalize_healpix_map(arr, hdr)


# def enforce_same_resolution(*skymaps: Dict[str, Any], nside_new: int | None = None) -> Tuple[Dict[str, Any], ...]:
#     """
#     Ensure all HEALPix maps share the same NSIDE (NESTED).

#     - If nside_new is None, downgrade/upgrade all to the *minimum* NSIDE found.
#     - Uses ligo.skymap.postprocess.util.smooth_ud_grade for probability and
#       applies the same grading to distance columns if present.
#     """
#     maps = list(skymaps)
#     if nside_new is None:
#         nside_new = int(np.amin([m['nside'] for m in maps]))

#     out: list[Dict[str, Any]] = []
#     for m in maps:
#         if m['nside'] == nside_new:
#             out.append(m)
#             continue
#         # Probability
#         prob_new = ligo_pp.smooth_ud_grade(m['prob'], nside_new, order_in='NEST', order_out='NEST')
#         new = {**m, 'prob': prob_new, 'nside': nside_new}
#         # Distance parameters (grade the same way if present)
#         for key in ('distmu', 'distsigma', 'distnorm'):
#             if m.get(key) is not None:
#                 new[key] = ligo_pp.smooth_ud_grade(m[key], nside_new, order_in='NEST', order_out='NEST')
#         out.append(new)
#     return tuple(out)

# Minimal stub loader for a GW skymap FITS file
# Keep this simple so there are no circular imports.

def load_gw_skymap(file_path: str):
    return {"file": file_path, "kind": "gw_skymap"}
