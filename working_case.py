#-*- coding: utf-8 -*-
import flickrapi
import sys
import codecs
from osgeo import ogr



try:
    infile_shape = sys.argv[1]	
    outfile_csv = sys.argv[2]
    
except:
	print "USAGE of this script: Shapefile_of_Bounding_Box.shp Output.csv"
	sys.exit()
drv = ogr.GetDriverByName('ESRI Shapefile')
ds_in = drv.Open(infile_shape)
lyr_in = ds_in.GetLayer(0)


#My data application:
api_key = "8f8fa0028f7f7dc6d7b1d21fc173c98b"
secret_api_key = "61f983a5fdc9a43e"

#create an API object:
flickr = flickrapi.FlickrAPI(api_key, secret_api_key)

#Search photos from a BBox:
#Documentation at https://www.flickr.com/services/api/flickr.photos.search.html
photo_list = flickr.photos.search(api_key=api_key, tags="flood,Flut,Überschwemmung, Flood, Hochwasser, floodplain", min_taken_date='2007-01-01 00:00:01', bbox="8, 48, 8.72, 49.421", accuracy=16,
                                  content_type=7, has_geo=1, extras="description, license, date_upload, date_taken, owner_name, icon_server, original_format, last_update, tags, geo, machine_tags, o_dims, views, media, path_alias, url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o",
                                  per_page=500,format='parsed-json')


pages = int(photo_list["photos"]["pages"])
#print (pages)


outFile = codecs.open("flood_heidelberg.csv", "w", "utf-8")
header = "fid;uid;tags;date;lat;lon;url\n"
outFile.write(header)


cnt_source = 0
cnt_final = 0

for i in range(1, pages+1):
    for photo in photo_list["photos"]["photo"]:
        cnt_source +=1
        fid = int(photo["id"])
        uid = photo["owner"]
        lat = photo["latitude"]
        lon = photo["longitude"]
        floatlat = float(lat)
        floatlon = float(lon)
        
        if "tags" in photo:
            tags = photo["tags"]
        else:
            tags = ""

        if "datetaken" in photo:
            date = photo["datetaken"]
        else:
            date = ""
            
        if "url_o" in photo:
            url = photo["url_o"]
        elif "url_o" not in photo and "url_c" in photo:
            url = photo["url_c"]
        else:
            url = ""
        
        point = ogr.Geometry(ogr.wkbPoint)

        point.SetPoint_2D(0, floatlon, floatlat)
        lyr_in.SetSpatialFilter(point)
        
          
            
        for feat_in in lyr_in:
            cnt_final +=1            
            add = "%s;%s;%s;%s;%s;%s;%s\n" % (fid, uid, tags, date, lat, lon, url)
            outFile.write(add)
            
# points in source vs points in polygon of shapefile
# if same= try bigger bbox in line 30
print "Points in Source:",cnt_source
print "Points in Polygon:", cnt_final
outFile.close()
