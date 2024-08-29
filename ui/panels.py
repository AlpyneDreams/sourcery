import bpy
from bpy.types import Panel, UIList, Operator
from ..data.scene import SourceData
from ..data.prefs import SourcePreferences
from . import lists

'''

class SourcePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sourcery'

class ModelList(UIList):
    bl_idname = 'SRC_UL_model_list'
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, 'name', text='', icon='OUTLINER_COLLECTION', emboss=False, translate=False)

class AddModel(Operator):
    bl_idname = 'src.add_model'
    bl_label = 'Add Model'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        data = SourceData.get(context)
        item = data.models.add()
        if context.collection:
            item.name = context.collection.name
            item.collection = context.collection
        return {'FINISHED'}

class MainPanel(SourcePanel, Panel):
    bl_idname = 'SRC_PT_main'
    bl_label = 'Models'
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        data = SourceData.get(context)
        prefs = SourcePreferences.get()

        model = lists.draw_list(layout, 'SRC_UL_model_list', data, 'models', data, 'models_active', add='src.add_model')
        if model:
            (header, col) = layout.panel('model_props')
            header.label(text='Model Properties')
            col = col.column(align=False)
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(model, 'name')
            col.prop(model, 'collection')
            col.prop(model, 'collision', icon='MESH_ICOSPHERE')
            col.prop_search(
                model, 'surfaceprop',
                prefs, 'surfaceprops',
                text='Surface Property',
                results_are_suggestions=True,
                icon='PLAY_SOUND'
            )

        row = layout.row(align=True)
        row.operator('src.add_item', icon='EXPORT', text='Export All')


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