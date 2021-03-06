#!/usr/bin/python
"""

Author: Ricardo O. S. Soares, PhD - 2014
        Faculty of Pharmaceutical Sciences at Ribeirao Preto
        Biological Chemistry and Physics Group
        University of Sao Paulo - Brazil
        contact: rsoares@fcfrp.usp.br

If you use this script for your research, please acknowledge it.
Please, feel free to report any bugs or send any suggestions!

For script usage please use the available help: python readHBmap.py -h 

A few tips:
    
    - Choose the threshold (-t) in accordance to your needs. If you want a general idea of the significant HBs, values
      between 10 to 20% are suitable. However if you want to isolate only the most frequent interactions, you may 
      increase this value up to 99%; 
    - Choose the timestep (-dt) accordingly, values around 1 to 10% of the total number of frames may be a good start.
    - Tho read the xvg file, use xmgrace with the -nxy flag.
"""

from __future__ import division
from argparse import RawTextHelpFormatter
import argparse
import linecache
import re

### Defining the user interface

# Delimiting user input (threshold) to 0-99%:
def thresholdInput(value):
    evaluate = float(value)
    if evaluate < 0 or evaluate > 100:
        raise argparse.ArgumentTypeError("%s is an invalid value, please choose a value between 0 and 99" % value)
    return evaluate
# Delimiting user input (dt) to > 0:  
def dtInput(value):
    evaluate = float(value)
    if evaluate <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid value, please choose a positive value equal or smaller than the total" \
        "number of frames in the HB map" % value)
    return evaluate  
  
parser = argparse.ArgumentParser(description='\tPython script (recommended version 2.7.+) to extract the hydrogen bond existences\n'\
'\tfrom HB Map file (.xpm) generated by h_bond from GROMACS. readHBmap.py outputs a\n'\
'\tlist with donor-acceptor pairs with occupancy above the user-input threshold.\n'\
'\tThe script also outputs a file which describes the occupancy over time, and although\n'\
'\tit is by default formatted to be read by Grace (xmgrace), it can be plotted with\n'
'\tother spreadsheet softwares. If you use this script for your research, please acknowledge it.\n' \
'\tA few tips:\n\t\t- Choose the threshold (-t) in accordance to your needs. If you want a general idea\n'\
'\t\t  of the significant HBs, values between 10 to 20% are suitable. However if you want\n'\
'\t\t  to isolate only the most frequent interactions, you may increase this value up to 99%;\n'
'\t\t- Choose the timestep (-dt) accordingly, values around 1 to 10% of the total number\n'\
'\t\t  of frames may be a good start.\n \t\t- To plot the xvg file, use xmgrace with the -nxy flag.'\
'\tPlease note that depending to \n\t\t  the chosen threshold, a great amount of data may be plotted.'\
'\n\n\t-- Author: Ricardo O. S. Soares, PhD --',formatter_class=RawTextHelpFormatter)

parser.add_argument('-hbm', dest='hbmap', default='hbmap.xpm',
                   help='Input, hydrogen bond map matrix file (default: hbmap.xpm)')
parser.add_argument('-hbn', dest='index', default='hbond.ndx',
                   help='Input, hydrogen bond index file (default: hbond.ndx)')
parser.add_argument('-f', dest='gro', default='traj.gro',
                   help='Input, protein structure in .gro format (default: traj.gro)')
parser.add_argument('-o', dest='plot', default='occupancy.xvg',
                   help='Output, occupancy of each pair over time (default: occupancy.xvg)')
parser.add_argument('-op', dest='pairs', default='pairs.dat',
                   help='Output, list of HB residue pairs and its occupancies (default: pairs.dat)')
parser.add_argument('-t', dest='threshold', default=10,
                   help='Option, Process and output only interacting pairs that have occupancy equal or larger than this value, '\
                   'must be between 0 and 99%% (default: 10%%)', type=thresholdInput)
parser.add_argument('-dt', dest='timestep', default=100,
                   help='Option, partial occupancies at each defined timestep (frames) along the trajectory (default: 100 frames)', type=dtInput)


args = parser.parse_args()
inputHbmap=str(args.hbmap)
inputIndex=str(args.index)
inputGro=str(args.gro)
outputPlot=str(args.plot)
outputPairs=str(args.pairs)
threshold=float(args.threshold)
dt=int(args.timestep)

