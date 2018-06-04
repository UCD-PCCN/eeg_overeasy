## eeg_overeasy
To make an ohm-lette you have to crack a few EEGs

Eeg_overeasy allows users to analyze the quality of their data quality and conduct power analyses on small amount of representative EEG data. Currently this tool works spesificially for mean amplitude ERP analysis, but in the future it may be expanded to other EEG/ERP analysis strategies.

This tool can be access through an online GUI located here : 

/url

or by dowloading and implimenting the class in custom scripts.

# Inputs

Files

Eeg_overeasy will load any number of raw EEG files in most common formats (list of tested file types) into MNE, and requires a montage file. These files should be processed to whatever extent the user wishes to power analysis to be conducted on (filtered, artifact rejected, ICA-corrected etc.). For use in the online GUI, these files should be named per subject ID and placed in a folder with a montage file.

Sample rate - in ms (? check if actually needed)

Events - as list of integers

User must spesifiy which events in the files correspond to EEG related to the stimuli which is to be analyzed. The events need not exactly represent the planned manipulation, but they do need to represent the same sort of stimuli. User can spesify any number of events, but they will all be treated equivalently so they should all be similar stimuli as to not bias the estimate of data quality. If the user wishes use the option to run the power analysis at different numbers of items, it should be noted that maximum number items which can be included in the power analysis is equal to the minimum number of items included in any of the data files uploaded.

Epoch - in ms

The time epoch spesified should represent the timing of whatever ERP component the user is interested in analyzing. This epoch will be used to measure the mean amplitude of EEG data for every event in every file.

Electrodes - as list of stings

User must spesify a list of which electrodes to conduct the power/data quality analysis on. These should reflect which electodes would be used to analyze an effect on whichever component ERP comonent is being analyzed. The electrodes must be spesified as a list of strings which exactly match the according electrode label in the header of the montage file.

Effect size

For the power analysis, the user must spesify an effect size. Ideally, this is based on previous research. (maybe we could add an option to spesify multiple effect sizes?)

# Data quality estimate

For every electrode, item, and subject included, mean amplitude EEG measurements are taken using the epoch spesified. Then  mean amplitudes are averaged across items to get an mean for each electrode and subject. To estimate the data quality, the standard error around these means are esimated using bootstrapping. Per electode, these estimates will then be averaged across subjects, to give the best estimate for the average quality of a subject's data from this spesific recording enviroment. Then, these data quality estimates will be output to the user in the form of a table (and maybe some plots...), and passed to the power analysis function.

# Power analysis

This function uses the bootstrapped estimates of the standard error to conduct a t-test power analysis for the given effect size and different numbers of subjects (10, 15, 20, 25, 30?). The analyses will be run for each electrode spesified, as well as for an average. (plots...?)

# Item analysis option...

to be continued...
