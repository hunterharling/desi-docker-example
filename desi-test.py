import os
import numpy as np

import fitsio

from astropy.io import fits
from astropy.table import Table, vstack, join
from astropy.convolution import convolve, Gaussian1DKernel

import matplotlib
import matplotlib.pyplot as plt

#-- input/output functions related to DESI spectra
import desispec.io

def test_spectra():
    sv3_bright_star = desispec.io.read_spectra('https://randommiscfiles.s3.us-west-1.amazonaws.com/coadd-sv3-bright-27256.fits')

    #-- plot the spectra

    fig, ax = plt.subplots(1, 1, figsize=(18,6))

    ax.set_xlim(3500, 9900)
    ax.set_xlabel(r"wavelength $\lambda\ \left[ \AA \right]$")
    ax.set_ylim(-2, 44)
    ax.set_ylabel(r"$F_{\lambda}\ \left[ 10^{-17}\ {\rm erg\ s}^{-1}\ {\rm cm}^{-2}\ \AA^{-1} \right]$")

    spectra = ( sv3_bright_star )
    zwarn   = (0,0,1570)
    coaddfs = (0,0,0)
    for PROG,ST,spec,color,zw,cfs in zip( ("OTHER","DARK","BRIGHT"), ("STAR","GALAXY","STAR"), spectra, ("k","orange","magenta"), zwarn, coaddfs ):
        for band in ("b","r","z"):
            label = f"PROG={PROG} | SPECTYPE={ST} | COADD_FIBERSTATUS={cfs} | ZWARN={zw}" if band=="b" else ""
            ax.plot(spec.wave[band], convolve(spec.flux[band][0], Gaussian1DKernel(5)), label=label, color=color, lw=2)

    ax.text(3600, 39, f"TARGETID = {tid}", ha="left", va="bottom")
    ax.legend(markerfirst=False, fontsize=18, handletextpad=0.5, frameon=False)

    #-- annotations
    ax.text(5800, 10, r"$\leftarrow$" + "arm overlap (not absorption)" + r"$\rightarrow$", ha="left", va="bottom", fontsize=19, color="red", rotation=350)
    ax.text(4800, 34, r"$\downarrow$", ha="left", va="bottom", fontsize=24, color="red")
    ax.text(6500, 23, r"$\downarrow$", ha="left", va="bottom", fontsize=24, color="red")
    ax.text(4920, 36, "absorption line", ha="left", va="bottom", fontsize=19, color="red")
    ax.text(6620, 25, "absorption line", ha="left", va="bottom", fontsize=19, color="red")

    plt.tight_layout()