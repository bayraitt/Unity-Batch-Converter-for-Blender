bl_info = {
    'name': 'ProcessFbxFolder',
    'author': 'Bay Raitt',
    'version': (0, 6.6),
    'blender': (2, 92, 0),
    "description": "Batch process selected fbx files",
    'category': 'Import-Export',
    'location': 'File > Import > Batch >',
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


class U_OT_process_fbx_folder(bpy.types.Operator, ImportHelper):
    """Process Multiple FBX Files in a folder"""
    bl_idname = 'import_scene.process_fbx_folder'
    bl_label = 'Choose .fbx files'
    bl_options = {'PRESET', 'UNDO'}
    bl_description = "Batch process selected fbx files"
    filepath = bpy.props.StringProperty(name="file path", description="Process folder")

    filename_ext = ".fbx"
    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
    )
    files: CollectionProperty(type=bpy.types.PropertyGroup)

    trim_end_bones: bpy.props.BoolProperty(name="Insert End Bones",
                                           description="trim end bones for maya compatibility",
                                           default=False)

    keep_anim_scale: bpy.props.BoolProperty(name="Keep Scale Animation",
                                            description="remove all scale animation channels",
                                            default=False)

    keep_anim_loc: bpy.props.BoolProperty(name="Keep Position Animation",
                                          description="remove all location animation channels",
                                          default=False)

    export_fbx: bpy.props.BoolProperty(name="Export as FBX",
                                       description="export as fbx files",
                                       default=True)

    export_obj: bpy.props.BoolProperty(name="Export as OBJ",
                                       description="export as obj files",
                                       default=False)

    export_scale: bpy.props.FloatProperty(name="Export Scale",
                                       description="Scale export units by",
                                       default=100.0)

    combine_meshes: bpy.props.BoolProperty(name="Combine Meshes",
                                       description="combine meshes into one object",
                                       default=True)


    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout

        row = layout.row(align=True)
        box: layout.box()
        row: box.row()
        # row.prop(self, "trim_end_bones")
        # layout.prop(self, "keep_anim_scale")
        # layout.prop(self, "keep_anim_loc")

        layout.prop(self, "export_obj")
        if self.export_obj:
            layout.prop(self, "export_scale")
            layout.prop(self, "combine_meshes")

        layout.prop(self, "export_fbx")

        if self.export_fbx:
            layout.prop(self, "trim_end_bones")
            layout.prop(self, "keep_anim_scale")
            layout.prop(self, "keep_anim_loc")

    def execute(self, context):
        scene = bpy.context.scene

        export_obj = self.export_obj

        export_scale = self.export_scale
        combine_meshes = self.combine_meshes

        export_fbx = self.export_fbx
        trim_end_bones = self.trim_end_bones
        keep_anim_scale = self.keep_anim_scale
        keep_anim_loc = self.keep_anim_loc

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
            imported_meshes = []
            for ob in imported_objects:
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(state=True)
                bpy.context.view_layer.objects.active = ob

                # Check if object is a Mesh
                # if ob.type == 'MESH':

                if export_fbx:
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

                if export_obj:
                    imported_meshes.append(ob)

            if export_fbx:
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
                # bpy.ops.export_scene.fbx(filepath=path_to_export_file, use_selection=True)
                # bpy.ops.export_scene.fbx(filepath=path_to_export_file,
                #                          check_existing=True,
                #                          filter_glob='*.fbx',
                #                          use_selection=True,
                #                          use_active_collection=False,
                #                          global_scale=1.0,
                #                          apply_unit_scale=True,
                #                          apply_scale_options='FBX_SCALE_NONE',
                #                          use_space_transform=False,
                #                          bake_space_transform=False,
                #                          object_types={'ARMATURE', 'CAMERA', 'EMPTY', 'LIGHT', 'MESH', 'OTHER'},
                #                          use_mesh_modifiers=True,
                #                          use_mesh_modifiers_render=True,
                #                          mesh_smooth_type='OFF',
                #                          use_subsurf=False,
                #                          use_mesh_edges=False,
                #                          use_tspace=False,
                #                          use_custom_props=False,
                #                          add_leaf_bones=True,
                #                          primary_bone_axis='Y',
                #                          secondary_bone_axis='X',
                #                          use_armature_deform_only=False,
                #                          armature_nodetype='NULL',
                #                          bake_anim=False,
                #                          bake_anim_use_all_bones=False,
                #                          bake_anim_use_nla_strips=False,
                #                          bake_anim_use_all_actions=False,
                #                          bake_anim_force_startend_keying=False,
                #                          bake_anim_step=1.0,
                #                          bake_anim_simplify_factor=1.0,
                #                          path_mode='AUTO',
                #                          embed_textures=False,
                #                          batch_mode='OFF',
                #                          use_batch_own_dir=True,
                #                          use_metadata=True,
                #                          axis_forward='-Z',
                #                          axis_up='Y')

                bpy.ops.export_scene.fbx(filepath=path_to_export_file,
                                         check_existing=False,
                                         use_active_collection=True,
                                         global_scale=1.0,
                                         use_space_transform=False,
                                         bake_space_transform=False,
                                         use_custom_props=False,
                                         add_leaf_bones=False,
                                         primary_bone_axis='Y',
                                         secondary_bone_axis='X',
                                         use_armature_deform_only=False,
                                         bake_anim=False,
                                         axis_forward='-Z',
                                         axis_up='Y')


                # delete the mesh
                ad = imported_armature.animation_data
                if ad:
                    if ad.action:
                        action_name = ad.action.name
                        bpy.data.actions[action_name].user_clear()

                bpy.ops.object.delete(use_global=False)

            if export_obj:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                for mesh in imported_meshes:
                    mesh.select_set(state=True)
                    bpy.context.view_layer.objects.active = mesh

                if combine_meshes:
                    bpy.ops.object.join()

                # print("=======DEBUG: " + scene.name)
                # raise KeyboardInterrupt()

                # export the armature
                basefilename = os.path.splitext(i.name)[0]
                tmp_path_to_file = (os.path.join(folder, basefilename))
                path_to_export_file = (tmp_path_to_file + "_processed.obj")
                bpy.ops.export_scene.obj(filepath=path_to_export_file,
                                         check_existing=False,
                                         filter_glob='*.obj',
                                         use_selection=True,
                                         use_animation=False,
                                         use_mesh_modifiers=True,
                                         use_edges=True,
                                         use_smooth_groups=False,
                                         use_smooth_groups_bitflags=False,
                                         use_normals=True,
                                         use_uvs=True,
                                         use_materials=True,
                                         use_triangles=False,
                                         use_nurbs=False,
                                         use_vertex_groups=False,
                                         use_blen_objects=True,
                                         group_by_object=False,
                                         group_by_material=False,
                                         keep_vertex_order=False,
                                         global_scale=export_scale,
                                         path_mode='AUTO',
                                         axis_forward='-Z',
                                         axis_up='Y')

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