class output():
    def openFiles(self,inputHbmap,inputIndex,outputPairs):
            hbmap= open(inputHbmap, "r") 
            index= open(inputIndex, "r")
            fileOccupancies= open(outputPairs, "w")  
            fileOccupancyTime= open(outputPlot, "w")
            return hbmap, index, fileOccupancies, fileOccupancyTime       

    def closeFiles(self,hbmap, fileOccupancies,fileOccupancyTime):
            hbmap.close()
            fileOccupancies.close()
            fileOccupancyTime.close()
            
    def writeHeader01(self,numberHbonds,threshold,inputHbmap,numberFrames):
            self.pairsFile="--> Results for readHBmap.py (Author: Ricardo O. S Soares)\n--> Found %i valid hydrogen bond" \
            " pairs with occupancy of more than %3.1f%%\n--> The hydrogen bond map (%s) has %i frames\n\nPair ID  |        "\
            "donor-acceptor        |   Atom Number   | Occupancy (%%) | Pair ID  \n\n" % (numberHbonds,threshold,inputHbmap,numberFrames)
            fileOccupancies.write(self.pairsFile)
    
    def writeHeader02(self,occupanciesThreshold,pairNames,threshold):
            fileOccupancyTime.write("@    title \"HB occupancy over time\" \n@    subtitle \"Above the threshold of %4.2f %%\" "\
            "\n@    xaxis  label \"Frame\" \n@    yaxis  label \"Occupancy (%%)\" \n@TYPE xy \n@page size 992, 612 \n" % threshold)
            fileOccupancyTime.write("@ legend on\n@ legend box on\n@ legend loctype view\n@ legend 1.25, 0.8\n@ legend length 2\n")
            for i in range(0,len(occupanciesThreshold)):
                fileOccupancyTime.write("@ s%i legend \"%s\"\n" % (i,pairNames[i]))
            fileOccupancyTime.write("\n")
            
    def writeDat(self,numberHbonds,occupancies,threshold,donorResNumber,donorResName,hydrogenNumber,donorGroupName, \
                 acceptorResNumber,acceptorResName,acceptorGroupNumber,acceptorGroupName,fileOccupancies):
            pairNames,occupanciesThreshold=([] for i in range(2))            
            n=0            
            for i in range(0, numberHbonds):                
                if occupancies[i] >= float(threshold):
                        n=n+1
                        donorResNumber[i]=donorResNumber[i].replace(" ","")
                        acceptorResNumber[i]=acceptorResNumber[i].replace(" ","")
                        acceptorGroupName[i]=acceptorGroupName[i].replace(" ","")
                        donorGroupName[i]=donorGroupName[i].replace(" ","")
                        occupanciesThreshold.append(i)
                        names=str(donorResNumber[i]+donorResName[i]+"-"+acceptorResNumber[i]+acceptorResName[i])
                        pairNames.append(names)  
                        FormattedLine = '{:>5} {:>9}{:>0}({:^3}) - {:<3}{:<0}({:^3})   {:>8} - {:<8} {:>8.1f} {:>10}'.format \
                        (n,donorResNumber[i],donorResName[i],donorGroupName[i],acceptorResNumber[i],acceptorResName[i],acceptorGroupName[i],\
                        hydrogenNumber[i],acceptorGroupNumber[i],occupancies[i],n)
                        fileOccupancies.write(FormattedLine)
                        fileOccupancies.write("\n")    
                else:
                    pass
            print "Successfully wrote file ""\"",outputPairs,"\""    
            return pairNames, occupanciesThreshold 
            
    def writeXvg(self,occupanciesThreshold,counterInterval,counterRemainder,remainder,fileOccupancyTime, dt,outputPairs, outputPlot):
            # Write values to 'occupancy_vs_time.xvg', converting the 1D array to write the values
            # Array= [1,2,3,4,5,6,7,8,9]
            # Print:
            # 1 2 3
            # 4 5 6 
            # 7 8 9
            # Rule to read array
            # limit= number of blocks that the array will be divided (same as number of lines that will be written to file)
            
            limit=int(len(counterInterval)/len(occupanciesThreshold))
            if remainder != 0:
                limit=limit+1
            else:
                pass
            m=len(occupanciesThreshold)
            k=0
            r=0
            init=0
                
            for i in range(0,limit): 
                FormattedLine = '{:>5} '.format(init)
                fileOccupancyTime.write(FormattedLine)        
                for j in range(k,m):
                    if remainder !=0 and m==len(counterInterval)+len(occupanciesThreshold):        
                        output=counterRemainder[r]/remainder*100 
                        FormattedLine = '{:>5.2f} '.format(output)
                        fileOccupancyTime.write(FormattedLine)
                        r=r+1
                    else:
                        output=counterInterval[j]/dt*100
                        FormattedLine = '{:>5.2f} '.format(output)
                        fileOccupancyTime.write(FormattedLine)
                fileOccupancyTime.write("\n")
                k=m
                m=m+len(occupanciesThreshold)
                init=init+dt
               
            print "Successfully wrote file ""\"",outputPlot,"\""    

    def noPairs(self,threshold):
            print "No hydrogen bonds found above the threshold of",threshold, "%%"

    def dtWarning(self,dt,numberFrames):
            print "Warning: the chosen timestep(",dt,") is larger than the total number of frames (",numberFrames,"),"\
            " the xvg output will be empty"
    
    def writeWarning(self, fileOccupancyTime,dt,numberFrames,inputHbmap):
            FormattedLine = 'No output to write, chosen timestep (dt= {:>1.2f}) should be positive and smaller than the"\
            " total number of frames from {:>s}, i.e. 0 < dt <={:>} '.format(dt,inputHbmap,numberFrames)            
            fileOccupancyTime.write(FormattedLine)
            
