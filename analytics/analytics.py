# Swarm Analytics - Taiming YuenJames
# Processes data files to compute and visualize makespan and traversal statistics for drone navigation strategies

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import scipy.stats

# === USER-CONFIGURABLE CONSTANTS ===

# Directory paths
ROOT_FOLDER = 'F:/files/school/wwu/research/robotics/simulationSwarm/cluttered-navigation/plinko-drones/analytics/sampleOutput/root'
MAKESPAN_DIR = 'makespan'
SPATIAL_DIR = 'spatial'
STRATEGIES = ['centralized', 'decentralized']
FOLDER_TYPES = ['bothFixed', 'angleFixed', 'countFixed']

# Plotting options
PLOT_COLORS = [
    "#6060ff", # [0]: data points in scatter plots, box color in boxplots
    "#ff2020", # [1]: best-fit line in scatter plots, median line in boxplots
    "#000000", # [2]: whiskers and caps in boxplots
    "#ffff60"  # [3]: outlier (flier) points in boxplots
]
FIGURE_SIZE = (7, 6)
BOX_WIDTH = 0.5
FONT_SIZE = 12

# Best-fit line degree (1=linear, 2=quadratic, 3=cubic, etc.)
BEST_FIT_DEGREE = 1
BEST_FIT_LABEL = {1: 'Linear Best Fit', 2: 'Quadratic Best Fit', 3: 'Cubic Best Fit'}

# Margin of error/confidence interval
CONFIDENCE_LEVEL = 0.95

# Title templates for all graphs (customize as needed)
TITLE_BARCHART_MAKESPAN_STRATEGY = 'Makespan by Strategy (Angle & Count Fixed)'
TITLE_BARCHART_TRAVERSAL_STRATEGY = 'Average Traversal Time by Strategy (Angle & Count Fixed)'
TITLE_BARCHART_EMD_STRATEGY = 'EMD by Strategy (Angle & Count Fixed)'
TITLE_MAKESPAN_DRONECOUNT_CENTRALIZED = 'Makespan vs. Drone Count for Centralized Strategy'
TITLE_TRAVERSAL_DRONECOUNT_CENTRALIZED = 'Average Traversal Time vs. Drone Count for Centralized Strategy'
TITLE_EMD_DRONECOUNT_CENTRALIZED = 'EMD vs. Drone Count for Centralized Strategy'
TITLE_MAKESPAN_DRONECOUNT_DECENTRALIZED = 'Makespan vs. Drone Count for Decentralized Strategy'
TITLE_TRAVERSAL_DRONECOUNT_DECENTRALIZED = 'Average Traversal Time vs. Drone Count for Decentralized Strategy'
TITLE_EMD_DRONECOUNT_DECENTRALIZED = 'EMD vs. Drone Count for Decentralized Strategy'
TITLE_MAKESPAN_ANGLE_CENTRALIZED = 'Makespan vs. Angle for Centralized Strategy'
TITLE_TRAVERSAL_ANGLE_CENTRALIZED = 'Average Traversal Time vs. Angle for Centralized Strategy'
TITLE_EMD_ANGLE_CENTRALIZED = 'EMD vs. Angle for Centralized Strategy'
TITLE_MAKESPAN_ANGLE_DECENTRALIZED = 'Makespan vs. Angle for Decentralized Strategy'
TITLE_TRAVERSAL_ANGLE_DECENTRALIZED = 'Average Traversal Time vs. Angle for Decentralized Strategy'
TITLE_EMD_ANGLE_DECENTRALIZED = 'EMD vs. Angle for Decentralized Strategy'

# Other settings
SHOW_MEANS = True
SHOW_LEGEND = True

# --- Utility Functions ---

def readFirstLineValue(filePath, xAxis):
    """Extract x value (droneCount or angle) from the first line of a file."""
    try:
        with open(filePath) as file:
            vals = file.readline().strip().split(',')
            if len(vals) < 3:
                return None
            return int(vals[1]) if xAxis == 'droneCount' else float(vals[2])
    except Exception:
        return None
    
def parseSpatialFile(filePath):
    """Parse a spatial log file into a dict: timeStamp -> list of (x, y) positions."""
    positionsByTime = {}
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 7 or vals[5].strip() == '<null>' or vals[6].strip() == '<null>':
                continue
            try:
                timeStamp = int(vals[4])
                x, y = float(vals[5]), float(vals[6])
                positionsByTime.setdefault(timeStamp, []).append((x, y))
            except ValueError:
                continue
    return positionsByTime

