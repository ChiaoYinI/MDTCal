#!/usr/bin/python

# Version 20160428b - Ken Abrams & Daniel Burk
#
# 20160428b - Make calcon load def , add calcon print debugs
# 20160424  - Fix file update when viewing/calcuculating fp/damping, combine veiwperiod/damping to viewsample def
# 20160421  - Set the default directory as the initial target when opening sigcal process dialog


from Tkinter import *
import sys
import MDTcaldefs
import tkMessageBox, tkFileDialog
import string
import subprocess

# Now, the most important part -- The legalese:
# COPYRIGHT  BOARD OF TRUSTEES OF MICHIGAN STATE UNIVERSITY
# ALL RIGHTS RESERVED

# PERMISSION IS GRANTED TO USE, COPY, COMBINE AND/OR MERGE, CREATE DERIVATIVE
# WORKS AND REDISTRIBUTE THIS SOFTWARE AND SUCH DERIVATIVE WORKS FOR ANY PURPOSE,
# SO LONG AS THE NAME OF MICHIGAN STATE UNIVERSITY IS NOT USED IN ANY ADVERTISING
# OR PUBLICITY PERTAINING TO THE USE OR DISTRIBUTION OF THIS SOFTWARE WITHOUT 
# SPECIFIC, WRITTEN PRIOR AUTHORIZATION.  IF THE ABOVE COPYRIGHT NOTICE OR ANY
# OTHER IDENTIFICATION OF MICHIGAN STATE UNIVERSITY IS INCLUDED IN ANY COPY OF 
# ANY PORTION OF THIS SOFTWARE, THEN THE DISCLAIMER BELOW MUST ALSO BE INCLUDED.

# THIS SOFTWARE IS PROVIDED AS IS, WITHOUT REPRESENTATION FROM MICHIGAN STATE
# UNIVERSITY AS TO ITS FITNESS FOR ANY PURPOSE, AND WITHOUT WARRANTY BY MICHIGAN
# STATE UNIVERSITY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT
# LIMITATION THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE.

# THE MICHIGAN STATE UNIVERSITY BOARD OF TRUSTEES SHALL NOT BE LIABLE FOR ANY
# DAMAGES, INCLUDING SPECIAL, INDIRECT, INCIDENTAL, OR CONSEQUENTIAL DAMAGES,
# WITH RESPECT TO ANY CLAIM ARISING OUT OF OR IN CONNECTION WITH THE USE OF
# THE SOFTWARE, EVEN IF IT HAS BEEN OR IS HEREAFTER ADVISED OF THE POSSIBILITY
# OF SUCH DAMAGES.
 
def BrowseDefaultDir(root_window,calcon_in,DirNameVar,):
    startdir = string.rstrip(calcon_in['target_dir'])
    startdir = string.rstrip(startdir,"\\") #          Strip off the backslash
    DirName=tkFileDialog.askdirectory(parent=root_window,initialdir=startdir, \
        title = 'Select Default Directory')
#    endloc=string.rfind(DirName,'/')+1   # 
    DirName = string.replace(DirName, "/", "\\")
    DirNameVar.set(DirName)
    calcon_in['target_dir'] = DirName+"\\"            # Restore the backslash	

# Loads all current tkinter data fileds to Calcon structure
#   to be called just before any MDTcaldefs functions
def LoadCalCon(calcon_in):
    calcon_in['station']=StationName.get()
    calcon_in['network']=StationNetwork.get()
    calcon_in['s_chname']=SensorName.get()
    calcon_in['s_chsen']=float(SensorSen.get())
    calcon_in['l_chname']=LaserName.get()
    calcon_in['l_chsen']=float(LaserSen.get())
    calcon_in['l_sen']=float(LaserReso.get())
    calcon_in['l_calconst']=float(LaserCal.get())
    calcon_in['target_dir']=str(DefaultDir.get())
    calcon_in['damping_ratio']=float(DampingValue.get())
    calcon_in['damping_ratio_source']=str(DampingFile.get())
    calcon_in['free_period']=float(FreeValue.get())
    calcon_in['free_period_source']=str(FreeFile.get())
    calcon_in['file_type']=DataFormat.get()

