#!/usr/bin/env python
# coding: utf-8

# # Introduction to DESI Early Data Release 
# 
# *Ragadeepika Pucha (U.Arizona), Anthony Kremin (Berkeley Lab), Stéphanie Juneau (NOIRLab), Jaime E. Forero-Romero (Uniandes) and DESI Data Team*

# # Table of Contents
# 
# * [Overview](#overview)
# * [Imports](#import)
# * [Accessing the data](#data_access)
#     * [Summary Files](#sumfiles)
#     * [Redshift Catalogs](#zcatalog)
#     * [Summary Redshift Catalogs](#summary_zcatalog)
#     * [Healpix/ Directory](#hpx)
# * [Accessing and Plotting Spectra of a Single Object](#spectra_access)
#     * [Working with Coadded Spectra using desispec.io.read_spectra](#spectra)
# * [References](#ref)

# <a class="anchor" id="overview"></a>
# # Overview
# 
# In this notebook, we will explore the DESI data file structure in the early data release (EDR). Information about the release can be found [here](https://data.desi.lbl.gov/doc/releases/). <br/> 
# The notebook shows how to access the different files in the data release, to access all the available spectra, along with the redshift information, for a given object, and to finally plot the "best" spectrum. 
# 
# A list of technical papers describing the science, targeting and the survey design for the DESI experiment can be found [here](https://data.desi.lbl.gov/doc/papers/).
# 
# All links in this tutorial are public unless stated that they are **exclusive to DESI collaborators**.
# 
# ### Bug Reporting
# If you identify any errors or have requests for additional functionality please create a new issue at https://github.com/desihub/tutorials/issues or submit a question on the [DESI User Forum](https://help.desi.lbl.gov).
# 
# ### Getting Started
# 
# #### Using NERSC
# 
# The easiest way to get started is to use the jupyter server at NERSC so that you don't need to
# install any code or download any data locally.
# 
# If you need a NERSC account, see https://desi.lbl.gov/trac/wiki/Computing/AccessNersc (**link exclusive to DESI collaborators**)
# 
# Then do the one-time jupyter configuration described at https://desi.lbl.gov/trac/wiki/Computing/JupyterAtNERSC (**link exclusive to DESI collaborators**)
# 
# From a NERSC command line, checkout a copy of the tutorial code, *e.g.* from perlmutter.
# ```console
# mkdir -p $HOME/desi/
# cd $HOME/desi/
# git clone https://github.com/desihub/tutorials
# ```
# And then go to https://jupyter.nersc.gov, login, navigate to where you checked out this package (*e.g.* `$HOME/desi/tutorials/getting_started`), and double-click on `intro_to_DESI_EDR_files.ipynb`.
# 
# 
# #### Setting up the DESI environment (kernel)
# 
# For those referring to this in 2023 or beyond: this tutorial has been tested using the "DESI 23.1" kernel installed at NERSC. If you don't see that installed, you will need to open a terminal either in jupyterhub or via an actual terminal logged in to NERSC and do the following:
# 
# ```console
# source /global/common/software/desi/desi_environment.sh 23.1
# ${DESIMODULES}/install_jupyter_kernel.sh 23.1
# 
# ```
# You'll then need to restart your jupyterhub instance to see the kernel. After following the step above and restarting: you can go to the Kernel menu, select "Change Kernel", then select 'DESI 23.1' from the dropdown menu.

# <a class="anchor" id="import"></a>
# # Imports

# In[1]:


# import some helpful python packages 
import os
import numpy as np

from astropy.io import fits
from astropy.table import Table
from astropy.convolution import convolve, Gaussian1DKernel

import matplotlib 
import matplotlib.pyplot as plt

#plt.style.use('../mpl/desi.mplstyle')


# In[2]:


# import DESI related modules - 
from desimodel.footprint import radec2pix      # For getting healpix values
import desispec.io                             # Input/Output functions related to DESI spectra
from desispec import coaddition                # Functions related to coadding the spectra

