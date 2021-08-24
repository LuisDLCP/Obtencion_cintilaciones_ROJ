#!/usr/bin/python3
import glob
import os 
from shutil import copy2

folder_common = "/home/cesar/Desktop/luisd/scripts/"
folder_src = folder_common + "Obtencion_cintilaciones/data_input/Data_ISMR/"
folder_dst = folder_common + "Obtencion_cintilaciones/data_input/Data_set/"
folder_dst2 = folder_common + "Obtencion_TEC/data_input/Data_set/"

# Move files 
sub_dir = [x[0] for x in os.walk(folder_src)]
for sf in sub_dir:
   files = glob.glob(sf + "/*ismr.gz")
   if len(files) > 0:
     for file_i in files:
        # Move files 
        file_name = file_i[len(sf)+1:]
        os.rename(file_i, folder_dst+file_name)
     print("All ismr files were moved succesfully!")

# Uncompress files
files = glob.glob(folder_dst + "*.ismr.gz")
if len(files)>0:
   for file_i in files:
      os.system("gunzip " + file_i)
   print("All ismr files were uncompressed!")

# Copy files from dest to dst2
files = glob.glob(folder_dst + "*.ismr")
if len(files)>0:
   for file_i in files:
      copy2(file_i, folder_dst2)
   print("All ismr files were copied to dest2!")		        