def BrowsePeriodFile(root_window,FileNameVar,DirNameVar):
    myFormats = [
    ('SAC File','*.sac'),
    ('CSS File','*.wfd'),
    ('Mini SEED File','*.mseed,*.msd,*.ms'),
    ('All Files','*')
    ]
#   get default directory off of screen 
    defaultdir = DirNameVar.get()
#   browse for data file using default directory    
    FileName=tkFileDialog.askopenfilename(parent=root_window,filetypes=myFormats,initialdir=defaultdir, \
        title = 'Select Free Period File')
    print '\nFree Period File Selected: {}'.format(FileName)
    FileNameVar.set(string.replace(FileName, "/", "\\"))

def CalcFreePeriod (calcon_in,free_file_in,free_period_in):
#   make sure CalCon is loaded    
    LoadCalCon(calcon_in)
#   show CalCon structure contents before calculation for troubleshooting
    print '*** Start Calc Free Period ***'
    print calcon_in
#   call freeperiod calc with root tkninter window & CalCon structure     
    freeval = MDTcaldefs.freeperiod(root,calcon_in)
#   update the CalCon with calculated value
    calcon_in['free_period']= freeval
#   update screen field with calc value
    free_period_in.set(freeval)

def BrowseDampingFile(root_window,FileNameVar,DirNameVar):
    myFormats = [
    ('SAC File','*.sac'),
    ('CSS File','*.wfd'),
    ('Mini SEED File','*.mseed'),
    ('All Files','*')
    ]
#   get default directory off of screen    
    defaultdir = DirNameVar.get() 
#   browse for data file using default directory   
    FileName=tkFileDialog.askopenfilename(parent=root_window,filetypes=myFormats,initialdir=defaultdir, \
        title = 'Select Damping File')
    print 'Damping File Selected: {}'.format(FileName)
    FileNameVar.set(string.replace(FileName, "/", "\\"))
    
def CalcDampingRatio (calcon_in,damping_file_in,damping_ratio_in):
#   make sure CalCon is loaded    
    LoadCalCon(calcon_in)
#   show CalCon structure contents before calculation for troubleshooting
    print '\n*** Start Calc Damping Ratio ***'
    print calcon_in
#   call dampingratio calc with root tkninter window & CalCon structure 
    damping = MDTcaldefs.dampingratio(root,calcon_in)
#   load calculated damping back into CalCon
    calcon_in['damping_ratio']= damping
#   Update screen with value
    damping_ratio_in.set(damping)
    
# function to call sac file preview if not empty
def ViewSample(file_name_in):
    FileName = file_name_in.get()
    if len(FileName)==0:
        tkMessageBox.showwarning("ERROR","No file selected")
    else:
        MDTcaldefs.file_preview(FileName)
        
def CallSigCal(root_window,calcon_in):
    selectedType=DataFormat.get()

    myFormats = [
    ('SAC files','*.sac'),
    ('CSS files','*.wfd'),
    ('Miniseed files','*.mseed,*.msd,*.ms'),
    ('All files','*.*')
    ]

    filez = tkFileDialog.askopenfilenames(parent=root_window,title='Use <shift> or <CTRL> to select the data files to include for processing:', \
            initialdir=calcon_in['target_dir'], \
            filetypes=myFormats)

# convert from unicode to str file list
    files = []
    for file in filez:
        files.append(string.replace(str(file), "/", "\\"))
  
#   make sure CalCon is loaded    
    LoadCalCon(calcon_in)
#   show CalCon structure contents before calculation for troubleshooting
    print '\n*** Start Signal Calibration ***'
    print calcon_in  
# call sigcal with list    
    MDTcaldefs.sigcal(calcon_in,files)
            

def main():
#   setup main data structure
    calcon = {'s_chname':'',\
          's_chsen':0.9455,\
          'l_chname':'LZR',\
          'l_chsen':0.9455,\
          'l_sen':1.00,\
          'l_calconst':0.579,\
          'target_dir':'c:\\Calibration\\',\
          'damping_ratio':0.707, \
          'damping_ratio_source':"", \
          'free_period':0.880,\
          'free_period_source':"", \
          'file_type':"sac",\
          'station':'MSU',\
          'network':'LM' }
    