class readFiles():
    def hbmap(self,hbmap,inputHbmap):
            lookup01 = 'char'  
            lookup02 = 'y-axis'
            startingLine=[]
            framesLine = []
            numberFrames=int
            numberHbonds=int
            for num, line in enumerate(hbmap, 1):
                if lookup01 in line:
                    framesLine=num
                if lookup02 in line:
                    startingLine=num
            framesLine=framesLine+1 # ...the line wich contains the number of frames and the number of hydrogen bonds                        
            startingLine=startingLine+1 # ...the starting line from the block where the occupancies are plotted
            # Read variables from line 'framesLine' and find the number of frames and total number of hydrogen bonds
            line = linecache.getline(inputHbmap, framesLine)
            framesLine = map(int, re.findall('\d+', line))
            # ...number of frames and H. bonds
            numberFrames=framesLine[0] 
            numberHbonds=framesLine[1]
            return startingLine,framesLine,numberFrames,numberHbonds
 
    def index(self,index,numberHbonds):
            lookup01 = 'hbonds'
            indexLine = int
            pairs= []
            for num, line in enumerate(index, 1):
                if lookup01 in line:
                    indexLine=num
            # Retrieve the content of the selected index file  (backwards)
            for i in range(indexLine+numberHbonds,indexLine,-1):
                line = linecache.getline(inputIndex, i)
                pairs.append(re.findall(r'\d+',line))
            return pairs

    def countHbmap(self,startingLine,numberHbonds,inputHbmap):
            counter = []
            for i in range(startingLine, startingLine+numberHbonds):
                line = linecache.getline(inputHbmap, i)
                counter.append(line.count('o'))
            return counter
            
    def gro(self,pairs,inputGro):
            occupancies, donorResNumber, donorResName, hydrogenNumber, donorGroupName, acceptorResNumber, acceptorResName,\
            acceptorGroupNumber, acceptorGroupName, occupanciesThreshold = ([] for i in range(10))
            # Assign the three variables of pairs[] to separated variables,
            for i in range(0, numberHbonds):
                lineDonorGroupNumber,lineHydrogenNumber,lineAcceptorGroupNumber=pairs[i]
                # Add +2 to compensate the 2 header lines in the .gro file
                lineDonorGroupNumber=int(lineDonorGroupNumber)+2
                lineHydrogenNumber=int(lineHydrogenNumber)+2
                lineAcceptorGroupNumber=int(lineAcceptorGroupNumber)+2
                # Extract the donor/acceptor residues/atoms and number/names from the .gro file
                # donorResName and hydrogenNumber belong to the same residue, so they have the same residue number 'donorResNumber'
                line_donor = linecache.getline(inputGro, lineHydrogenNumber)
                line_acceptor = linecache.getline(inputGro, lineAcceptorGroupNumber)
                donorResNumber.append(line_donor[1:5])
                donorResName.append(line_donor[5:8])
                donorGroupName.append(line_donor[12:15])
                hydrogenNumber.append(line_donor[15:20])
                acceptorResNumber.append(line_acceptor[1:5])
                acceptorResName.append(line_acceptor[5:8])
                acceptorGroupName.append(line_acceptor[12:15])
                acceptorGroupNumber.append(line_acceptor[15:20])
                # Calculate occupancies in percentage
                occupancies.append(counter[i]/numberFrames*100)
                
            return occupancies, donorResNumber, donorResName, hydrogenNumber, donorGroupName, acceptorResNumber, acceptorResName,\
            acceptorGroupNumber, acceptorGroupName          
             