# DESI targeting masks - 
from desitarget.sv1 import sv1_targetmask    # For SV1
from desitarget.sv2 import sv2_targetmask    # For SV2
from desitarget.sv3 import sv3_targetmask    # For SV3


# <a class="anchor" id="data_access"></a>
# # Accessing the data
# 
# The DESI Early Data Release (EDR) consists some of the commissioning data, as well as the whole of the survey validation (SV) data. This includes SV1, SV2, and SV3 (1% survey). 
# Information about the SV data can be found [here](https://data.desi.lbl.gov/doc/). 
# 
# For the EDR data, the spectra are divided by the `SURVEY` (sv1/sv2/sv3) they were observed in. The observing conditions (dark or bright), called as `PROGRAM` in the DESI terminology, is used to categorize the spectra further. 

# In[3]:


# Release directory path

specprod = 'fuji'    # Internal name for the EDR
specprod_dir = './s3/cfs/cdirs/desi/public/edr/spectro/redux/fuji'
print(specprod_dir)


# In[4]:


# List everything in this directory
#os.listdir(specprod_dir)


# ### Important files to Note:
# 
# 1. tiles-fuji.fits (or .csv) -- This contains information about the observed tiles.
# 2. exposures-fuji.fits (or .csv) -- This consists of information about individual exposures of the targets.
# 3. zcatalog/ Directory -- This directory contains all of the redshift catalogs.
# 4. tiles/ Directory -- This directory holds all of the per-tile coadds and redshifts, in various flavors.
# 5. healpix/ Directory -- This directory holds all of the coadds and redshifts based on sky location (healpix).

# <a class="anchor" id="sumfiles"></a>
# ## Summary Files
# 
# Let's first take a look at the tiles and exposure summary files.

# ### tiles-fuji.fits
# This file tells you what tiles were observed, what `SURVEY` and `PROGRAM` they were observed for, some observing conditions, and three estimates of the "effective time" (in seconds) that each tile acquired. The time estimate used for survey operations decisions is `EFFTIME_SPEC`. The datamodel for this table is described [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/tiles-SPECPROD.html).

# In[5]:


tiles_table = Table.read(f'{specprod_dir}/tiles-{specprod}.fits',)
print(f"Tiles table columns: {tiles_table.colnames}")


# In[9]:


tiles_table[0:5]


# Let's use this to find the number of tiles in each SURVEY and each PROGRAM.

# In[10]:


for survey in ['cmx', 'sv1', 'sv2', 'sv3']:
    print(f'{survey}: Ntiles = {np.sum(tiles_table["SURVEY"]==survey)}')


# In[11]:


for program in ['bright', 'dark']:
    print(f'{program}: Ntiles = {np.sum(tiles_table["PROGRAM"]==program)}')


# ### exposures-fuji.fits
# This file is primarily used for daily operations, but can be handy for looking at individual exposures and the amount of "EFFECTIVE TIME" that exposure acquired. <br/>
# The datamodel for this file is available [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/exposures-SPECPROD.html).

# In[12]:


exp_table = Table.read(f'{specprod_dir}/exposures-{specprod}.fits', hdu='EXPOSURES')
print(f"Tiles table columns: {exp_table.colnames}")


# In[13]:


exp_table[-5:]


# Let's use this to find the number of exposures in each `SURVEY` and each `PROGRAM`.

# In[14]:


for survey in ['cmx', 'sv1', 'sv2', 'sv3']:
    print(f'{survey}: Nexps={np.sum(exp_table["SURVEY"]==survey)}')


# In[15]:


for program in ['bright', 'dark']:
    print(f'{program}: Nexps={np.sum(exp_table["PROGRAM"]==program)}')


