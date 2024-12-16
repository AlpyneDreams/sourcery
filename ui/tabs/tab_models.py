import bpy
from bpy.types import Panel, UIList, Operator, Collection, UILayout
from ...data.scene import SceneData
from ...data.prefs import SourcePreferences
from ..exporter import draw_export_properties
from .. import lists

def get_src_exporter(collection: Collection):
    for exp in collection.exporters:
        if exp.export_properties.__class__.__name__ == 'EXPORT_SCENE_OT_src_gltf':
            return exp
    return None

def get_src_exporter_index(collection: Collection):
    for i, exp in enumerate(collection.exporters):
        if exp.export_properties.__class__.__name__ == 'EXPORT_SCENE_OT_src_gltf':
            return i
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

class AddModel(Operator):
    bl_idname = 'src.add_model'
    bl_description = 'Add a model exporter for the active collection'
    bl_label = 'Add Model'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        scene_data = SceneData.get(context)
        return scene_data.models_active < 0 or bpy.data.collections[scene_data.models_active] is not context.collection

    def execute(self, context):
        bpy.ops.collection.exporter_add(name='IO_FH_src_gltf')
        SceneData.get(context).models_active = bpy.data.collections.find(context.collection.name)
        return {'FINISHED'}
    
class RemoveModel(Operator):
    bl_idname = 'src.remove_model'
    bl_description = 'Remove model exporter from the active collection'
    bl_label = 'Remove Model'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    # FIXME: For some reason context.temp_override(collection=collection) doesn't work
    # for this operator when doing layout.operator, so we have to pass the collection name
    target: bpy.props.StringProperty()

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event, title='Remove exporter?')

    def execute(self, context):
        collection = bpy.data.collections[self.target]
        if collection:
            with context.temp_override(collection=collection):
                idx = get_src_exporter_index(collection)
                if idx is not None:
                    bpy.ops.collection.exporter_remove(index=idx)
                    scene_data = SceneData.get(context)
                    while scene_data.models_active >= 0 and get_src_exporter(bpy.data.collections[scene_data.models_active]) is None:
                        scene_data.models_active -= 1
        return {'FINISHED'}

###############################################################################

def draw_tab_models(panel, layout, context):
    scene_data = SceneData.get(context)
    prefs = SourcePreferences.get()

    row = layout.row()
    collection: Collection = lists.draw_list_simple(row, 'SRC_UL_model_list', bpy.data, 'collections', scene_data, 'models_active')

    col = row.column(align=True)
    op = col.operator('src.add_model', icon='ADD', text='')

    if collection:
        with context.temp_override(collection=collection):
            # Remove model
            op = col.operator('src.remove_model', icon='REMOVE', text='')
            op.target = collection.name

            # Export settings
            exp = get_src_exporter(collection)
            if exp:
                draw_export_properties(panel, context, exp.export_properties, context.region.width < 360)
    else:
        col.operator('src.remove_item_disabled', icon='REMOVE', text='')
    
    # Export and Export All buttons
    row = layout.row()
    if collection:
        with context.temp_override(collection=collection):
            row.operator('collection.export_all', icon='EXPORT', text='Export')
    row.operator('wm.collection_export_all', icon='EXPORT', text='Export All')
