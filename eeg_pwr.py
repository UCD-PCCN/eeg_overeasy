#imports 
import mne
import numpy as np
import pandas as pd
import os
import glob
from matplotlib import pyplot as plt
import sys
import warnings

import seaborn as sns
from itertools import product as prod

import webbrowser

from PIL import Image, ImageDraw, ImageFont

import itertools as itr
from functools import reduce

import scipy.stats as sts
import scipy

#classes
class eeg_dynamic_read:   
    '''class reads in eeg data and finds the appropriate read in method from mne.io
    
    file : (String) - Name of eeg data file to read in
    montage : (Sting) - name of montage file associated with the eeg file
    
    '''
    def __init__(self, file, montageFile):
        self.file=file
        self.montage=montageFile
    
    def read_eeg(self):
        eeg_type='read_'+self.file.split('.')[-1]
        method=getattr(self, eeg_type, lambda: 'Invalid Type')
        return method()
    
    def read_sqd(self):
        return mne.io.read_raw_kit(self.file,self.montage)
    
    def read_vhdr(self):
        return mne.io.read_raw_brainvision(self.file,self.montage)

    def read_ctf(self):
        return mne.io.read_raw_ctf(self.file,self.montage)
    
    def read_edf(self):
        return mne.io.read_raw_edf(self.file,self.montage)

    def read_bdf(self):
        return mne.io.read_raw_edf(self.file,self.montage)
    
    def read_gdf(self):
        return mne.io.read_raw_ctf(self.file,self.montage)

    def read_egi(self):
        return mne.io.read_raw_egi(self.file,self.montage)
    
    def read_mff(self):
        return mne.io.read_raw_egi(self.file,self.montage)
    
    def read_set(self):
        return mne.io.read_raw_eeglab(self.file,self.montage)

    def read_nxe(self):
        return mne.io.read_raw_eximia(self.file,self.montage)
    
    def read_cnt(self):
        return mne.io.read_raw_cnt(self.file, self.montage)
    
