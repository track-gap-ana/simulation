Scripts that take files that are already online processed and uncompress+split them, SRT clean, compute CommonVariables etc.

Steps from online to common variables:

1. Read SuperDST, convert to pulseseries map, trigger split etc.
   1. Find this script in offline_filters.read_superdst_files
2. SRT clean
3. Track recos
4. CommonVariables

You can find these segments in `segments`.

One should also weight at some point, but original weights are fine as long as you use density.

Then there are scripts called XXX_i3_to_hdf5.py which read in .i3 files and produce an hdf5 file that can be used for plotting.

The plotting is done with plot_XXX_hdf5.py. Remember that CORSIKA weighting needs # of files used.

The script utils.py contains some functions that are used by either of both of LLP (MuonGun) and CORSIKA, such as MMCTrackList info extractor, plot scripts, etc.