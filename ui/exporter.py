import bpy
from bpy.props import BoolProperty, EnumProperty
from ..data.scene import CollectionData
import io_scene_gltf2 as gltf2
from ..util import override_props
from ..data.prefs import SourcePreferences
from bpy_extras.io_utils import ExportHelper

class IO_FH_src_gltf(bpy.types.FileHandler):
    bl_idname = "IO_FH_src_gltf"
    bl_label = "glTF (Source Engine)"
    bl_import_operator = "import_scene.gltf"
    bl_export_operator = "export_scene.src_gltf"
    bl_file_extensions = ".glb;.gltf"

@override_props
class ExportGLTF2_Sourcery(bpy.types.Operator, gltf2.ExportGLTF2_Base, ExportHelper):
    """Export scene as a specialized glTF 2.0 file"""
    bl_idname = 'export_scene.src_gltf'
    bl_label = 'Export glTF (Sourcery)'

    # Don't overwrite glTF settings
    will_save_settings: BoolProperty(default=False)

    # Disable unsupported features
    export_morph: BoolProperty(default=False)
    export_skins: BoolProperty(default=False)
    export_animations: BoolProperty(default=False)

    # Don't export textures
    export_image_format: EnumProperty(default='NONE')

    # Enable certain things by default
    export_apply: BoolProperty(default=True)    # apply modifiers
    export_tangents: BoolProperty(default=True) # export tangents

    def draw(self, context):
        draw_export_properties(self, context, self)

def draw_export_properties(self, context, operator, compact=False):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False  # No animation.

    # Are we inside the File browser
    is_file_browser = context.space_data.type == 'FILE_BROWSER'

    if context.collection and context.collection.sourcery_data:
        data: CollectionData = context.collection.sourcery_data
        prefs = SourcePreferences.get()

        header, body = layout.panel("SRC_gltf_props")
        header.label(text="Properties")
        if body:
            CollectionData.draw(data, body, context)

    header, body = layout.panel("SRC_gltf_options", default_closed=True)
    header.label(text="glTF Options")
    if body:
        export_main(body, operator, is_file_browser)
        #gltf2.export_panel_collection(body, operator, is_file_browser)   # only contains 'at_collection_center', moved to Scene Graph
        body.use_property_split = not compact
        export_panel_include(body, operator, is_file_browser)
        #gltf2.export_panel_transform(body, operator)                     # only contains +Y up option, we always want that
        export_panel_data(body, operator)
        #gltf2.export_panel_animation(body, operator)                     # unsupported

        # If gltfpack is not setup in plugin preferences -> don't show any gltfpack relevant options in export dialog
        gltfpack_path = context.preferences.addons['io_scene_gltf2'].preferences.gltfpack_path_ui.strip()
        if gltfpack_path != '':
            gltf2.export_panel_gltfpack(body, operator)

        gltf2.export_panel_user_extension(context, body)

def export_main(layout, operator, is_file_browser):
    # Override: disable changing export format
    col = layout.column()
    #col.enabled = False
    col.prop(operator, 'export_format')
    if operator.export_format == 'GLTF_SEPARATE':
        layout.prop(operator, 'export_keep_originals')
        if operator.export_keep_originals is False:
            layout.prop(operator, 'export_texture_dir', icon='FILE_FOLDER')
    if operator.export_format == 'GLTF_EMBEDDED':
        layout.label(
            text="This is the least efficient of the available forms, and should only be used when required.",
            icon='ERROR')

    layout.prop(operator, 'export_copyright')
    if is_file_browser:
        layout.prop(operator, 'will_save_settings')


def export_panel_include(layout, operator, is_file_browser):
    if not is_file_browser: # Only for file browser mode for now
        return
    return gltf2.export_panel_include(layout, operator, is_file_browser)

def export_panel_data(layout, operator):
    #header, body = layout.panel("GLTF_export_data", default_closed=True)
    #header.label(text="Data")
    body = layout
    if body:
        export_panel_data_scene_graph(body, operator)
        gltf2.export_panel_data_mesh(body, operator)
        #gltf2.export_panel_data_material(body, operator)   # not exposed to user
        #gltf2.export_panel_data_shapekeys(body, operator)  # unsupported
        #gltf2.export_panel_data_armature(body, operator)   # unsupported
        #gltf2.export_panel_data_skinning(body, operator)   # unsupported
        #gltf2.export_panel_data_lighting(body, operator)   # unsupported

        if gltf2.is_draco_available():
            gltf2.export_panel_data_compression(body, operator)

def export_panel_data_scene_graph(layout, operator):
    header, body = layout.panel("GLTF_export_data_scene_graph", default_closed=True)
    header.label(text="Scene Graph")
    if body:
        body.prop(operator, 'at_collection_center')         # moved from export_panel_collection
        body.prop(operator, 'export_gn_mesh')
        #body.prop(operator, 'export_gpu_instances')        # unsupported
        body.prop(operator, 'export_hierarchy_flatten_objs')
        body.prop(operator, 'export_hierarchy_full_collections')