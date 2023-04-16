from arcpy import GetParameter, GetParameterAsText, AddMessage, AddError, GetCount_management, SetProgressor, SetProgressorPosition, SetProgressorLabel
from arcpy.da import SearchCursor
from arcpy.mp import ArcGISProject
from arcpy import env
from arcpy.management import SelectLayerByLocation
from requests import get
from os import path


# declare exiting behavior. If set to false, ArcGIS will wait the script to terminate, instead terminating immediately
env.autoCancelling = False

def main():
    """
    This is the main function of the tool. Althouth it's not necessary, 
    the advantage of wrapping the main code into a function is that you can quickly terminate the script by using "return False"
    otherwise when using sys.exit() instead, sometimes  it leads to the error messages/stack traces in the tool output.
    """
    # getting variables from the tool GUI
    map_gdb_path = GetParameterAsText(0)
    map_url_field = GetParameterAsText(1)
    use_current_extent = GetParameter(2)
    search_layer = GetParameter(3)
    output_location = GetParameterAsText(4)

    
    # if "Use current extent" checkbox is set, get the current map extent as polygon. Works only if the map tab is active
    if use_current_extent:
        try:
            pro_project = ArcGISProject("CURRENT")
            search_layer = pro_project.activeView.camera.getExtent().polygon
        except:
            AddError("Can't get the current extent. Make sure the map window is active before running the tool")
            return False

    # checking if use current extent checkbox is checked or if the user selected something from "Or select layer" drop down.
    # why str(search_layer) - search layer input is not a string but a geoprocessing.value or geoprocessing.layer object, so need to cast it to str
    if any((use_current_extent, str(search_layer))):
        # selecting LiDAR/other tiles that intersect with the selected layer or extent polygon from the tile map layer
        selected_tiles = SelectLayerByLocation(map_gdb_path, "INTERSECT", search_layer, None, "NEW_SELECTION", "NOT_INVERT")
    else:
        AddError("Please select input layer to search for tiles, or check Use current extent checkbox")
        return False
        
    # if all checks passed, run the worker function
    download_files(selected_tiles, map_url_field, output_location)
    


def download_files(layer, url_field_name, output_folder):
    """
    This function loops through the selected tiles, retrieves URLs and downloads files.
    """
    # get the total number of the tiles selected to use in progress bar
    total_tiles_to_download = int(GetCount_management(layer)[0])
    # trying to download only if there were more than 0 tiles
    if total_tiles_to_download > 0:
        # initialize the progress bar
        SetProgressor("step", "Downloading files...", 0, total_tiles_to_download, 1)
        # loop through the tiles using SearchCursor
        with SearchCursor(layer, url_field_name) as cursor:
            for row_number, row in enumerate(cursor, 1):
                try:
                    url = row[0].split('"')[1]
                    filename = url.split('/')[-1]
                    
                    # Downloading file using requests library. Timeout(5 seconds in our case) parameter is important
                    # otherwise script will hang should the network connectivity error occur
                    # also we're downloading files in small chunks of 128(bytes?), so we don't have to fit all the file in memory
                    # code is borrowed here: https://docs.python-requests.org/en/master/user/quickstart/#raw-response-content
                    data = get(url, stream=True, timeout=5)
                    with open(path.join(output_folder, filename), 'wb') as file:
                        for chunk in data.iter_content(chunk_size=128):
                            file.write(chunk)
                    
                    # checking if user cancelled the tool. If we don't check this and trust ArcGIS to stop our script, it
                    # has troubles terminating the script.
                    if env.isCancelled:
                        AddMessage("Received cancel signal, exiting...")
                        break
                # handling (network) errors during downloading files
                except Exception as e:
                    AddError(f"Downloading of tile {row_number} has failed, error message: {e}")
                    continue
                # increment the progress bar
                SetProgressorPosition()
                # update the progress bar text to communicate number of files downloaded
                SetProgressorLabel(f"Downloading file {row_number} out of {total_tiles_to_download}")
    
    # Adding the error message if there was nothing to download
    else:
        AddError("There were no tiles to download in the area. Try selecting a different URL layer, search layer or extent")

# this is a common pattern to check if the script is not imported as a module in an another script, and run the main() function
if __name__ == "__main__":
    main()