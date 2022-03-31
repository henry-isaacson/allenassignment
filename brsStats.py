import sys
import statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import csv


#method for reading in given files
def read_files(signalFile, annotationFile, structureFile):
    signals = np.load(signalFile)['arr_0'] # 3D numpy array of signals volume
    annotations = np.load(annotationFile)['arr_0'] # 3D numpy array of corresponding ID's volume
    structures = pd.read_csv(structureFile, index_col=0) # Pandas dataframe
    return signals, annotations, structures
    
#method for visualizing data as two graphs - signals and annotations
def visualization(data):
    # 3D data visualization - taken from numpy website
    x = data[:,1]
    y = data[:,2]
    z = data[:,3]
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x,y,z)
    plt.show()

# sorts signals into a dictionary based on tree level
def data_sort(signals, annotations, structures):
    global signalsList
    global annotationsList

    signalsList, annotationsList = list_init(signals, annotations) #1D list conversion
    sortedDataDict = {} #dictionary (key is level in tree, value is unordered brain ID's)
    rawData = structures['structure_id_path'].tolist() #stores structure ID strings in list
    rawIDs = structures['id'].tolist() #stores corresponding region ID strings in list
    index = 0
    for treePath in rawData: #for each structure ID string
        treeLevel = str(treePath.count('/') - 2) #splice structure ID path for "/"
        signal = signal_calculator(rawIDs[index]) #calculate signal for structure
        if treeLevel in sortedDataDict.keys():
            currentValue = sortedDataDict.get(treeLevel) #grabs current list of signals given a certain level
            sortedDataDict[treeLevel] = currentValue + [signal] #append signal value to dictionary if key is present
        else:
            sortedDataDict[treeLevel] = [signal] #create new key value pair if key is not present
        index += 1
    return sortedDataDict

# gets summed signal per region ID
def signal_calculator(signalID):
    global signalsList
    global annotationsList

    signalSum = 0 #total signal
    tempSignals = [] #signals to be kept
    tempAnnotations = [] #annotations to be kept
    print(len(annotationsList))
    for annotationIndex in range(len(annotationsList)): #iterates through annotations list
        if annotationsList[annotationIndex] == signalID: #finds instance of signal ID in annotations volume
            signalSum = float(signalSum + signalsList[annotationIndex]) #adds corresponding signal from signals volume
            annotationsList[annotationIndex] = 0 #turns annotation to 0 as it has been "counted"
        else: #adds unused data for next function call
            tempSignals.append(signalsList[annotationIndex])  
            tempAnnotations.append(annotationsList[annotationIndex])
    signalsList = tempSignals
    annotationsList = tempAnnotations
    return signalSum

#converts 3D arrays to 1D lists for simplicity in shortening
def list_init(signals, annotations):
    signalsList = []
    annotationsList = []
    for col in range(len(annotations)):
        for row in range(len(annotations[col])):
            for depth in range(len(annotations[col][row])):
                if annotations[col][row][depth] != 0:
                    signalsList.append(signals[col][row][depth])
                    annotationsList.append(annotations[col][row][depth])
    return signalsList, annotationsList

# calculates mean max min and sum at each level
def statistics_calculator(sortedDataDict):
    level = 0
    statsArray = []
    while str(level) in sortedDataDict.keys(): #iterates through all levels in sequential order
        regionMean = statistics.mean(sortedDataDict[str(level)])
        regionMax = max(sortedDataDict[str(level)])
        regionMin = min(sortedDataDict[str(level)])
        regionSum = sum(sortedDataDict[str(level)])
        #places data into array as a formatted string
        statsArray.append("Level " + str(level) + ": Mean = " + str(regionMean) + ", Max = " + str(regionMax) + ", Min = " + str(regionMin) + ", Sum = " + str(regionSum))
        level += 1
    print("done with statistics calculator")
    return statsArray

# writes calculated statistics to csv file
def statistics_writer(statsArray, outgoingFile):
    with open(outgoingFile, 'w') as f: #opens csv file
        writer = csv.writer(f)
        for data in statsArray: #writes each element of statsArray as single line
            writer.writerow(data)


# Main method
if __name__ == "__main__":

    # Ensures all arguments were specified
    if len(sys.argv) < 5:
        print("Usage: [signal.npz] [annotation.npz] [structures.csv] [outgoing.csv]")
        print("For visualization: add -v as a 5th argument")
        sys.exit()
    signalFile = sys.argv[1]
    annotationFile = sys.argv[2]
    structureFile = sys.argv[3]
    outgoingFile = sys.argv[4]

    # reads in all files and sets them in arrays
    signals, annotations, structures = read_files(signalFile, annotationFile, structureFile)
    
    # visualizes signals and annotations if requested
    if len(sys.argv) == 6:
        if sys.argv[5] != "-v":
            print("Error: For Visualization use -v as 5th argument.")
        else:
            visualization(signals)
            visualization(annotations)

    #sorts data by level on tree into dictionary
    sortedDataDict = data_sort(signals, annotations, structures)
    #calculates statistics based on level
    statsArray = statistics_calculator(sortedDataDict)
    #writes statistics to outgoing file
    statistics_writer(statsArray, outgoingFile)
    

    