# <a class="anchor" id="zcatalog"></a>
# 
# ## Redshift Catalogs
# 
# The redshift catalogs that are in the `zcatalog/` directory are divided into `zpix` and `ztile` files. The `zpix` files have the format: `zpix-{survey}-{program}.fits`, while the `ztile` have the format: `ztile-{survey}-{program}-{group}.fits`. The datamodel for the different files within this folder can be found [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/index.html). Each of these files contain redshift and targeting information of the sources based on how their spectra are coadded. 
# 
# * **survey**: SURVEY that the target was observed in. This can be sv1, sv2, or main.
# * **program**: FIBER ASSIGNMENT PROGRAM. This is the planned observing conditions for the target. It can be dark or bright or backup. In case of cmx and sv1, there is 'other' as well.
# * **group**: This denotes what type of coadd. It can be perexp, pernight, or cumulative.
# 
# For example, `zpix-sv1-dark.fits` contains information about the targets that were observed in SV1 for the _dark_ program. Since it is healpix based, the resulting spectra for a particular target is the coadded spectra across all tiles that were observed within the given `SURVEY` and `PROGRAM`. This will provide the highest S/N version of each target.
# 
# Note that some of the targets were observed in multiple surveys and/or programs. In such cases, one may want to select the _PRIMARY_ spectrum of a given object. This information is available in the redshift summary catalogs, which will be explained in detail below.

# In[16]:


# Listing all the available redshift catalogs

os.listdir(f'{specprod_dir}/zcatalog')


# Now, we will look at the summary redshift catalogs that contain the `PRIMARY` spectra information
# 
# <a class="anchor" id="summary_zcatalog"></a>
# ## Summary Redshift Catalogs
# 
# There are two summary redshift catalogs: <br/>
# **zall-pix-fuji.fits** <br/> 
# This is a stack of all the healpix-based redshift catalogs, including all surveys and programs. The datamodel is [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zall-pix-SPECPROD.html). <br/>
# **zall-tilecumulative-fuji.fits** <br/>
# This is a stack of all the tile-based cumulative redshift catalogs, including all surveys and programs. The datamodel is [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zall-tilecumulative-SPECPROD.html).
# 
# For both these summary catalogs, all the columns in the original catalogs ([zpix-SURVEY-PROGRAM.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zpix-SURVEY-PROGRAM.html) and [ztile-SURVEY-PROGRAM-GROUPTYPE.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zpix-SURVEY-PROGRAM.html)) are included. <br/>
# Four new columns are added:
# 
# 1. SV_NSPEC - Number of SV spectra available of each target.
# 2. SV_PRIMARY - PRIMARY flag for the sources with SV spectra.
# 3. ZCAT_NSPEC - Number of spectra available in the entire catalog of each target.
# 4. ZCAT_PRIMARY - PRIMARY flag for the sources in the entire catalog.

# ### Tile-based vs healpix-based
# The choice of which you use will depend on your specific science case. If you want the hightest S/N spectra then you'll likely want to use healpix based redshifts. If you want a more consistant observing depth among the redshfits in your sample, or you need objects that fit on a single pointing, then tile redshifts may be of more 
# interest.
# 
# We will focus here on the healpix based redshifts.

# ### Working with the zall-pix file

# In[17]:


zpix_cat = Table.read(f'{specprod_dir}/zcatalog/zall-pix-{specprod}.fits', hdu="ZCATALOG")


# In[18]:


print(zpix_cat.columns)


# In[19]:


zpix_cat[0:5]


# ### Selecting sources based on Targeting Information
# 
# There are five main target types used in DESI:
# 1. Milky Way Survey (MWS)
# 2. Bright Galaxy Survey (BGS)
# 3. Luminous Red Galaxies (LRG)
# 4. Emission Line Galaxies (ELG)
# 5. Quasars (QSO).
# 
# Information about how these targets are selected are available separately for [SV1](https://desi.lbl.gov/trac/wiki/TargetSelectionWG/SurveyValidation), [SV2](https://desi.lbl.gov/trac/wiki/TargetSelectionWG/SV2), and [SV3](https://desi.lbl.gov/trac/wiki/TargetSelectionWG/SV3) (**links exclusive to DESI collaborators**). Based on the tests on SV data, the finalized target selection for the main survey is available [in this paper](https://ui.adsabs.harvard.edu/abs/2023AJ....165...50M/abstract). <br/>
# **To-do: Add public links to SV target selection when available**

# In[20]:


