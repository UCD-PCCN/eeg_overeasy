# eeg_overeasy

To make an ohm-lette you have to crack a few EEGs

![eegs_overeasy](eeg_overeasy/pictures/eegs_overeasy.jpg)

Eeg_overeasy allows users to analyze data quality and conduct power analyses on a small amount of representative EEG data. Currently this tool works specifically for mean amplitude ERP analysis, but in the future it may be expanded to other EEG/ERP analysis strategies.

This tool can be accessed through an online GUI located here : 

[GUI link (not functional yet)](put_url_here)

or by dowloading and implementing the class in custom scripts.

## Inputs

### _Mandatory_

##### Data files

Eeg_overeasy will load any number of raw EEG files in most common formats (cnt, bdf, eeg, etc.) into MNE, and requires a montage file of electrode number and locations. These files should be pre-processed to whatever extent the user wishes the power analysis to be conducted on (filtered, artifact rejected, ICA-corrected, etc.). For use in the online GUI, these files should be named per subject ID and placed in a folder with a montage file.

##### *Sample rate - in ms (? check if actually needed)*

##### Events - as list of integers

User must specify which events in the files correspond to EEG related to the stimuli which is to be analyzed. The events need not exactly represent the planned manipulation, but they do need to represent the same sort of stimuli. User can specify any number of events, but they will all be treated equivalently so they should all be similar stimuli so as to not bias the estimate of data quality. If the user wishes to use the option to run the power analysis at different numbers of items, it should be noted that maximum number items which can be included in the power analysis is equal to the number of items included in any of the data files uploaded.

##### Epoch - in ms

The time epoch specified should represent the timing of whatever ERP component the user is interested in analyzing. This epoch will be used to measure the mean amplitude of EEG data for every event in every file.

### _Optional_

##### Electrodes - as list of stings

User may specify a list of electrodes to conduct the power/data quality analysis on. The analysis will default to all electrodes if this parameter is left blank. The chosen electrodes should reflect which electodes would be used to analyze an effect on whichever component ERP comonent is being analyzed. The electrodes must be specified as a list of strings which exactly match the according electrode label in the header of the montage file.

#### _Additional power analysis inputs_

For the normal power analysis option, user must include up to 4 inputs for both 'Effect size' and 'Subject sample size'. 'Item sample size' will then use a single value, which defaults to the maximum number of items possible.

If the item power analysis option is selected, user must include only 1 input for 'Effect size', and include up to 4 inputs for 'Item sample size'. The power analysis will be conducted on this effect size and show the relation between different combinations of subject and item sample sizes.

##### Effect size(s)

User must specify an effect size. Ideally, this is based on previous research. EEG_overeasy allows for the power analysis to be conducted on up to 4 effect sizes.

##### Subject sample size(s)

User must specify the the subject sample sizes for the power analysis to use. As many as 4 sample sizes can be used.

###### Item sample size(s)

User may specify the number of items per subject for the power analysis to use. If left blank, this defaults to the maximum number of possible items. If the item power analysis option is used, the user may include as many as 4 item sample sizes can be used for the analysis. (see item analysis option below)

## Data quality estimate

For every electrode, item, and subject included, mean amplitude EEG measurements are taken using the epoch specified. Then mean amplitudes are averaged across items to get an mean for each electrode and subject. To estimate the data quality, the standard error around these means are estimated using bootstrapping. Per electode, these estimates will then be averaged across subjects, to give the best estimate for the average quality of a subject's data from this specific recording enviroment. Then, these average data quality estimates will be available to the user in the form of an array, or plotted as a topographic map. Further, user can access the variability of these estimates.

## Power analysis

This function uses the bootstrapped estimates of the standard error to conduct a t-test power analysis for a set of effect sizes and different numbers of subjects (up to 4 of each). The analyses will be run for every electrode, but output only for which electrodes were selected in addtion to the average of the selected electrodes. 

#### How it works:

Mean amplitudes are measured for each subject's sample data (using whatever events and time epochs are specified). For each electrode and subject, the standard error around their average mean amplitude is calculated by bootstrapping this mean 200 times. This bootstrapped estimate of the standard error (BESE), scaled by a hypothetical sample sizes of subjects, is used to create a (normal) null hypothesis mean distribution around 0. An alternative hypothesis mean distribution is created using the same parameters as the null distribution, but centered around a value equal to a hypothetical effect size. A critical value is calculated from the null distribution (two tailed - 97.5 percentile). The percent of the alternative distribution which falls beyond this critical value is used as an estimate of power.

This process is then repeated for every combination of specified electrodes, subject sample sizes, and effect sizes. 

### Item analysis option

This option estimates the implications of reducing the number of experimental items per subject for statistical power. During the bootstrapping procedure, the distribution of means is produced using a fewer number of random draws than the number of itmes available. The power analysis is then conducted on the set of electrodes, each with a BESE for up to 4 sample sizes of items, and with up to 4 sample sizes of subjects. To simplify output, if the item analysis option is selected, the effect size of the power analysis is kept constant at some value. 
