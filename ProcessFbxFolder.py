bl_info = {
        'name': 'Process FBX Files',
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
import bpy, os
from bpy.props import *


import os
import warnings

# ImportHelper mixin class uses this
filename_ext = ".fbx"

filter_glob : StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        )

class BR_OT_process_fbx_folder(bpy.types.Operator, ImportHelper):
        """Process Multiple Obj Files at Once"""
        bl_idname = 'import_scene.process_fbx_folder'
        bl_label = 'Process all fbx files in a folder and export'
        bl_options = {'PRESET', 'UNDO'}
        bl_description = "process all fbx files in a folder"



        # Selected files
        files : CollectionProperty(type=bpy.types.PropertyGroup)

        # List of operator properties, the attributes will be assigned
        # to the class instance from the operator settings before calling.
        ngons_setting : BoolProperty(
                name="NGons",
                description="Import faces with more than 4 verts as ngons",
                default=True,
                )
        edges_setting : BoolProperty(
                name="Lines",
                description="Import lines and faces with 2 verts as edge",
                default=True,
                )
        smooth_groups_setting : BoolProperty(
                name="Smooth Groups",
                description="Surround smooth groups by sharp edges",
                default=True,
                )

        split_objects_setting : BoolProperty(
                name="Object",
                description="Import OBJ Objects into Blender Objects",
                default=True,
                )
        split_groups_setting : BoolProperty(
                name="Group",
                description="Import OBJ Groups into Blender Objects",
                default=True,
                )

        groups_as_vgroups_setting : BoolProperty(
                name="Poly Groups",
                description="Import OBJ groups as vertex groups",
                default=False,
                )

        image_search_setting : BoolProperty(
                name="Image Search",
                description="Search subdirs for any associated images "
                            "(Warning, may be slow)",
                default=True,
                )

        split_mode_setting : EnumProperty(
                name="Split",
                items=(('ON', "Split", "Split geometry, omits unused verts"),
                       ('OFF', "Keep Vert Order", "Keep vertex order from file"),
                       ),
                default='OFF',
                )

        clamp_size_setting : FloatProperty(
                name="Clamp Size",
                description="Clamp bounds under this value (zero to disable)",
                min=0.0, max=1000.0,
                soft_min=0.0, soft_max=1000.0,
                default=0.0,
                )
        axis_forward_setting : EnumProperty(
                name="Forward",
                items=(('X', "X Forward", ""),
                       ('Y', "Y Forward", ""),
                       ('Z', "Z Forward", ""),
                       ('-X', "-X Forward", ""),
                       ('-Y', "-Y Forward", ""),
                       ('-Z', "-Z Forward", ""),
                       ),
                default='-Z',
                )

        axis_up_setting : EnumProperty(
                name="Up",
                items=(('X', "X Up", ""),
                       ('Y', "Y Up", ""),
                       ('Z', "Z Up", ""),
                       ('-X', "-X Up", ""),
                       ('-Y', "-Y Up", ""),
                       ('-Z', "-Z Up", ""),
                       ),
                default='Y',
                )

        def draw(self, context):
            layout = self.layout

            row = layout.row(align=True)
            row.prop(self, "ngons_setting")
            row.prop(self, "edges_setting")

            layout.prop(self, "smooth_groups_setting")

            box : layout.box()
            row : box.row()
            row.prop(self, "split_mode_setting", expand=True)

            row : box.row()
            if self.split_mode_setting == 'ON':
                row.label(text="Split by:")
                row.prop(self, "split_objects_setting")
                row.prop(self, "split_groups_setting")
            else:
                row.prop(self, "groups_as_vgroups_setting")

            row.prop(self, "clamp_size_setting")
            layout.prop(self, "axis_forward_setting")
            layout.prop(self, "axis_up_setting")

            layout.prop(self, "image_search_setting")

        def execute(self, context):

            # get the folder
            folder = (os.path.dirname(self.filepath))

            # iterate through the selected files
            for i in self.files:

                # generate full path to file
                path_to_file = (os.path.join(folder, i.name))

                # call obj operator and assign ui values                  
                bpy.ops.import_scene.fbx(filepath = path_to_file,
                                    axis_forward = self.axis_forward_setting,
                                    axis_up = self.axis_up_setting, 
                                    use_edges = self.edges_setting,
                                    use_smooth_groups = self.smooth_groups_setting, 
                                    use_split_objects = self.split_objects_setting,
                                    use_split_groups = self.split_groups_setting,
                                    use_groups_as_vgroups = self.groups_as_vgroups_setting,
                                    use_image_search = self.image_search_setting,
                                    split_mode = self.split_mode_setting,
                                    global_clight_size = self.clamp_size_setting)
                                    
#  utils for batch processing kitbash stamps.       
#                bpy.context.scene.objects.active = bpy.context.selected_objects[0]
#                bpy.ops.object.modifier_add(type='SUBSURF')
#                bpy.context.object.modifiers["Subsurf"].levels = 2
#                bpy.ops.object.modifier_add(type='DECIMATE')
#                bpy.context.object.modifiers["Decimate.001"].ratio = 0.5
#                bpy.ops.object.modifier_add(type='DECIMATE')
#                bpy.context.object.modifiers["Decimate.001"].decimate_type = 'DISSOLVE'
#                bpy.context.object.modifiers["Decimate.001"].delimit = {'SEAM', 'SHARP'}
#                bpy.context.object.modifiers["Decimate.001"].angle_limit = 0.0523599
#                bpy.ops.object.modifier_add(type='TRIANGULATE')
#                bpy.context.object.modifiers["Triangulate"].quad_method = 'BEAUTY'
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate")
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Decimate.001")
#                # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Triangulate")
#                bpy.ops.object.mode_set(mode='EDIT')
#                bpy.ops.mesh.select_all(action = 'DESELECT')
#                bpy.ops.mesh.select_all(action='TOGGLE')
#                bpy.ops.mesh.tris_convert_to_quads()
#                bpy.ops.mesh.faces_shade_smooth()
#                bpy.ops.mesh.mark_sharp(clear=True)
#                bpy.ops.mesh.mark_sharp(clear=True, use_verts=True)
#                #if not bpy.context.object.data.uv_layers:
#                bpy.ops.uv.smart_project(island_margin=0.01 , user_area_weight=0.75)
#                bpy.ops.object.mode_set(mode='OBJECT')
#                bpy.context.object.data.use_auto_smooth = True
#                bpy.context.object.data.auto_smooth_angle = 0.575959

                #process the mesh
                imported_objects = bpy.context.selected_objects

                # for ob in imported_objects:
                #     ob.select_set(state=True)
                #     bpy.context.view_layer.objects.active = ob
                # bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                # bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
                # bpy.ops.mesh.normals_make_consistent(inside=False)
                # bpy.ops.mesh.remove_doubles()

                #export the mesh
                basefilename = os.path.splitext(i.name)[0]
                tmp_path_to_file = (os.path.join(folder, basefilename))
                path_to_export_file = (tmp_path_to_file + "_processed.fbx")
            

                bpy.ops.export_scene.fbx(   filepath = path_to_export_file, use_selection   =   True )

                bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                # delete the mesh
                bpy.ops.object.delete(use_global=False)

            return {'FINISHED'}


def menu_import_draw(self, context):
    self.layout.operator(BR_OT_process_fbx_folder.bl_idname)


classes = (
    BR_OT_process_fbx_folder,
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
    bpy.types.VIEW3D_MT_view.remove(menu_import_draw)

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
