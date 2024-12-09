import bpy
from bpy.types import Panel, UIList, Operator, Collection, UILayout
from ..data.scene import SceneData
from ..data.prefs import SourcePreferences
from .exporter import draw_export_properties
from . import lists

class SourcePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sourcery'

def get_src_exporter(collection: Collection):
    for exp in collection.exporters:
        if exp.export_properties.__class__.__name__ == 'EXPORT_SCENE_OT_src_gltf':
            return exp
    return None


class ModelList(UIList):
    bl_idname = 'SRC_UL_model_list'
    def draw_item(self, context, layout, data, item: Collection, icon, active_data, active_propname):
        layout.prop(item, 'name', text='', icon='OUTLINER_COLLECTION', emboss=False, translate=False)

    def filter_items(self, context, data, property):
        items = getattr(data, property)
        flags = [] #bpy.types.UI_UL_list.filter_items_by_name("base", self.bitflag_filter_item, items, "name")
        for item in items:
            # TODO: Filter by current scene somehow
            flag = 0
            exp = get_src_exporter(item)
            if exp:
                flag = self.bitflag_filter_item
            flags.append(flag)
        return (flags, [])

''''
class AddModel(Operator):
    bl_idname = 'src.add_model'
    bl_label = 'Add Model'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        # TODO
        return {'FINISHED'}
    
class RemoveModel(Operator):
    bl_idname = 'src.remove_model'
    bl_label = 'Remove Model'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        # TODO
        return {'FINISHED'}
'''
        
class MainPanel(SourcePanel, Panel):
    bl_idname = 'SRC_PT_main'
    bl_label = 'Models'
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        scene_data = SceneData.get(context)
        prefs = SourcePreferences.get()

        collection: Collection = lists.draw_list_simple(layout, 'SRC_UL_model_list', bpy.data, 'collections', scene_data, 'models_active')

        if collection:
            # Export settings
            with context.temp_override(collection=collection):
                exp = get_src_exporter(collection)
                draw_export_properties(self, context, exp.export_properties, context.region.width < 360)

        # Export and Export All buttons
        row = layout.row()
        if collection:
            with context.temp_override(collection=collection):
                row.operator('collection.export_all', icon='EXPORT', text='Export')
        row.operator('wm.collection_export_all', icon='EXPORT', text='Export All')


'''
class ConfigPanel(SourcePanel, Panel):
    bl_idname = 'SRC_PT_sourcery'
    bl_label = 'Settings'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    def draw(self, context):
        prefs = SourcePreferences.get()
        prefs.layout = self.layout
        prefs.draw(context)

'''