# Targetting bits are coded in the sv*_targetmask.desi_mask
## The long list of targeting reflects the complexity of the targeting process and helps in subselecting from the main target types.

sv1_targetmask.desi_mask


# In[21]:


# A simple example of using the bitmasks

print(sv1_targetmask.desi_mask.mask("STD_FAINT"), sv1_targetmask.desi_mask.mask("STD_BRIGHT"), sv1_targetmask.desi_mask.mask("STD_FAINT|STD_BRIGHT"))
print(2**33, 2**35, 2**33 + 2**35)


# In[22]:


# Targeting information about the DESI targetting is stored in the different desi_target columns
# sv1_targetmask.desi_mask corresponds to SV1_DESI_TARGET
# sv2_targetmask.desi_mask corresponds to SV2_DESI_TARGET
# sv3_targetmask.desi_mask corresponds to SV3_DESI_TARGET

sv1_desi_tgt = zpix_cat['SV1_DESI_TARGET']
sv2_desi_tgt = zpix_cat['SV2_DESI_TARGET']
sv3_desi_tgt = zpix_cat['SV3_DESI_TARGET']

sv1_desi_mask = sv1_targetmask.desi_mask
sv2_desi_mask = sv2_targetmask.desi_mask
sv3_desi_mask = sv3_targetmask.desi_mask


# In[23]:


# Selecting candidates - 
# The code below selects the individual targets observed in all the SV1, SV2, and SV3 tiles.

## All BGS targets from sv1, sv2, and sv3
is_bgs = (sv1_desi_tgt & sv1_desi_mask['BGS_ANY'] != 0)|(sv2_desi_tgt & sv2_desi_mask['BGS_ANY'] != 0)|(sv3_desi_tgt & sv3_desi_mask['BGS_ANY'] != 0)
## All LRG targets from sv1, sv2, and sv3
is_lrg = (sv1_desi_tgt & sv1_desi_mask['LRG'] != 0)|(sv2_desi_tgt & sv2_desi_mask['LRG'] != 0)|(sv3_desi_tgt & sv3_desi_mask['LRG'] != 0)
## All ELG targets from sv1, sv2, and sv3
is_elg = (sv1_desi_tgt & sv1_desi_mask['ELG'] != 0)|(sv2_desi_tgt & sv2_desi_mask['ELG'] != 0)|(sv3_desi_tgt & sv3_desi_mask['ELG'] != 0)
## All QSO targets from sv1, sv2, and sv3
is_qso = (sv1_desi_tgt & sv1_desi_mask['QSO'] != 0)|(sv2_desi_tgt & sv2_desi_mask['QSO'] != 0)|(sv3_desi_tgt & sv3_desi_mask['QSO'] != 0)
## All MWS targets from sv1, sv2, and sv3
is_mws = (sv1_desi_tgt & sv1_desi_mask['MWS_ANY'] != 0)|(sv2_desi_tgt & sv2_desi_mask['MWS_ANY'] != 0)|(sv3_desi_tgt & sv3_desi_mask['MWS_ANY'] != 0)
## All Secondary targets from sv1, sv2, and sv3
is_scnd = (sv1_desi_tgt & sv1_desi_mask['SCND_ANY'] != 0)|(sv2_desi_tgt & sv2_desi_mask['SCND_ANY'] != 0)|(sv3_desi_tgt & sv3_desi_mask['SCND_ANY'] != 0)


# In[21]:


# Number of sources of each target type
n_bgs = len(zpix_cat[is_bgs])
n_lrg = len(zpix_cat[is_lrg])
n_elg = len(zpix_cat[is_elg])
n_qso = len(zpix_cat[is_qso])
n_mws = len(zpix_cat[is_mws])
n_scnd = len(zpix_cat[is_scnd])


# In[22]:


# Let us look at the numbers visually - 

plt.figure(figsize = (10, 8))

targets = ['BGS', 'LRG', 'ELG', 'QSO', 'MWS', 'SCND']
numbers = [n_bgs, n_lrg, n_elg, n_qso, n_mws, n_scnd]

