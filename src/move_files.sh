#!/bin/bash
FOLDER_SRC="/media/cesar/Septentrio03/ISMR/"
FOLDER_DST="/home/cesar/Desktop/luisd/scripts/Obtencion_cintilaciones/data_input/Data_ISMR/"
FOLDERS=`diff -q ${FOLDER_SRC} ${FOLDER_DST} | grep Only | grep ${FOLDER_SRC} | awk '{print $4}'`
if [[ -z $FOLDERS ]]
then 
  echo "There isn't any new folder yet!"
else
  echo "The new files are:"
  echo $FOLDERS
  for FOLDER in $FOLDERS
  do
    cp -r ${FOLDER_SRC}$FOLDER ${FOLDER_DST}
  done
  echo "All files were copied sucesfully!"
fi
