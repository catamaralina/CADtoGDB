# CADtoGDB
Searches through folders for .dwg files and brings specific layers/features into a gdb.
**Detailed Steps for Each Function**
## **Setup and Configuration:**
1. Define Address and Set Environment:
   - Specify the folder address where the CAD files are located (address variable).
   - Set the environment workspace to the specified address
(arcpy.env.workspace).
2. Create or Link to Output Geodatabase (GDB):
   - Create a new file geodatabase (GDB) within the specified address if it doesn't already exist (arcpy.management.CreateFileGDB).
   - Link to the existing GDB if it's already created.
## **Main Processing:**
1. Loop Through School Folders:
   - Iterate through each school folder in the specified address using
arcpy.ListWorkspaces().
2. Check/Create Feature Dataset:
   - Check if a feature dataset for the school exists in the GDB (arcpy.Describe).
   - If the feature dataset doesn't exist, create it within the GDB (arcpy.CreateFeatureDataset_management).
3. Loop Through DWG Files:
   - Traverse through DWG files (*.dwg) in the school folder using arcpy.ListDatasets().
4. Extract Point and Polyline Layers:
   - Extract Point and Polyline layers from each DWG file using arcpy.Describe(dwg_path).children.
   - Iterate through the layers and identify Point and Polyline layers.
5. Rename and Import Layers to Feature Dataset:
   - Rename the extracted layers according to a standard convention.
   - Create a feature layer from the DWG layer (arcpy.management.MakeFeatureLayer).
   - Import the feature layer into the corresponding feature dataset within the GDB (arcpy.FeatureClassToFeatureClass_conversion).
6. Extract Specific Features (e.g., ROOMTAG):
   - Identify specific features (e.g., ROOMTAG) within Point layers.
   - Copy selected features to a new feature class within the feature dataset (arcpy.CreateFeatureclass_management and arcpy.da.InsertCursor).