plt.bar(targets, numbers, color = 'purple', alpha = 0.5)
plt.ylabel('Number of primary spectra')
plt.yscale('log')


# In[23]:


# Now let us look at the distribution of redshifts -

fig, axs = plt.subplots(4, 1, figsize = (9, 12))
bins = np.arange(0, 4, 0.2)

axs[0].hist(zpix_cat['Z'][is_bgs], color = 'C0', bins = bins, label = f'BGS: {n_bgs} sources')
axs[0].legend(fontsize = 14)
axs[0].set_ylabel("N(z)")
axs[1].hist(zpix_cat['Z'][is_lrg], color = 'C1', bins = bins, label = f'LRG: {n_lrg} sources')
axs[1].legend(fontsize = 14)
axs[1].set_ylabel("N(z)")
axs[2].hist(zpix_cat['Z'][is_elg], color = 'C2', bins = bins, label = f'ELG: {n_elg} sources')
axs[2].legend(fontsize = 14)
axs[2].set_ylabel("N(z)")
axs[3].hist(zpix_cat['Z'][is_qso], color = 'C3', bins = bins, label = f'QSO: {n_qso} sources')
axs[3].legend(fontsize = 14)
axs[3].set_ylabel("N(z)")
axs[3].set_xlabel("Redshift")


# #### Other masks

# `desi_mask` consists of the uppermost level targeting information in DESI. However, there can be sub-classes of targets. For example, BGS have different target masks depending on the selection criterion. Each of the different secondary target proposals have their own masks. They can be selected in a similar way as above, but with the respective columns in the redshift catalog. More information about Bitmasks in DESI is available [here](https://desidatamodel.readthedocs.io/en/latest/bitmasks.html).

# In[24]:


sv1_targetmask.bgs_mask.names


# In[25]:


sv1_targetmask.scnd_mask.names


# Now, we will explore the Healpix/ directory and see how to access the required coadded spectra

# <a class="anchor" id="hpx"></a>
# ## Healpix/ Directory
# 
# This directory divides the coadded spectra of targets based on the healpix number and the observing conditions (dark/bright).

# In[26]:


healpix_dir = f'{specprod_dir}/healpix'


# In[27]:


os.listdir(healpix_dir)


# The directories in `healpix` folder are divided based on the `SURVEY` and then by the `PROGRAM` (dark or bright or backup).

# In[28]:


# Define survey and program here - 
survey = 'sv1'
program = 'bright'


# In[29]:


os.listdir(f'{healpix_dir}/{survey}')


# In[30]:


sorted(os.listdir(f'{healpix_dir}/{survey}/{program}'))[0:10]


# <a class="anchor" id="spectra_access"></a>
# # Accessing and Plotting Spectra of a Single Object
# 
# Under the healpix/ directory, the different healpix directories are grouped together in healpix subgroups. 
# 
# To access a particular coadded spectra, we need the following information:
# 
# * **survey**: SURVEY that the target was observed in. This can be sv1, sv2, or sv3.
# * **program**: FIBER ASSIGNMENT PROGRAM. This is the planned observing conditions for the target. It can be dark or bright or backup. In the case of sv1, we also have "other".
# * **healpix**: HEALPIX Number, which depends on the position of the object in the sky.
# 
# The coadd filepath can be created using this -
# ```
# {healpix_directory}/{survey}/{program}/{healpix_group}/{healpix}/coadd-{survey}-{program}-{healpix}.fits
# ```
# The healpix group can be derived from the healpix number. 

# In[31]:


# Selecting a random object which has multiple spectra in DESI
sel = (zpix_cat['ZCAT_NSPEC'] >= 4)
targets = zpix_cat[sel]['TARGETID']

## Selecting random TARGETID from these targets
ii = 13
targetid = targets[ii]


# In[32]:


# Selecting the redshift catalogs rows for the particular targetid
rows = zpix_cat['TARGETID'] == targetid
zcat_sel = zpix_cat[rows]


# In[33]:


zcat_sel


# In[34]:


# Defining healpix, survey, and program variables for this target

