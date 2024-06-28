# TCDSB AUTOMATION

# Geodatabase: gdb

# SCRIPT PROPERTIES
# Can create gdb if one isn't already created 
#     (edit the REVIEW SECTION as needed)
# Takes folders that are datasets (edit address to folder location)
# Creates a feature dataset in gdb
# For each folder looks at each dwg file
# For each dwg file selects Point, and Polyline layers,
#     renames to a standard convention and
#     translates to related feature dataset in gdb
#     creates a feature class and selects a Point substet called ROOMTAG

import arcpy
import os

# ADDRESS
# the address should be changed to where the files for cad to ArcGIS Pro are located.
# Working with the format that in the address folder there is:
# -- Folders for each school: School Name_#
# -- In each school folder is GEOREFERENCED .dwg files
address = r"C:\Users\tj\Documents\ElementarySchools"

# SETTING UP THE ENVIRONMENT
arcpy.env.workspace = address

# LIST WORKSPACES IN THE CHOSEN WORKSPACE
# This lists all the files in the address folder.
workspaces = arcpy.ListWorkspaces()
print(workspaces)

# set the coordinate system for the project/code.
coordsys = arcpy.SpatialReference(2958)
arcpy.env.outputCoordinateSystem = coordsys
    


# ---   ---   --- REVIEW SECTION ---   ---   ---
# CREATE GDB IN ADDRESS FOLDER
# If there is no gdb created, rename the gdb in the below gdbname variable and make sure the next 2 lines are uncommented
gdbname = "FINAL_TEST"
arcpy.management.CreateFileGDB(address, gdbname)

# IF ALREADY CREATED, LINK TO GDB 
# if there is an already created gdb, replace the address below. 
# gdb = r"C:\Users\tj\Documents\GEOM68_Collab\TEST\TCDSB_TEST.gdb"

# IF GDB NOT ALREADY CREATED, leave the above gdb commented and make sure the below is uncommented:
gdb = address + '\\' + gdbname + '.gdb'

# --- END REVIEW SECTION ---



# SEARCH FOR CURRENT FEATURE DATASETS IN GDB
feature_datasets = []
for root, dirs, files in arcpy.da.Walk(gdb, datatype="FeatureDataset"):
    if os.path.splitext(root.lower())[-1] in (".gdb", ".sde"):
        for dirname in dirs:
            feature_datasets.append(os.path.join(dirname.lower()))

# PRINT OUT FEATURE DATASETS CURRENTLY IN THE GDB
# print("FEATURE DATASETS:", feature_datasets)


# WORK THROUGH EACH POTENTIAL WORKSPACE
# This will loop through every school folder in the address folder specified.
for work in workspaces:
    # WORK IS THE ADDRESS TO THE SCHOOL FOLDER (EG. ...\\BISHOP ALLEN ACADEMY_549)
    workDesc = arcpy.Describe(work)

    # if the workspaceType isn't working, check to make sure that all files (.dwg) are in a folder. 
    # .csv files are ok
    workType = workDesc.workspaceType
    foldername = os.path.basename(work)

    # CREATING A SCHOOL FOLDER NAME TO WORK WITH IN PRO FOR DATASETS
    removechar = ['.', ' ', '(', ')', '&', '-', "'"]
    for char in removechar:
        foldername = foldername.replace(char, '')

    # FILTER OUT WORKSPACES THAT AREN'T FOLDERS:
    if workType != 'FileSystem':
        print('The workspace, {0}'.format(foldername), 'is a {0} and no further action will be taken because it is not a folder.'.format(workType), '\n')
    
    # IF THE WORKSPACE IS A FOLDER:
    else:
        # Seeing where we're working with
        print("Workspace:", work)

        # PRINT OUT SECTIONS FOR EACH FOLDER FOR EASY VISUALIZATION
        print('\n')
        print('-----     -----     -----     -----     {}     -----     -----     -----     -----'.format(foldername))
    
        # CREATE/CHECK FOR FEATURE DATASET IN THE GDB FOR EACH SCHOOL 

        # IF THE DATASET ALREADY EXISTS, WE SKIP
        if foldername.lower() in feature_datasets:
            print("Feature dataset {} already exists".format(foldername), '\n')
        # IF IT DOESN'T EXIST, IT IS CREATED
        else:
            arcpy.CreateFeatureDataset_management(gdb, foldername, coordsys)
            print("Created feature dataset {}".format(foldername), '\n')

        # CREATE THE PATH NAME TO THE DATASET
        fds_path = gdb + '\\' + foldername
        print("fds path: ", fds_path)

        # SET WORK ENVIRONMENT FOR EACH SCHOOL FOLDER   
        arcpy.env.workspace = work

        # LISTS THE FILES THAT ARE IN THE SCHOOL FOLDER
        # print('The folder {} has the following .dwg files:'.format(os.path.basename(work)))
        

        # LIST DATASETS THAT END IN DWG
        dwg_datasets = arcpy.ListDatasets("*.dwg")

        for d in dwg_datasets:
            dpath = os.path.join(work, d)
            nameconv = d[:9]  # Extract the first 9 characters of the DWG filename for naming conventions
            print("DWG File:", dpath)

            # Describe the DWG dataset
            ddesc = arcpy.Describe(dpath)
            dtype = ddesc.datasetType


