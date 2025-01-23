Documentation for HTS Data Processing Application
1. Overview
   
    This application is designed to process High-Throughput Screening (HTS) data using a web-based interface built with Dash, a Python framework for building analytical web applications. The application allows users to upload Excel files, define regions of interest, assign control regions, and perform calculations based on user-defined equations. The results can be saved back to Excel files.

2. Functional Description
   
    1) File Upload: Users can upload multiple Excel files and a template file (JSON format) to define the processing parameters.
    2) Region Selection: Users can specify start and end regions within the Excel files to focus on specific data ranges.
    3) Control Region Assignment: Users can define positive, negative, blank, and none control regions within the selected data range.
    4) Calculation: Users can input a custom equation to calculate results based on the control regions and the selected data.
    5) Result Display: The application displays the selected region, role assignments, and calculated results in tabular format.
    6) Save Functionality: Users can save the processing template and the processed results back to Excel files.

3. Architecture of this project(for python scripts)
   
    /project-root
   
    │
   
    ├── app.py                      # Dash application
   
    ├── requirements.txt            # Python dependencies
   
    ├── README.md                   # Project documentation   
   
    └── main.py                     # For terminal via python

4. Installation
   
    1) Set up a conda environment from requirements.txt
        conda env create -n HTSdata -f requirements.txt # Install dependencies
    2) Run the project
        conda activate HTSdata
        cd project-root/
        python main.py # Run from terminal
    3) Process in browser

5. HTSData processing pipeline
    
    1) Uploading Files:
        (1) Upload Template File: Drag and drop or select a JSON template file that contains predefined processing parameters.
        (2) Upload Data Files: Drag and drop or select one or more Excel files containing the data to be processed.
    2) Defining Regions and Controls
        (1) Start and End Region: Enter the start and end regions (e.g., B2 to D10) to define the data range.
        (2) Control Regions: Define the positive, negative, blank, and none control regions using cell references or row/column ranges (e.g., A3-A21, column 1-5, row 2-4).
    3) Performing Calculations
        (1) Equation Input: Enter a custom equation using placeholders for control regions (e.g., (neg-sample)/(neg-pos)*100% or (1-sample/blank)*100%).
        (2) Calculate: Click the "Calculate" button to perform the calculation and display the results.
    4) Saving Results
        (1) Save Template: Save the current processing parameters as a JSON template file.
        (2) Save Results: Save the processed data to Excel files with _processed appended to the original filenames.

6. Control regions and abbreviations in the equation
    
    pos: positive control regions (averaged value in equation)
   
    neg: negative control regions(averaged value in equation)
   
    blank: blank control regions (averaged value in equation, often for DMSO or vehicle)
   
    none: irrelevant regions
   
    sample: cells in data range (including pos, neg, and blank without none)

8. Example Template File
   
    {
        "start_region": "B2",
        "end_region": "AV10",
        "positive_ctrl_cells": "A3-A21",
        "negative_ctrl_cells": "column 1-5",
        "blank_ctrl_cells": "row 2-4",
        "none_cells": "B5,row 7",
        "equation": "(neg-sample)/(neg-pos)*100%"
    }