class process():
    def countInterval(self,numberFrames,dt,occupanciesThreshold,startingLine,inputHbmap):
    
        counterInterval = []
        counterRemainder = []
        init=0
        # If the total number of frames is not divisible by the user inputed time-step, the last percentages will be wrong,
        #so we need to find the remainder
        remainder=numberFrames%dt
        numberFrames=numberFrames-remainder
    
        for init in range(0,numberFrames,dt):
            for i in range(0,len(occupanciesThreshold)):      
                j=startingLine+occupanciesThreshold[i]
                line = linecache.getline(inputHbmap, j)
                counterInterval.append(line.count('o',init,init+dt))
        
        
        if remainder != 0:
                for i in range(0,len(occupanciesThreshold)):      
                    j=startingLine+occupanciesThreshold[i]
                    line = linecache.getline(inputHbmap, j)
                    counterRemainder.append(line.count('o',init,init+remainder))
                    
        return  remainder,counterInterval,counterRemainder              


########################################################################################
# Create file with occupancies list
########################################################################################

# Open Hydrogen Bond Map generated by g_hbond (GROMACS)
hbmap, index, fileOccupancies, fileOccupancyTime=output().openFiles(inputHbmap,inputIndex,outputPairs)

# Isolate the map from the xpm file:
startingLine,framesLine,numberFrames,numberHbonds=readFiles().hbmap(hbmap,inputHbmap)

# Count the occupancies from each line of xpm file map (Starting from startingLine)
counter=readFiles().countHbmap(startingLine,numberHbonds,inputHbmap)

# Identify the pairs using the index file
pairs=readFiles().index(index,numberHbonds)

# Writing the header of the occupancies list file
output().writeHeader01(numberHbonds,threshold,inputHbmap,numberFrames)

# Use the index file to read pair names in .gro file and write to occupancies list
occupancies,donorResNumber,donorResName,hydrogenNumber,donorGroupName,acceptorResNumber,acceptorResName, \
acceptorGroupNumber,acceptorGroupName=readFiles().gro(pairs,inputGro)

# Write data to the file
pairNames,occupanciesThreshold=output().writeDat(numberHbonds, occupancies, threshold, donorResNumber, \
donorResName, hydrogenNumber, donorGroupName, acceptorResNumber, acceptorResName, acceptorGroupNumber, \
acceptorGroupName, fileOccupancies)
    
########################################################################################
# Create file with occupancies occupancies vs time
########################################################################################    

# At each user-defined interval, count the occupancies in the hydrogen bond map and write to an array
remainder,counterInterval,counterRemainder=process().countInterval(numberFrames,dt,occupanciesThreshold,\
startingLine,inputHbmap)

# Check if there is hydrogen bonds above the threshold
if len(occupanciesThreshold) > 0:
    if dt< numberFrames:    
        # Write header and legend info of the occupancies vs time
        output().writeHeader02(occupanciesThreshold,pairNames,threshold)
        # Write xvg file
        output().writeXvg(occupanciesThreshold,counterInterval,counterRemainder,remainder,fileOccupancyTime,\
        dt,outputPairs, outputPlot)
    else:
        output().writeWarning(fileOccupancyTime,dt,numberFrames,inputHbmap)
        output().dtWarning(dt,numberFrames)
else:
    output().noPairs(threshold)

# Close files and end script
output().closeFiles(hbmap, fileOccupancies, fileOccupancyTime)