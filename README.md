# Unity-Batch-Converter-for-Blender
This is a simple batch import/export to process multiple fbx files.  

usage: file > import > batch > choose fbx files

each selected .fbx file will be imported and re-exported with a "_processed"  appended to the filename.

if export FBX is selected, meshes and non armature objects will be deleted and the blender import filter will remove all gimbal flips.  

if export OBJ is selected, and combined is checked, meshes will be combined into a single mesh.
