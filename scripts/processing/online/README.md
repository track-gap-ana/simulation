Scripts that take files that are already online processed and uncompress+split them, SRT clean, compute CommonVariables etc.

Steps from online to common variables:

1. Read SuperDST, convert to pulseseries map, trigger split etc.
   1. Find this script in offline_filters.read_superdst_files
2. SRT clean
3. Track recos
4. CommonVariables

You can find these segments in `segments`.