# Setup GUI window
    global root
    root = Tk()
    root.title(string='MDT Seismic Sensor Calibration - v20160428b')
#root.geometry('200x210+350+70')


# Setup default data path selection prompt
    Label(root, text="DATA SET SELECTION").grid(row=1, column=0,padx=5,pady=5,sticky=W)
    Label(root, text="Default Directory:").grid(row=2,column=0,sticky=E)

    global DefaultDir
    DefaultDir = StringVar()
    DefaultDir.set(calcon['target_dir'])
    
    SetDefaultDirectory = Entry(root, bg='white',textvariable=DefaultDir).grid(row=2,column=1,columnspan=6,sticky=W+E)
    SetDirectoryBrowse = Button(root, text='  BROWSE  ',command=lambda: BrowseDefaultDir(root,calcon,DefaultDir)).grid(row=2,column=7,padx=5,sticky=W+E)

# Setup sensor info block labels
    Label(root, text="SENSOR INFORMATION").grid(row=4,column=0,padx=5,pady=5,sticky=W)

# Prompt for Station Location name and network
#    StationName = StringVar()
    global StationName
    StationName= StringVar()
    StationName.set(calcon['station'])
    
    Label(root, text="Station Location Name:").grid(row=5,column=0,sticky=E)
    StationEntry = Entry(root,bg='white',textvariable=StationName).grid(row=5,column=1,padx=3,sticky=W)
    
    global StationNetwork
    StationNetwork = StringVar()
    StationNetwork.set(calcon['network'])    
    Label(root, text="Network:").grid(row=5,column=2,padx=3,sticky=E)
    StationEntry = Entry(root,bg='white',textvariable=StationNetwork).grid(row=5,column=3,sticky=W)    
    
# Setup sensor info block labels
    Label(root, text="Sensor Channel Name:").grid(row=6,column=0,pady=2,sticky=E)
    Label(root, text="Sensitivity:").grid(row=6,column=2,sticky=E)
    Label(root, text="uV/cnt", fg='blue').grid(row=6,column=4,sticky=W)

    global SensorName
    SensorName = StringVar()
    SensorName.set(calcon['s_chname'])
    SensorChannelName   = Entry(root, bg='white',textvariable=SensorName).grid(row=6,column=1)
    global SensorSen
    SensorSen = StringVar()
    SensorSen.set(calcon['s_chsen'])
    SensorSensitivity   = Entry(root, bg='white',textvariable=SensorSen).grid(row=6,column=3)
    
    Label(root, text="Laser Channel Name:").grid(row=7,column=0,sticky=E)
    Label(root, text="Sensitivity:").grid(row=7,column=2,sticky=E)
    Label(root, text="uV/cnt", fg='blue').grid(row=7,column=4,sticky=W)

    global LaserName
    LaserName = StringVar()
    LaserName.set(calcon['l_chname'])
    LaserChannelName   = Entry(root, bg='white',textvariable=LaserName).grid(row=7,column=1)
    global LaserSen
    LaserSen = StringVar()
    LaserSen.set(calcon['l_chsen'])
    LaserSensitivity   = Entry(root, bg='white',textvariable=LaserSen).grid(row=7,column=3)

# Setup Laser settings block
    Label(root, text="  LASER POSITION SESNSOR").grid(row=8,column=0,pady=5,sticky=W)
    Label(root, text="Resolution:").grid(row=9,column=0,sticky=E)
    Label(root, text="Cal Constant:").grid(row=10,column=0,sticky=E)
    Label(root, text="V/mm", fg='blue').grid(row=9,column=2,sticky=W)
    Label(root, text="Pendulum Ratio", fg='blue').grid(row=10,column=2,sticky=W)

    global LaserReso
    LaserReso = StringVar()
    LaserReso.set(calcon['l_sen'])
    LaserResolution = Entry(root, bg='white',textvariable=LaserReso).grid(row=9,column=1)
    global LaserCal
    LaserCal = StringVar()
    LaserCal.set(calcon['l_calconst'])
    LaserCalConstant = Entry(root, bg='white',textvariable=LaserCal).grid(row=10,column=1)
    
