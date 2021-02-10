bl_info = {
    'name': 'ProcessFbxFolder',
    'author': 'Bay Raitt',
    'version': (0, 1),
    'blender': (2, 91, 0),
    "description": "Import all FBX Folder and Export",
    'category': 'Import-Export',
    'location': 'File > Import',
    'wiki_url': ''}

import bpy
from bpy_extras.io_utils import ExportHelper
from bpy_extras.io_utils import ImportHelper
import os.path
from bpy.props import *
import subprocess
import os
import warnings
from bpy.props import (
    StringProperty,
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    CollectionProperty,
)


# ImportHelper mixin class uses this
filename_ext = ".fbx"

filter_glob: StringProperty(
    default="*.fbx",
    options={'HIDDEN'},
)

class U_OT_process_fbx_folder(bpy.types.Operator, ImportHelper):
    """Process Multiple FBX Files in a folder"""
    bl_idname = 'import_scene.process_fbx_folder'
    bl_label = 'Choose Mocap .fbx files'
    bl_options = {'PRESET', 'UNDO'}
    bl_description = "process all fbx files in a folder"

    filepath = bpy.props.StringProperty(name="file path", description="Process folder")
    files: CollectionProperty(type=bpy.types.PropertyGroup)



    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        row = layout.row(align=True)
        box: layout.box()
        row: box.row()
        row.prop(self, "trim_end_bones")
        layout.prop(self, "keep_anim_scale")
        layout.prop(self, "keep_anim_loc")

    def execute(self, context):

        trim_end_bones = False
        keep_anim_scale = False
        keep_anim_loc = False
        scene = bpy.context.scene
        objects = bpy.context.selected_objects
        if objects is not None:
            for obj in objects:
                starting_mode = bpy.context.object.mode
                if "OBJECT" not in starting_mode:
                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    bpy.ops.object.select_all(action='DESELECT')

        # get the folder
        folder = (os.path.dirname(self.filepath))
        # iterate through the selected files
        for i in self.files:
            for c in bpy.data.collections:
                for o in c.objects:
                    bpy.data.objects.remove(o)

            # generate full path to file
            path_to_file = (os.path.join(folder, i.name))

            # call obj operator and assign ui values
            bpy.ops.import_scene.fbx(filepath=path_to_file,
                                     filter_glob='*.fbx',
                                     ui_tab='MAIN',
                                     use_manual_orientation=False,
                                     global_scale=1.0,
                                     bake_space_transform=False,
                                     use_custom_normals=True,
                                     use_image_search=True,
                                     use_alpha_decals=False,
                                     decal_offset=0.0,
                                     use_anim=True,
                                     anim_offset=1.0,
                                     use_subsurf=False,
                                     use_custom_props=True,
                                     use_custom_props_enum_as_string=True,
                                     ignore_leaf_bones=trim_end_bones,
                                     force_connect_children=False,
                                     automatic_bone_orientation=False,
                                     primary_bone_axis='Y',
                                     secondary_bone_axis='X',
                                     use_prepost_rot=True,
                                     axis_forward='-Z',
                                     axis_up='Y')

            # do stuff to the mesh here
            imported_objects = bpy.context.selected_objects
            for ob in imported_objects:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob

                # Check if object is a Mesh
                # if ob.type == 'MESH':

                # Delete everything but armature
                if ob.type != 'ARMATURE':
                    ad = ob.animation_data
                    if ad:
                        if ad.action:
                            action_name = ad.action.name
                            bpy.data.actions[action_name].user_clear()
                    if ob.type != 'MESH':
                        bpy.ops.object.delete(use_global=False)
                else:
                    imported_armature = ob

            for block in bpy.data.actions:
                if block.users == 0:
                    bpy.data.actions.remove(block)

            bpy.ops.object.select_all(action='DESELECT')
            imported_armature.select_set(state=True)
            bpy.context.view_layer.objects.active = imported_armature

            bpy.ops.object.mode_set(mode='POSE')

            # clear off scale and position keyframes
            root_bones = [b for b in imported_armature.data.bones if not b.parent]
            # if not keep_anim_scale or not keep_anim_loc:
                # bpy.ops.object.mode_set(mode='POSE')
                # bpy.ops.object.select_all(action='DESELECT')
                # bpy.ops.pose.select_all(action='DESELECT')

                # imported_armature.select = True
                # for pb in imported_armature.pose.bones:
            for pb in root_bones:
                bpy.ops.pose.select_all(action='DESELECT')
                # if pb not in root_bones:
                imported_armature.data.bones[pb.name].select = True
                if not keep_anim_scale:
                    bpy.ops.pose.scale_clear()
                if not keep_anim_loc:
                    bpy.ops.pose.loc_clear()

            bpy.ops.object.mode_set(mode='OBJECT')

            # check if actions is empty
            if bpy.data.actions:
                action_list = [action.frame_range for action in bpy.data.actions]
                keys = (sorted(set([item for sublist in action_list for item in sublist])))
                scene.frame_start = keys[0]
                scene.frame_end = keys[-1]
            else:
                print("no actions")

            # print("=======DEBUG: " + scene.name)
            # raise KeyboardInterrupt()

            # export the armature
            basefilename = os.path.splitext(i.name)[0]
            tmp_path_to_file = (os.path.join(folder, basefilename))
            path_to_export_file = (tmp_path_to_file + "_processed.fbx")
            bpy.ops.export_scene.fbx(filepath=path_to_export_file, use_selection=True)

            # delete the mesh
            bpy.ops.object.delete(use_global=False)
        cmd = ("explorer " + folder)
        subprocess.Popen(cmd)
        return {'FINISHED'}


class U_MT_BatchSubMenu(bpy.types.Menu):
    bl_idname = 'U_MT_BatchSubMenu'
    bl_label = 'Batch'

    def draw(self, context):
        layout = self.layout
        self.layout.operator(U_OT_process_fbx_folder.bl_idname)


def menu_import_draw(self, context):
    layout = self.layout
    layout.menu(U_MT_BatchSubMenu.bl_idname)


classes = (
    U_MT_BatchSubMenu,
    U_OT_process_fbx_folder,
)


def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_import_draw)


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    bpy.types.TOPBAR_MT_file_import.remove(menu_import_draw)


if __name__ != "__main__":
    bpy.types.TOPBAR_MT_file_import.remove(menu_import_draw)

if __name__ == "__main__":
    try:
        # by running unregister here we can run this script
        # in blenders text editor
        # the first time we run this script inside blender
        # we get an error that removing the changes fails
        unregister()
    except:
        pass
    register()