#--------------------------------------------------------------------------------------------------------
# This is where we start the process for extracting CAD file Data.
            # GET SUB LAYERS OF THE DWG DATASET 
            # BRINGING DWG INTO CAD, IT GENERALLY HAS 5 LAYERS:    
            # ANNOTATION, POINT, POLYLINE, POLYGON, MULTIPATCH
            # FOR THIS PROJECT POINT AND POLYLINE ARE USED

            dlayers = ddesc.children
            for layer in dlayers:

                print('\t','Layer Name:{}'.format(layer.name))

                if layer.name =='Polyline':

                    # CREATE OUTPUT LAYER NAME WITH NAMING CONVENTIONS
                    # IN FEATURE DATASET: LAYERNAME_#_NthFl
                    #                     Point_555_1stFl
                    output_layer_name = "{}_{}".format(layer.name, nameconv)

                    # FEATURE LAYER PATH IN GDB
                    fl_path = os.path.join (fds_path, output_layer_name)

                    # CHECK IF FEATURE LAYER ALREADY EXISTS
                    if arcpy.Exists(fl_path):
                        print('\t',"This layer, {} already exists in {}.".format(output_layer_name, foldername))

                    else:
                        try:
                            # MAKE FEATURE LAYER IF IT DOESN'T ALREADY EXIST
                            # INPUT LAYER, OUTPUT LAYER
                            arcpy.management.MakeFeatureLayer(dpath + "\\" + layer.name, output_layer_name)
                            print('\t',"Feature layer created:", output_layer_name)

                            # COPY FEATURE LAYER TO THE GDB
                            arcpy.FeatureClassToFeatureClass_conversion(output_layer_name, fds_path, output_layer_name)
                            print('\t',"Feature layer copied to geodatabase:", output_layer_name)
                        except arcpy.ExecuteError as e:
                            print('\t',"Error:", e)

                elif layer.name =='Point':
                    # SAME AS POLYLINE TO CREATE POINT LAYER
                    # CREATE OUTPUT LAYER NAME WITH NAMING CONVENTIONS
                    # IN FEATURE DATASET: LAYERNAME_#_NthFl
                    #                     Point_555_1stFl
                    output_layer_name = "{}_{}".format(layer.name, nameconv)

                    # FEATURE LAYER PATH IN GDB
                    fl_path = os.path.join (fds_path, output_layer_name)

                    # CHECK IF FEATURE LAYER ALREADY EXISTS
                    if arcpy.Exists(fl_path):
                        print('\t',"This layer, {} already exists.".format(output_layer_name))
                    else:
                        try:
                            # MAKE FEATURE LAYER IF IT DOESN'T ALREADY EXIST
                            # INPUT LAYER, OUTPUT LAYER
                            arcpy.management.MakeFeatureLayer( dpath + "\\" + layer.name, output_layer_name)
                            print('\t',"Feature layer created:", output_layer_name)

                            # COPY FEATURE LAYER TO THE GDB
                            arcpy.FeatureClassToFeatureClass_conversion(output_layer_name, fds_path, output_layer_name)
                            print('\t',"Feature layer copied to geodatabase:", output_layer_name)

                        except arcpy.ExecuteError as e:
                            print('\t',"Error:", e)

                    # ----------------------------------------------------------------------------------
                    # NOW CREATING NEW LAYER FOR SPECIFIC POINTS
                    # IN THIS PROJECT, ROOMTAG WAS MOST IMPORTANT POINT FEATURE
                    ROOMTAG_layer_name = "ROOMTAG_{}".format(nameconv) 
                    ROOMTAG_path = fds_path + '\\' + ROOMTAG_layer_name
                    # # Want to search for specific subclasses in the newly created feature layer
                    # fields = ['Layer']
                    if arcpy.Exists(ROOMTAG_path):
                        print('\t',"This layer, {} already exists.".format(ROOMTAG_layer_name))
                    else:
                        # CREATE THE ROOMTAG FEATURE CLASS
                        arcpy.CreateFeatureclass_management(fds_path, ROOMTAG_layer_name, 'POINT', output_layer_name, spatial_reference=coordsys)

                        # CREATE CURSOR TO ITERATE OVER FEATURES
                        with arcpy.da.SearchCursor(output_layer_name, '*', spatial_reference=coordsys) as cursor:

                            for row in cursor:
                                layer_value = row[4]  # Extract the value of the 'Layer' field
                                if layer_value == 'ROOMTAG':                             
                                    # INSERT SELECTED FEATURES INTO CREATED FC
                                    with arcpy.da.InsertCursor(ROOMTAG_path, '*') as insert_cursor:
                                        insert_cursor.insertRow(row)
                        print('\t',"Selected features copied to new feature class:", ROOMTAG_layer_name)


print("File Database transfer of school folder files to ArcGIS Pro has been completed.")