survey_col = zcat_sel['SURVEY'].astype(str)
program_col = zcat_sel['PROGRAM'].astype(str)
hpx_col = zcat_sel['HEALPIX']

# Selecting the primary spectra - 
is_primary = zcat_sel['ZCAT_PRIMARY']

# Information needed to access the spectra 
survey = survey_col[is_primary][0]
program = program_col[is_primary][0]
hpx = hpx_col[is_primary][0]    ## This is same for all the rows, given its the same TARGET. But, just to be consistent.

# Let us explore the target directory
# Note that the target directory is different for the different spectra.
# We first explore the primary spectra and look at the other spectra later.
tgt_dir = f'{healpix_dir}/{survey}/{program}/{hpx//100}/{hpx}'


# In[35]:


os.listdir(tgt_dir)


# In every directory, we have the following files (together with a description of what they contain): 
# 
# * **spectra-{survey}-{program}-{healpix}.fits**: individual exposure spectra that go into the coadds.
# * **coadd-{survey}-{program}-{healpix}.fits**: coadded spectra of the targets
# * **redrock-{survey}-{program}-{healpix}.fits**: redshift information obtained from the redrock.
# * **rrdetails-{survey}-{program}-{healpix}.h5**: information about the templates used by redrock.
# * **qso_mgii-{survey}-{program}-{healpix}.fits**: redshift information after using MgII selection for QSOs. This is run on the redrock output. For Everest this only exists if QSO targets are in the redshift file. 
# * **qso_qn-{survey}-{program}-{healpix}.fits**: redshift information after running the redrock output through QuasarNet. For Everest this only exists if QSO targets are in the redshift file. 
# * **logs**: logs from the processing of the data. You can safely ignore this.
# 
# Let us explore the coadd* and redrock* files

# ### Healpix based coadd file

# In[36]:


# Filename - 
coadd_filename = f'coadd-{survey}-{program}-{hpx}.fits'


# In[37]:


h_coadd = fits.open(f'{tgt_dir}/{coadd_filename}')
h_coadd.info()


# We can see that every coadd* file has 18 extensions:
# * **FIBERMAP** consists of information about the different targets
# * **EXP_FIBERMAP** contains the exposure information of the targets
# * For every camera (B,R,Z), we have wavelength, flux, inverse variance and resolution arrays for the individual targets.
# * **SCORES** contains more information about the coadds of the target spectra
# 
# Detailed datamodel is available [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/healpix/SURVEY/PROGRAM/PIXGROUP/PIXNUM/coadd-SURVEY-PROGRAM-PIXNUM.html). <br/>
# Let us plot the position of different sources in the sky and overplot the different `Milky Way Survey (MWS)` sources

# In[38]:


fm = Table(h_coadd['FIBERMAP'].data)
is_mws = (fm[f'{survey.upper()}_DESI_TARGET'] & sv1_targetmask.desi_mask['MWS_ANY']) != 0
h_coadd.close()


# In[39]:


plt.figure(figsize = (8, 8))

plt.scatter(fm['TARGET_RA'], fm['TARGET_DEC'], color = 'grey', s = 50, label = 'All')
plt.scatter(fm['TARGET_RA'][is_mws], fm['TARGET_DEC'][is_mws], color = 'r', s = 50, marker = 'x', label = 'MWS')
plt.xlabel('R.A. (deg)')
plt.ylabel('DEC (deg)')
plt.legend()


# ### Healpix based redrock file

# In[40]:


# Filename -
z_filename = f'redrock-{survey}-{program}-{hpx}.fits'


# In[41]:


h_rr = fits.open(f'{tgt_dir}/{z_filename}')
h_rr.info()
h_rr.close()


# The redrock* file has 4 extensions:
# 
# * **REDSHIFTS** consists of redshift information and outputs from redrock.
# * **FIBERMAP** is similar to the one in coadd* file and has information about the targets.
# * **EXP_FIBERMAP** is again similar to the one in the coadd* file and has exposure information about the targets.
# * **TSNR2** contains information about the expected SNR measurements for the targets.
# 
# Information about the datamodel is [here](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/healpix/SURVEY/PROGRAM/PIXGROUP/PIXNUM/redrock-SURVEY-PROGRAM-PIXNUM.html). <br/>
# You can in principle use these files directly and write your own code to access the spectra. However, `desispec` also provides a function for accessing the coadded spectra as shown below.