class subject:
    def __init__(self, ID, data, montage, eventIDs=None):
        """
        Subject class the contain individual subject data and the methods necessary to 
        do all within subjects processing and analyses
        
        ID: (String/Int) - Subject Identifier
        data : (String) - name of data file - automatically loaded into mne with dynamic read
        montage : (String) - name of monatage file automatically loaded into mne with dynamic read
        eventIDs : (Dict) - mapping of event names to event codes
        
        """
        self.ID=ID
        self.data=eeg_dynamic_read(data, montage).read_eeg()
        self.events=mne.find_events(self.data)
        self.event_ID=eventIDs if eventIDs else list(np.unique(self.events[:,2]))
        self.sample_rate=self.data.info['sfreq']
        
        #data stores for sample data
        #electorde x event code x event x time
        self.sample_channels=None
        self.sample_store=None
        self.sample_events=None
        
        #bootstrap dependedant struture
        # boot shape x random Draws
        self.boot_store=None
    
    def get_item_eeg(self, tmin=-.1, tmax=.8, baseline=(None,0.0), 
                         events=None, chans=[],  average=False, store=False):
        
        """function epochs the data and returns an electrode x event code x event x sample array, with option
        to store in the sample_store attribute.
          
        tmin : (float/int) - time in seconds to begin epoch
        tmax : (float/int) - time in seconds to end epoch
        baseline : (tuple of ints) - beginning, end of baseline period
        events : (list of strings or Ints) list of events names to pull out
        chans : (list of strings) - list of channel names to get data from
        average : (boolean) : whether or not to average the data
        store : (boolean) : whether or not to store data in the class attribute
        
        """
        
        if not events:
            raise 'Event of Interest Must be specified'
        if not chans:
            chans=[self.data.info['ch_names'][k] for k in mne.pick_types(self.data.info, eeg=True)]
        
        erp=mne.Epochs(self.data, events=self.events, event_id=self.event_ID, tmin=tmin,
                       picks=mne.pick_channels(self.data.info['ch_names'], chans),
                    tmax=tmax, baseline=baseline, preload=True)
        
        #swap axes 0,1
        if average:
            ret=erp[event].average(picks=chans)
        else:
            ret=np.array([erp[event].get_data() for event in events])
            
            #strutuces the array
            ret=np.swapaxes(np.swapaxes(ret, 0, 2), 1, 2)
        
        #option to store the data as part of the class
        #or return in
        if store:
            self.sample_channels=chans
            self.sample_store=ret
        else:   
            return ret
    
        
    def random_draw(self, array, nDraws=100, sampleSize=None, replacement=True):
        '''
        returns an array of boot-strapped means along the last axis of the passed array
        
        array : (nD array)
        nDraws : (int) - number of means to generate
        sampleSize : (int) - number of sample to take on each draw
        replacment : (boolean) - replacement for draws
        '''
        
        if sampleSize:
            warnings.warn("Sampling at adjusted sample size is not recommended for boot-strapping")
            
            
        if not replacement:
            warnings.warn("Sampling at without replacement is not recommended for boot-strapping")
        
        #pull size of the array's last dimension as deflault sample size
        samplesSize = sampleSize if sampleSize else array.shape[-1] 
        
        def _make_index(shape):
            '''takes in array shape tuple and out puts a list of all 
            index combinations'''
            ind=list(map(range, shape))
            ind=list(map(list, ind))
            return list(prod(*ind))
        
        #get the necessary array shape for initiating the matrix
        arrShape=list(array.shape)[:-1]
        arrShape.extend([nDraws])
        
        #intiate thats shape x random draw
        boot_dist=np.zeros(arrShape)
        
        for idx in _make_index(arrShape):
            #pull out random indexes and slice the array
            rand_idx=np.random.choice(array.shape[-1], size=sampleSize, replace=replacement)
            
            #we have to pull out all but the last element of the idx tuple so that we're drawing
            #from the correct groups
            pulled_data=array[idx[:-1]]
            boot_dist[idx]=np.mean(pulled_data[rand_idx])
        
        return boot_dist
        
    
    def get_mean_amp(self, flatten_axes=None, boots=200, samples=None):
        
        '''get the mean amplitude accross the epoch'''
        mean_amp=np.mean(self.sample_store, (len(self.sample_store.shape)-1))
        
        if flatten_axes:
            mean_amp=mean_amp.reshape(*mean_amp.shape[:flatten_axes], -1)
        self.boot_store= self.random_draw(mean_amp,nDraws=boots, sampleSize=samples)
     
        
    
    def peak_latency(self):
        pass
    
    def get_summary_stats(self, stats=['std']):
        '''returns array of summary statistics along the last axis and axis mappings
        
        stats : (list of strings) - names of numpy stats functions to be called on the data
        
        '''
        if len(stats)==1:
            return getattr(np, stats[0])(self.boot_store, -1)
        else:
            return np.array([getattr(np, k)(self.boot_store, -1) for k in stats])
         
