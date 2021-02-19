# Unity-Batch-Converter-for-Blender
This is a simple batch import/export to process multiple fbx files to remove gimbal flips utilizing the blender import filter.  

usage: file > import > batch > choose fbx files

each selected .fbx file will be imported and re-exported with a "_processed"  appended to the filename.

if export FBX is selected, meshes and non armature objects will be deleted  

if export OBJ is selected, and combined is checked, meshes will be combined into a single mesh.