# <a class="anchor" id="spectra"></a>
# ## Working with Coadded Spectra using _desispec.io.read_spectra()_

# In[42]:


# Using desispec to read the spectra

coadd_obj = desispec.io.read_spectra(f'{tgt_dir}/{coadd_filename}')
coadd_tgts = coadd_obj.target_ids().data


# In[43]:


# Selecting the particular spectra of the targetid

row = (coadd_tgts == targetid)
coadd_spec = coadd_obj[row]


# In[44]:


coadd_spec.wave


# In[45]:


coadd_spec.flux


# In[46]:


# Plotting this spectra -

plt.figure(figsize = (20, 6))
# Plot the spectrum from each arm (B,R,Z) in blue, green, red

plt.plot(coadd_spec.wave['b'], coadd_spec.flux['b'][0], color = 'b', alpha = 0.5)
plt.plot(coadd_spec.wave['r'], coadd_spec.flux['r'][0], color = 'g', alpha = 0.5)
plt.plot(coadd_spec.wave['z'], coadd_spec.flux['z'][0], color = 'r', alpha = 0.5)
# Over-plotting smoothed spectra in black for all the three arms
plt.plot(coadd_spec.wave['b'], convolve(coadd_spec.flux['b'][0], Gaussian1DKernel(5)), color = 'k')
plt.plot(coadd_spec.wave['r'], convolve(coadd_spec.flux['r'][0], Gaussian1DKernel(5)), color = 'k')
plt.plot(coadd_spec.wave['z'], convolve(coadd_spec.flux['z'][0], Gaussian1DKernel(5)), color = 'k')
plt.xlim([3500, 9900])
plt.xlabel('$\lambda$ [$\AA$]')
plt.ylabel('$F_{\lambda}$ [$10^{-17} erg\ s^{-1}\ cm^{-2}\ \AA^{-1}$]')
plt.show()


# The coadded spectra available is divided based on the observed (B,R,Z) camera. We can obtain the joint spectrum using the available `coaddition.coadd_cameras` function.

# In[47]:


# Combined Spectra - 

spec_combined = coaddition.coadd_cameras(coadd_spec)


# In[48]:


spec_combined.wave


# In[49]:


spec_combined.flux


# In[50]:


# Plotting this combined spectra - 

# Plotting this spectra -

plt.figure(figsize = (20, 6))
# Plot the combined spectrum in maroon
plt.plot(spec_combined.wave['brz'], spec_combined.flux['brz'][0], color = 'maroon', alpha = 0.5)
# Over-plotting smoothed spectra 
plt.plot(spec_combined.wave['brz'], convolve(spec_combined.flux['brz'][0], Gaussian1DKernel(5)), color = 'k', lw = 2.0)
plt.xlim([3500, 9900])
plt.xlabel('$\lambda$ [$\AA$]')
plt.ylabel('$F_{\lambda}$ [$10^{-17} erg\ s^{-1}\ cm^{-2}\ \AA^{-1}$]')
plt.show()


# Let us now plot all the available spectra available for this object

# In[51]:


# Number of spectra 
n = len(zcat_sel)

fig, ax = plt.subplots(n, 1, figsize = (12,(4*n)))