def computeWasserstein(positionsA, positionsB):
    """Compute Wasserstein EMD between two 2D point sets."""
    if not positionsA.size or not positionsB.size:
        return None
    costMatrix = cdist(positionsA, positionsB)
    rowInd, colInd = linear_sum_assignment(costMatrix)
    return costMatrix[rowInd, colInd].mean()

# --- Data Extraction Functions ---

def extractMakespan(filePath):
    """Return makespan (last exit - first exit) for valid lines in file, or None if invalid."""
    minExit, maxExit = float('inf'), float('-inf')
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                exitTime = float(vals[5])
                minExit = min(minExit, exitTime)
                maxExit = max(maxExit, exitTime)
            except ValueError:
                continue
    return maxExit - minExit if minExit != float('inf') and maxExit != float('-inf') else None

def extractTraversal(filePath):
    """Return average traversal time (exit-entry) for valid lines in file, or None if invalid."""
    traversalTimes = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                entryTime, exitTime = float(vals[4]), float(vals[5])
                traversal = exitTime - entryTime
                if traversal >= 0:
                    traversalTimes.append(traversal)
            except ValueError:
                continue
    return np.mean(traversalTimes) if traversalTimes else None

def extractEmd(filePath, referenceArray=None):
    """Return average EMD over all time steps in a spatial file."""
    positionsByTime = parseSpatialFile(filePath)
    if not positionsByTime:
        return None
    if referenceArray is None:
        # Use the first non-empty time step as reference
        for t in sorted(positionsByTime):
            arr = np.array(positionsByTime[t])
            if arr.size > 0:
                referenceArray = arr
                break
        else:
            return None
    emdVals = []
    for t in sorted(positionsByTime):
        positionsArray = np.array(positionsByTime[t])
        emd = computeWasserstein(positionsArray, referenceArray)
        if emd is not None:
            emdVals.append(emd)
    return np.mean(emdVals) if emdVals else None

def folderStats(folderPath, xAxis, statFunc):
    """Return list of (x, stat) for all .txt files in folder using statFunc."""
    data = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue
        filePath = os.path.join(folderPath, fileName)
        xValue = readFirstLineValue(filePath, xAxis)
        if xValue is None:
            continue
        stat = statFunc(filePath)
        if stat is not None:
            data.append((xValue, stat))
    return data

# --- Plotting Functions ---

def printDescriptiveStats(title, dataDict):
    """Print descriptive statistics for each group in a pretty way with a title."""
    # Print a formatted table of stats for each group (e.g., strategy)
    print(f"\n=== {title} ===")
    for group, values in dataDict.items():
        arr = np.array(values)
        if arr.size == 0:
            print(f"{group}: No data.")
            continue
        # Compute and print common descriptive statistics
        stats = {
            'Count': len(arr),
            'Mean': np.mean(arr),
            'Std': np.std(arr, ddof=1) if len(arr) > 1 else 0.0,
            'Min': np.min(arr),
            '25%': np.percentile(arr, 25),
            'Median': np.median(arr),
            '75%': np.percentile(arr, 75),
            'Max': np.max(arr)
        }
        print(f"{group}:")
        for k, v in stats.items():
            print(f"  {k:>6}: {v:>10.3f}" if isinstance(v, float) else f"  {k:>6}: {v}")