#Setup Free Period file dialog and action buttons
    Label(root, text="  FREE PERIOD MEASUREMENT").grid(row=11, column=0,pady=5,sticky=W)
    Label(root, text="Data File:").grid(row=12,column=0,sticky=E)

    global FreeFile
    FreeFile = StringVar()
    FreeFile.set(calcon['free_period_source'])
    
    global FreeValue
    FreeValue = StringVar()
    FreeValue.set(calcon['free_period']) 

    FreePeriodFileEntry = Entry(root, bg='white',textvariable=FreeFile).grid(row=12, column=1, columnspan=6,sticky=W+E)
    FreePeriodBrowse = Button(root, text=' BROWSE ', command=lambda: BrowsePeriodFile(root,FreeFile,DefaultDir)).grid(row=12,column=7,padx=5,sticky=W+E)
    FreePeriodView   = Button(root, text='  VIEW  ', command=lambda: ViewSample(FreeFile)).grid(row=13,column=7,padx=5,sticky=W+E)

    FreePeriodCalc   = Button(root, text=' CALCULATE',command=lambda: CalcFreePeriod(calcon,FreeFile,FreeValue)).grid(row=13, column=1,pady=3)

    Label(root, text='Value:').grid(row=14,column=0,sticky=E)
    FreePeriod = Entry(root, bg = 'white', fg='red',textvariable=FreeValue).grid(row=14,column=1,sticky=W)
    Label(root, text='Hz',fg='blue').grid(row=14,column=2,sticky=W)

#Setup Dampening File Selection
    Label(root, text="  DAMPING RATIO (h)").grid(row=15, column=0,pady=5,sticky=W)
    Label(root, text="Data File:").grid(row=16,column=0,sticky=E)
    global DampingFile
    DampingFile = StringVar()
    DampingFile.set(calcon['damping_ratio_source'])
    global DampingValue
    DampingValue = StringVar()
    DampingValue.set(calcon['damping_ratio'])
    
    DampingFileEntry = Entry(root, bg='white',textvariable=DampingFile).grid(row=16, column=1, columnspan=6,sticky=W+E)
    DampingBrowse = Button(root, text=' BROWSE ', command=lambda: BrowseDampingFile(root,DampingFile,DefaultDir)).grid(row=16,column=7,padx=5,sticky=W+E)
    DampingView   = Button(root, text='  VIEW  ', command=lambda: ViewSample(DampingFile)).grid(row=17,column=7,padx=5,sticky=W+E)
    
    DampingCalc   = Button(root, text=' CALCULATE', command=lambda: CalcDampingRatio(calcon,DampingFile,DampingValue)).grid(row=17, column=1,pady=3)

    Label(root, text="Value:").grid(row=18,column=0,sticky=E)
    DampingRatio = Entry(root, bg='white', fg='red',textvariable=DampingValue).grid(row=18,column=1,sticky=W)


#Select Data Format
    Label(root, text="  SELECT DATA FORMAT").grid(row=19, column=0,pady=5,sticky=W)
    global DataFormat
    DataFormat = StringVar()
    DataFormat.set("SAC")
    Radiobutton(root, text="CSS", variable=DataFormat, value='CSS').grid(row=20,column=1,sticky=W)
    Radiobutton(root, text="SAC", variable=DataFormat, value='SAC').grid(row=21,column=1,sticky=W)
    Radiobutton(root, text="MSEED", variable=DataFormat, value='MSEED').grid(row=22,column=1,sticky=W)
    Label(root, text="  ").grid(row=23,column=0)

#SigCal Process Button Setup
    SigCalButton = Button(root,text=' PROCESS SIGCAL',command=lambda: CallSigCal(root,calcon)).grid(row=24,column=1,pady=7)
#SigCalButton.config(state=NORMAL)

#Exitbutton setup
    ExitButton = Button(root,text=' EXIT program',command=lambda: sys.exit()).grid(row=24,column=3)
#    ExitButton = Button(root,text=' EXIT program').grid(row=24,column=3)

# Preload calcontrol file if exists
#SigCalButton.config(state=DISABLED)

  #  xxx = tkFileDialog.askopenfilename(parent=root,initialdir=calcon['target_dir'])

    root.mainloop()

main()