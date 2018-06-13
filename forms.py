from flask_wtf.file import FileField
from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField    
from wtforms import validators, ValidationError
    
class inputForm(Form):    
    electrodes = TextField("Electrodes",[validators.Required("Please enter your electrodes.")])
    eventCodes = TextField("Event codes",[validators.Required("Please enter your event codes.")])
    epochStart = TextField("Start of the epoch",[validators.Required("Please enter the start time of your epoch.")])
    epochEnd = TextField("End of the epoch",[validators.Required("Please enter the end time of your epoch.")])
    dataFile = FileField("Your data file")
    #fields for power analysis
    subjectSampleSizes = TextField("Subject sample sizes",[validators.Required("Please enter subj sample sizes.")])
    itemSampleSizes = TextField("Number of items",[validators.Required("Please enter number of items.")])    
    effectSizes = TextField("Effect sizes",[validators.Required("Please enter your expected effect sizes.")]) 
    
    submit = SubmitField("Send")
    
    



    