def plotScatter(data, title, xLabel, yLabel, xIntTicks=False):
    """Reusable scatter plot with best-fit line and descriptive stats."""
    # Early exit if no data
    if not data:
        print(f"No data for {title}"); return
    xValues, yValues = zip(*data)
    # Print stats for y-values (dependent variable)
    printDescriptiveStats(title, {yLabel: yValues})
    plt.figure(figsize=FIGURE_SIZE)
    plt.scatter(xValues, yValues, label='Data Points', color=PLOT_COLORS[0])  # Data points (same as box color)
    # Add best-fit line if more than one point
    if len(xValues) > 1:
        coeffs = np.polyfit(xValues, yValues, BEST_FIT_DEGREE)
        poly = np.poly1d(coeffs)
        xFit = np.linspace(min(xValues), max(xValues), 100)
        plt.plot(xFit, poly(xFit), color=PLOT_COLORS[1], label=BEST_FIT_LABEL.get(BEST_FIT_DEGREE, 'Best Fit'))  # Best-fit line (same as median)
    plt.title(title, fontsize=FONT_SIZE)
    plt.xlabel(xLabel, fontsize=FONT_SIZE)
    plt.ylabel(yLabel, fontsize=FONT_SIZE)
    # Set x-axis ticks for integer-based axes
    if xIntTicks:
        xMin, xMax = int(min(xValues)), int(max(xValues))
        if xLabel.startswith('Drone Count'):
            plt.xticks(np.arange(0, xMax+1, 5))
        else:
            step = 5 if xMax - xMin > 6 else 1
            plt.xticks(np.arange(xMin, xMax+1, step))
    if SHOW_LEGEND:
        plt.legend()
    plt.show()

def plotBox(samplesDict, title, yLabel):
    """Reusable boxplot with descriptive stats for each group (e.g., strategy)."""
    printDescriptiveStats(title, samplesDict)
    plt.figure(figsize=FIGURE_SIZE)
    plt.boxplot(
        [samplesDict['centralized'], samplesDict['decentralized']],
        tick_labels=['Centralized', 'Decentralized'],
        patch_artist=True,
        showmeans=SHOW_MEANS,
        meanprops={"marker":"o","markerfacecolor":"white","markeredgecolor":"black"},
        widths=BOX_WIDTH,
        boxprops=dict(color=PLOT_COLORS[0], facecolor=PLOT_COLORS[0]), # Box color (same as scatter data points)
        medianprops=dict(color=PLOT_COLORS[1]), # Median line (same as best-fit line)
        whiskerprops=dict(color=PLOT_COLORS[2]), # Whiskers
        capprops=dict(color=PLOT_COLORS[2]), # Caps
        flierprops=dict(markerfacecolor=PLOT_COLORS[3], marker='o') # Outliers
    )
    plt.title(title, fontsize=FONT_SIZE)
    plt.ylabel(yLabel, fontsize=FONT_SIZE)
    plt.xlabel('Strategy', fontsize=FONT_SIZE)
    plt.show()

# --- Analysis Functions ---

def analyzeFixed(folderType, rootFolder, strategies, xAxis, statFuncs, plotFuncs, plotTitles, xLabel, yLabels, xIntTicks=False):
    """Generalized analysis for bothFixed, angleFixed, and countFixed folders.
    For each strategy, computes and plots stats for makespan, traversal, and EMD.
    """
    for strategy in strategies:
        # Build paths for makespan and spatial data for this strategy and folder type
        pathMakespan = os.path.join(rootFolder, 'Makespan', strategy, folderType)
        pathSpatial = os.path.join(rootFolder, 'Spatial', strategy, folderType)
        # For makespan and traversal, plot for each stat function
        if os.path.isdir(pathMakespan):
            for statFunc, plotFunc, plotTitle, yLabel in zip(statFuncs, plotFuncs, plotTitles, yLabels):
                data = folderStats(pathMakespan, xAxis, statFunc)
                plotFunc(data, plotTitle.format(strategy), xLabel, yLabel, xIntTicks)
        # For EMD, plot EMD vs. x-axis
        if os.path.isdir(pathSpatial):
            emdData = folderStats(pathSpatial, xAxis, extractEmd)
            plotScatter(emdData, plotTitles[-1].format(strategy), xLabel, yLabels[-1], xIntTicks)

def extractMakespanSamples(filePath):
    """Return a list of exit times for all drones in the file (for margin of error calculation)."""
    exitTimes = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                exitTime = float(vals[5])
                exitTimes.append(exitTime)
            except ValueError:
                continue
    return exitTimes

def extractTraversalSamples(filePath):
    """Return a list of traversal times (exit-entry) for all drones in the file (for margin of error calculation)."""
    traversalTimes = []
    with open(filePath) as file:
        for line in file:
            vals = line.strip().split(',')
            if len(vals) < 6 or vals[5].strip() == '<null>':
                continue
            try:
                entryTime, exitTime = float(vals[4]), float(vals[5])
                traversal = exitTime - entryTime
                if traversal >= 0:
                    traversalTimes.append(traversal)
            except ValueError:
                continue
    return traversalTimes

