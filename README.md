## eeg_overeasy
To make an ohm-lette you have to crack a few EEGs

Eeg_overeasy allows users to analyze the quality of their data quality and conduct power analyses on small amount of representative EEG data. Currently this tool works spesificially for mean amplitude ERP analysis, but in the future it may be expanded to other EEG/ERP analysis strategies.

This tool can be access through an online GUI located here : 

/url

or by dowloading and implimenting the class in custom scripts.

# Inputs

Files

Eeg_overeasy will load any number of raw EEG files in most common formats (list of tested file types) into MNE, and requires a montage file. These files should be processed to whatever extent the user wishes to power analysis to be conducted on (filtered, artifact rejected, ICA-corrected etc.). 

Sample rate (? check if actually needed)

Events

User must spesifiy which events in the files correspond to EEG related to the stimuli which is to be analyzed. The events need not exactly represent the planned manipulation, but they do need to represent the same sort of stimuli. For instance if 

Epoch

Electrodes

Effect size

to be continued...
