Scripts that further process trigger level simulation files. Applying wavedeform, splitting, cleaning, track reco, CommonVariables, etc. on trigger level files.

Order needs to be:

1. Base process (wavedeform etc.)
2. SRT cleaning
3. Track reco
4. CommonVariables

The script trigger_to_track_reco.py takes in a trigger file and does base process, srt clean and track reco.