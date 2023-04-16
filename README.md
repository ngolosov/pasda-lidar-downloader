# pasda-lidar-downloader
PASDA LiDAR downloader for ArcGIS Pro: A script tool automates downloading LiDAR files and products from PASDA for easier access by end-users.

The Commonwealth of Pennsylvania, in collaboration with PSU, provides open access to GIS data for end-users. However, the current official method of downloading files from PASDA at a specific geographic location involves using a web map and manually clicking on links from map pop-ups, which can be inconvenient and impractical for downloading a large number of files.

To address this issue, I have developed a script tool to automate the downloading of LiDAR files and LiDAR-derived products, including LAS, DEMs, and XYZ files, hosted on PASDA. PASDA offers different LiDAR coverages and product types for different years. The script tool prompts the user to select the appropriate coverage layer and product type, and then downloads all the LiDAR or product tiles in the current extent or those intersecting with a selected layer.

### Test scenario

1)	Download and unpack the flies from GitHUB, note the folder location.
2)	Open ArcGIS Pro and create a new project, add Allegheny.shp from the sub-folder “test shp” to a new map, zoom to the layer
3)	Switch to ArcGIS Pro Catalog view, navigate to the folder where you’ve unpacked the files at step 1, double click \toolbox\PASDALidarDownloader.tbx toolbox and then PASDA LiDAR Downloader tool.
4)	Enter the following input parameters in the tool dialog:
LiDAR URLs layer: Path to the folder with the toolbox\lidar.gdb\ Allegheny_County_2015 feature class
Product type: select URL_las
Use current extent: uncheck
Or select layer: select Allegheny from the drop-down
Output dataset location: select any writable folder
5)	Click the Run button. The tool should download 4 zip files to the “Output dataset location”
Additional steps to test downloading files within the current extent:
6)	Switch to a Map tab from a Catalog tab. Zoom to the Allegheny layer.
7)	Remove the Allegheny layer from the map(optional).
