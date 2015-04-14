
#Initial_data_scrub_1

import os,arcpy, time
#Time reference for file naming
timestr = time.strftime("%m%d%Y_%H%M")

"""Project related info. Input applicable data here"""
#Location of data and location of output GDB and address locator
workspace = "C:/Users/KProsen/Desktop/MOD_Test/013015"
output_GDB = 'C:/Users/KProsen/Desktop/MOD_Test/MOD_Test.gdb'
address_locator_location = "T:/BSD/13_Documentation/US_Address_Locator/US_AddressLocator/Street_Addresses_US"

#4 Letter abbr
city = "MOD"
#Audit or Install- that will be written as AUD or INST
phase = "Aud"
#Data Analyst
data_analyst_initials= "KP"

proj = city + "_" + phase + "_" +data_analyst_initials + "_"

#set Workspace

"""Convert CSV to shapefile, shapefile to Layer, and add Layer to the top of the Data Frame with the same display name as the layer 
file in Windows Explorer. Input and output files are mutable below. """

#Note the difference here--> The TOC_output_lyr is the simple file name, and the output_lyr is that which is put into the savetolayer function
#Note: Each of these items must be unique for the file to run. Please update this every time you run.

output_shp_initial = "MOD_Audi_013015"
output_lyr_initial = proj + "output_lyr_initial_"+ timestr
output_shp_for_query = proj + "output_shp_query_"+ timestr
output_lyr_for_query = proj + "output_lyr_query_"+ timestr
arcpy.env.workspace = workspace

#We are assuming that the coordinate system is WGS 1984. If different, tell Kyle and he will fix
sp_ref = r"Coordinate Systems\Geographic Coordinate Systems\World\WGS 1984"


#Add csv to dataframe
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
newlayer = arcpy.mapping.Layer(workspace + "/" + output_shp_initial + ".shp")
arcpy.mapping.AddLayer(df, newlayer, "BOTTOM")


arcpy.FeatureClassToGeodatabase_conversion(output_shp_initial, output_GDB)
arcpy.SaveToLayerFile_management(output_shp_initial, output_lyr_initial, "RELATIVE")

#This adds the new Layer to the Data Frame. If you want the new layer to display at the bottom of the Data Frame, Replace the 'TOP' with 'BOTTOM.'
layer_initial_to_dataframe = arcpy.mapping.Layer(workspace+ "/"+output_lyr_initial+".lyr")
layer_initial_to_dataframe.name = output_lyr_initial
arcpy.mapping.AddLayer(df, layer_initial_to_dataframe,"TOP")


"""Now, for some reason, you need to do a FeatureClasstoFeatureClass export so that you can SelectLayerByAttributes. It has something to do with OIDs, and ArcMap
liking those in the shapefiles."""
arcpy.FeatureClassToFeatureClass_conversion(output_shp_initial,output_GDB, output_shp_for_query)
arcpy.SaveToLayerFile_management(output_shp_for_query, output_lyr_for_query, "RELATIVE")

#Fixing the field names to reflect desired names
arcpy.AlterField_management(output_GDB + "/" + output_shp_for_query, "GPS_Time", phase + "Time")
arcpy.AlterField_management(output_GDB + "/" + output_shp_for_query, "GPS_Date", phase + "Date")

#Calculating UID
# Add field, calculate new field based on string concatenation of filename and Point_ID
UID = phase+"UID"
UID_expression = '[Datafile]&"_"&[Point_ID]'
arcpy.AddField_management(output_shp_for_query,UID, 'TEXT', "", "", 30)
arcpy.CalculateField_management(output_shp_for_query,UID,UID_expression)
#Add Fields for Notes/Comments/Address/Street/City/Zip
arcpy.AddField_management(output_shp_for_query,"Notes", 'TEXT', "", "", 30)
arcpy.AddField_management(output_shp_for_query,"Address", 'TEXT', "", "", 40)
arcpy.AddField_management(output_shp_for_query,"Street", 'TEXT', "", "", 30)
arcpy.AddField_management(output_shp_for_query,"City", 'TEXT', "", "", 15)
arcpy.AddField_management(output_shp_for_query,"Zipcode", 'TEXT', "", "", 10)

#Begin reverse Geocode
Rev_gcd_filename = city+"_Audit"+"_RevGcd"+timestr
arcpy.ReverseGeocode_geocoding(output_shp_for_query,address_locator_location,Rev_gcd_filename, "Address", "100 feet")

#END OF CODE FOR NOW

#Make sure that if it is in a GDB that you use square brackets for the field name
arcpy.SelectLayerByAttribute_management(output_lyr_for_query, "ADD_TO_SELECTION", [AuditUID] IN (SELECT[AUDITUID] FROM [Audit2DataDupeCheck_Features] GROUP BY [AUDITUID] HAVING COUNT(*)>1)
arcpy.SelectLayerByAttribute_management(output_lyr_for_query, "ADD_TO_SELECTION", ' [latitude] = 0 OR NULL OR [longitude] = 0 OR NULL')


#To verify everything up to this point has worked
print "Layer add completed"

#Starting to Scrub the site for redundancies
#This code needs to be added later on---> arcpy.MakeFeatureLayer_management ("C:/data/data.mdb/states", "stateslyr")
"""arcpy.SelectLayerByAttribute_management(TOC_output_lyr, "ADD_TO_SELECTION", ' [latitude] = 0 OR NULL OR [longitude] = 0 OR NULL')
if int(arcpy.GetCount_management(TOC_output_lyr).GetOutput(0)) > 0:
	arcpy.DeleteRows_management(TOC_output_lyr)"""

"""
[AuditUID] IN (SELECT[AUDITUID] FROM [Audit2DataDupeCheck_Features] GROUP BY [AUDITUID] HAVING COUNT(*)>1)
"""