def extractEmdSamples(filePath, referenceArray=None):
    """Return a list of EMD values for all time steps in a spatial file (for margin of error calculation)."""
    positionsByTime = parseSpatialFile(filePath)
    if not positionsByTime:
        return []
    if referenceArray is None:
        for t in sorted(positionsByTime):
            arr = np.array(positionsByTime[t])
            if arr.size > 0:
                referenceArray = arr
                break
        else:
            return []
    emdVals = []
    for t in sorted(positionsByTime):
        positionsArray = np.array(positionsByTime[t])
        emd = computeWasserstein(positionsArray, referenceArray)
        if emd is not None:
            emdVals.append(emd)
    return emdVals

def getStrategySamples(folderPath, sampleFunc):
    """Aggregate all samples for a strategy from all .txt files in a folder."""
    samples = []
    for fileName in os.listdir(folderPath):
        if not fileName.endswith('.txt'):
            continue
        filePath = os.path.join(folderPath, fileName)
        samples.extend(sampleFunc(filePath))
    return samples

def marginOfError(samples, confidence=CONFIDENCE_LEVEL):
    """Calculate the margin of error for a list of samples at the given confidence level (user-configurable)."""
    n = len(samples)
    if n < 2:
        return 0.0
    mean = np.mean(samples)
    sem = scipy.stats.sem(samples)
    h = sem * scipy.stats.t.ppf((1 + confidence) / 2, n - 1)
    return h

def main():
    """Main function to run all analyses and plots for the experiment data."""
    if not os.path.isdir(ROOT_FOLDER):
        print(f"Warning: root folder '{ROOT_FOLDER}' does not exist. Please update the path."); return
    # Both Fixed
    makespanSamplesDict, traversalSamplesDict, emdSamplesDict = {}, {}, {}
    for strategy in STRATEGIES:
        pathMakespan = os.path.join(ROOT_FOLDER, MAKESPAN_DIR, strategy, FOLDER_TYPES[0])
        pathSpatial = os.path.join(ROOT_FOLDER, SPATIAL_DIR, strategy, FOLDER_TYPES[0])
        if os.path.isdir(pathMakespan):
            makespanSamples = getStrategySamples(pathMakespan, extractMakespanSamples)
            traversalSamples = getStrategySamples(pathMakespan, extractTraversalSamples)
            makespanSamplesDict[strategy] = makespanSamples
            traversalSamplesDict[strategy] = traversalSamples
        if os.path.isdir(pathSpatial):
            emdSamples = getStrategySamples(pathSpatial, extractEmdSamples)
            emdSamplesDict[strategy] = emdSamples
    plotBox(makespanSamplesDict, TITLE_BARCHART_MAKESPAN_STRATEGY, 'Makespan (ms)')
    plotBox(traversalSamplesDict, TITLE_BARCHART_TRAVERSAL_STRATEGY, 'Average Traversal Time (ms)')
    plotBox(emdSamplesDict, TITLE_BARCHART_EMD_STRATEGY, 'Wasserstein EMD')
    # Angle Fixed
    analyzeFixed(
        FOLDER_TYPES[1], ROOT_FOLDER, STRATEGIES, 'droneCount',
        [extractMakespan, extractTraversal],
        [plotScatter, plotScatter, plotScatter],
        [
            TITLE_MAKESPAN_ANGLE_CENTRALIZED,
            TITLE_TRAVERSAL_ANGLE_CENTRALIZED,
            TITLE_EMD_ANGLE_CENTRALIZED
        ],
        'Drone Count',
        ['Makespan (ms)', 'Average Traversal Time (ms)', 'Wasserstein EMD'],
        xIntTicks=True
    )
    # Count Fixed
    analyzeFixed(
        FOLDER_TYPES[2], ROOT_FOLDER, STRATEGIES, 'angle',
        [extractMakespan, extractTraversal],
        [plotScatter, plotScatter, plotScatter],
        [
            TITLE_MAKESPAN_ANGLE_DECENTRALIZED,
            TITLE_TRAVERSAL_ANGLE_DECENTRALIZED,
            TITLE_EMD_ANGLE_DECENTRALIZED
        ],
        'Angle (Degrees)',
        ['Makespan (ms)', 'Average Traversal Time (ms)', 'Wasserstein EMD'],
        xIntTicks=True
    )

if __name__ == "__main__":
    main()