class boots: 
    def __init__(self, fileDir=None,  dataType=None, montage=None, eventMap=None):
        
        '''class that serves as the group level data type
        
        fileDir : (String) - file path (organized to BIDs specs)
        dataType : (String) - type of eeg file being loaded in
        montage : (Stinge) - path for montage file
        eventMap : (Dict) - dictionary with Key, Value pairs that specify event name, event code
        
        '''
        if not dataType:
            raise 'EEG file type must be specified'
       
        #search the whole directory tree for anything with the 
        #specified data type
        self.directory=fileDir
        self.files=glob.glob(os.path.join(fileDir, '**', 'EEG', ('*' + dataType)))                            
        self.montage=mne.channels.read_montage(montage) if montage else None
        self.data=None
        self.eventMap=eventMap
        
        #stores for boot_SE
        #so it can be called at will from
        #script
        self.boot_SE=None
        
        self.pwr=None
        
        
        #reference for array structure so we can 
        #have name based accessors in the GUI
        self.key2axes={'subject':0, 'electrode':1, 'eventName':2, 'event':3, 'time':4}
        
        self.subsets={}
        
    def eeg_error(self, e):
        
        
        font=ImageFont.truetype('arial.ttf', 50)
        
        img=Image.open(os.path.join('pictures', 'eeg_splat.jpg'))
        
        draw = ImageDraw.Draw(img)
        draw.text((150, 300), str(e), fill='rgb(255,0,0)', font=font)
        img.save(os.path.join('pictures', 'eegs_errormessage.jpg'))
        
        br=webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s")
        
        br.open(os.path.join('pictures', 'eegs_errormessage.jpg'))
    
    
    
    def get_error(self, across='subject', stat='mean'):
        '''function to get average SE from the store across designated axis
        across : (string/int) - Name/number of one of the axis dimensions 
        type : (string) - name of numpy method the can be called over the array
        '''
        try:
        
            ax=self.key2axes[across] if isinstance(across, str) else across
        
            return getattr(np, stat)(self.boot_SE, axis=ax)
    
        except Exception as e:
            self.eeg_error(e)
            raise
    
    
    
    def get_name(self, fstring):
        '''gets subject ID from file string'''
        return fstring.split(os.sep)[-3]
        
    def load_data(self):
        '''load method after intial init, this will give us the flexibility to restart after node subsetting if we need to'''
        dats=[subject(ID=self.get_name(file),data=file, montage=self.montage, eventIDs=self.eventMap) for file in self.files]
        
        #default group level event mappings
        #to the subject level defualt
        if not self.eventMap:
            warnings.warn('No event mappings specified... Using event codes as names')
            self.eventMap=dats[0].event_ID
        
        self.data=dats
    
    
    def epoch_subjects(self,tmin=-.2, tmax=.8, baseline=(None,0.0), 
                         event=None, chans=[], average=False, store=False):
       
        #sets what we pulled out for the analyses so we can 
        self.subsets['electrodes']=chans
        self.subsets['events']=event
        
        #creates the epoch data for each subject
        [s.get_item_eeg(tmin=tmin, tmax=tmax, baseline=baseline,events=event, chans=chans, average=average, store=store) for s in self.data]
        
        
    def mean_amplitude(self, flatten_axes=None, boots=200, samples=None, return_stats=['mean'], output=False):
        
        if flatten_axes >2:
            warnings.warn('Axis conservation may result in longer processing times')
        #boot each subject in turn
        [s.get_mean_amp(flatten_axes=flatten_axes, boots=boots, samples=samples) for s in self.data]
        
        
        if return_stats:
            #save standard error measures for each subject into the class
            self.boot_SE=np.array([s.get_summary_stats(stats=return_stats) for s in self.data])
        if output:
            return self.boot_SE

    def plot_quality_topo(self, across='subjects', stat='mean', montage_file=None):
        #if no montage is specified try to 
        #pull a defualt from the class
        if not montage_file:
            try:
                montage_pos=self.montage.pos[:,[0,1]]
            except:
                print ("no montage specified and no default available")
        else:
            montage_pos=mne.montage(montage_file).pos[:,[0,1]]
	
        plt_avg=mne.viz.plot_topomap(self.get_error(across=across, stat=stat), montage_pos)
        
    
    def _power_anova(self, alpha=.05, effSize=1, N=20, design='2x1', effect_factor=1, std=1):
        
        #turn design into int representing factor groups
        #so we can use them in degrees of freedom calcualtion
        split_design=design.split('x')
        split_design=list(map(int, split_design))
        
        #is this a correct calucaltion of the numerator df??
        m=split_design[effect_factor] if not effect_factor == 'interaction' else reduce(lambda x, y: x*y, split_design)
        
        df_num=m     
        df_denom=N-m
        
        #create an f distribution taking the bootstrapped
        #SE into account
        f=sts.f.ppf(1-alpha, df_num, df_denom, scale=std)
        
        ncp=(effSize**2)*N
        
        power=scipy.special.ncfdtr(1, 18, ncp, f)
        return power
    
    def _power_t(self, alpha=.05, effSize=1, N=20, std=1):
        df=N-1
        c=sts.t.ppf(1-alpha, df, scale=std)
        ncp=0
        power=sts.nct.cdf(c, df, ncp, loc=effSize, scale=std)
        return power
        

    def power_analysis(self, n_subs, es,model='anova', model_specs={'alpha': 0.5, 'design':'2x1','effect_factor':'interaction'}, store=True):
        
        '''function for creating power analysis for multiple values of number of subject and effect size
        
        nSubs : (list/array of ints) - list of hypothetical number of subject values
        ES : (list/array) - list of hypothetical effect sizes
        model_spec: (dictionary) - key/vaule pairings of model parameters for the analysis of interest. Exact parameters
                    will vary based on analysis
        store: (boolean) - option to store resulting analysis
        
        '''
        if 1 in n_subs:
            self.eeg_error("You can\'t do t-tests with one subject!")
        
        pwrs = np.zeros((self.boot_SE.shape[1], len(n_subs), len(es)))
        
        #pull the average standard error across subjects
        data_array=self.get_error(across='subject', stat='std')* 1e6
        
        #create and index list so we can use single loop
        idx_list=itr.product(range(pwrs.shape[0]), range(pwrs.shape[1]), range(pwrs.shape[2]))
        
        for idx in idx_list:
            pwrs[idx]=getattr(self, '_power_'+model)(**model_specs, std=data_array[idx[0]], 
                                                                                   N=n_subs[idx[1]], effSize=es[idx[2]])
        
        if store:
            self.pwr = {'power_values':pwrs, 'effect_sizes':es, 'sample_sizes':n_subs}
        else:
            return pwrs

    
    
    def power_table(self, channels=None, col_wrap=3):
        ''' plots the stored power array attribute in the class
        
        channels : (list/None/string='Average') - either a list of channels to plot, None specifying all channels,  "average" specifying the 
                                                average power overall channels
        '''
        if channels=='average':
        
            # Draw a heatmap with the numeric values in each cell
            f, ax = plt.subplots(figsize=(9, 6))
            sns.heatmap(np.mean(self.data.pwr['power_values'], 0), annot=True, fmt="f", linewidths=.5, ax=ax,                    xticklabels=self.data.pwr['effect_sizes'], yticklabels=self.data.pwr['sample_sizes'])
            ax.set_title('Power at different N and ES ')
            plt.xlabel('Effect Sizes')
            plt.ylabel('Numbers of subjects')
       
        else:
            #squirrels into a subset of class 
            chans=self.data[0].data.info['ch_names']
            
            #conditioally set the index function so we can loop over stuff
            ch_indicies=mne.pick_channels(chans, channels) if channels else np.arange(self.pwr['power_values'].shape[0])
            
            rows=np.ceil(len(ch_indicies)/col_wrap)
            plots, axs = plt.subplots(int(rows), col_wrap, figsize=((5*len(self.pwr['effect_sizes'])),(3*len(ch_indicies))))
            
            #unravel the axs shape so we can loop over 
            #a single dimension
            axsr=axs.ravel()
            
            for ax in range(len(ch_indicies)):
                sns.heatmap(self.pwr['power_values'][ch_indicies[ax]], annot=True, fmt="f", linewidths=.5, ax=axsr[ax], xticklabels=self.pwr['effect_sizes'], yticklabels=self.pwr['sample_sizes'])
                axsr[ax].set_title('Power Estimates for Channel ' + chans[ch_indicies[ax]])
                axsr[ax].set_xlabel('Effect Sizes')
                axsr[ax].set_ylabel('Numbers of subjects')
                        