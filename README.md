# Unity-Batch-Converter-for-Blender
This is a simple batch import/export to process multiple fbx files.  

usage: file > import > batch > choose fbx files

each selected .fbx file will be imported and re-exported with a "_processed"  appended to the filename.

if export FBX is selected, meshes and non armature objects will be deleted and the blender import filter will remove all gimbal flips.  Files will be exported next to their original files with a "_processed" suffix added. 

if export OBJ is selected, and combined is checked, meshes will be combined into a single mesh.

usage: file > import > batch > choose folder

This will duplicate the entire folder tree of the selected folder and place a copy next to the source folder withe a "_processed" suffix.  Every .fbx file in the tree will be imported and re-exported to have gimbal flips removed.