for jj in range(n):
    survey = survey_col[jj]
    program = program_col[jj]
    hpx = hpx_col[jj]
    
    spectype = zcat_sel['SPECTYPE'].astype(str).data[jj]
    primary_flag = zcat_sel['ZCAT_PRIMARY'].data[jj]

    tgt_dir = f'{healpix_dir}/{survey}/{program}/{hpx//100}/{hpx}'
    coadd_filename = f'coadd-{survey}-{program}-{hpx}.fits'
    coadd_obj = desispec.io.read_spectra(f'{tgt_dir}/{coadd_filename}')
    coadd_tgts = coadd_obj.target_ids().data
    row = (coadd_tgts == targetid)
    coadd_spec = coadd_obj[row]

    spec_combined = coaddition.coadd_cameras(coadd_spec)
    
    # Plot the combined spectrum in maroon
    ax[jj].plot(spec_combined.wave['brz'], spec_combined.flux['brz'][0], color = 'maroon', alpha = 0.5)
    # Over-plotting smoothed spectra 
    ax[jj].plot(spec_combined.wave['brz'], convolve(spec_combined.flux['brz'][0], Gaussian1DKernel(5)), color = 'k', lw = 2.0)
    ax[jj].set(xlim = [3500, 9900], xlabel = '$\lambda$', ylabel = '$F_{\lambda}$')
    
    trans = ax[jj].get_xaxis_transform()
    ax[jj].annotate(f'{survey}, {program}', xy = (6000, 0.85), xycoords = trans, fontsize = 16)
    ax[jj].annotate(f'SPECTYPE : {spectype}', xy = (8000, 0.85), xycoords = trans, fontsize = 16)
    ax[jj].annotate(f'PRIMARY Flag : {primary_flag}', xy = (8000, 0.75), xycoords = trans, fontsize = 16)
    
plt.tight_layout()


# Redrock uses a set of templates to classify sources and find their redshifts. You can use the zbest fit coefficients with the redrock-templates to compare the spectra to the best-fit template. A tutorial on how to do this is available [here](https://github.com/desihub/tutorials/blob/main/redrock/RedrockOutputs.ipynb).

# <a class="anchor" id="ref"></a>
# # References
# 
# * DESI experiment paper: https://arxiv.org/abs/1611.00036
# * Information about EDR: https://data.desi.lbl.gov/public/edr
# * Information about Survey Validation: https://desi.lbl.gov/trac/wiki/SurveyValidation (**link exclusive to DESI collaborators**)
# * Targetting Information: 
#     * [SV1](https://desi.lbl.gov/trac/wiki/TargetSelectionWG/SurveyValidation) (**link exclusive to DESI collaborators**)
#     * [SV2](https://desi.lbl.gov/trac/wiki/TargetSelectionWG/SV2) (**link exclusive to DESI collaborators**)
#     * [SV3](https://desi.lbl.gov/trac/wiki/TargetSelectionWG/SV3) (**link exclusive to DESI collaborators**)
#     * [main](https://ui.adsabs.harvard.edu/abs/2023AJ....165...50M/abstract) survey
# * Datamodel information: https://desidatamodel.readthedocs.io/en/latest/
#     * [tiles-fuji.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/tiles-SPECPROD.html)
#     * [exposures-fuji.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/exposures-SPECPROD.html)
#     * [Redshift catalogs](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/index.html)
#     * [zall-pix-fuji.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zall-pix-SPECPROD.html)
#     * [zall-tilecumulative-fuji.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zall-tilecumulative-SPECPROD.html)
#     * [zpix-SURVEY-PROGRAM.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zpix-SURVEY-PROGRAM.html)
#     * [ztile-SURVEY-PROGRAM-GROUPTYPE.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/zcatalog/zpix-SURVEY-PROGRAM.html)
#     * [coadd-SURVEY-PROGRAM-PIXNUM.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/healpix/SURVEY/PROGRAM/PIXGROUP/PIXNUM/coadd-SURVEY-PROGRAM-PIXNUM.html)
#     * [redshift-SURVEY-PROGRAM-PIXNUM.fits](https://desidatamodel.readthedocs.io/en/latest/DESI_SPECTRO_REDUX/SPECPROD/healpix/SURVEY/PROGRAM/PIXGROUP/PIXNUM/redrock-SURVEY-PROGRAM-PIXNUM.html)
# * Information about DESI bitmasks: https://desidatamodel.readthedocs.io/en/latest/bitmasks.html
# * Redrock Template Tutorial: https://github.com/desihub/tutorials/blob/main/redrock/RedrockOutputs.ipynb

