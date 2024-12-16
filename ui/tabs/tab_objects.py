import bpy
from bpy.types import Object, UIList, UILayout, Operator, Context
from ...data.scene import SceneData, ObjectData, COLLISION_MODE_ICONS, CollisionModeProperty
from .. import lists

###############################################################################

COLLISION_MODE_NAMES = {
    'AUTO': 'Auto',
    'MESH': 'Add Mesh',
    'HULL': 'Add Hull',
    'BOX': 'Add Box',
    'NONE': 'No Collision',
}

###############################################################################

def obj_can_have_data(obj):
    return obj.type == 'MESH'

def obj_has_data(obj):
    return obj.sourcery_data and not obj.sourcery_data.is_empty()

def obj_can_add_data(obj):
    return obj_can_have_data(obj) and not obj_has_data(obj)

###############################################################################

class ObjectList(UIList):
    bl_idname = 'SRC_UL_object_list'
    def draw_item(self, context, layout: UILayout, data, item: Object, icon, active_data, active_propname):
        layout.prop(item, 'name', text='', icon=COLLISION_MODE_ICONS[item.sourcery_data.collision_mode] or 'OBJECT_DATA', emboss=False, translate=False)

    def filter_items(self, context, data, property):
        items = getattr(data, property)
        flags = []
        for item in items:
            flag = 0
            if item.type == 'MESH':
                if obj_has_data(item):
                    flag = self.bitflag_filter_item
            flags.append(flag)
        return (flags, [])

# Tagged Object List Operators
###############################################################################

class ObjectListOp:
    @classmethod
    def poll(cls, context):
        scene_data = SceneData.get(context)
        return scene_data.objects_active >= 0    

class RemoveObject(ObjectListOp, Operator):
    bl_idname = 'src.remove_object'
    bl_description = 'Clear tags from this object'
    bl_label = 'Clear Tags'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_data = SceneData.get(context)
        object = bpy.data.objects[scene_data.objects_active]
        if object:
            object.sourcery_data.reset()
        while scene_data.objects_active >= 0 and not obj_has_data(bpy.data.objects[scene_data.objects_active]):
            scene_data.objects_active -= 1

        return {'FINISHED'}    

class SelectObject(ObjectListOp, Operator):
    bl_idname = 'src.select_object'
    bl_description = 'Select this object'
    bl_label = 'Select'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_data = SceneData.get(context)
        object = bpy.data.objects[scene_data.objects_active]
        if object:
            object.select_set(True)

        return {'FINISHED'}
    
class DeselectObject(ObjectListOp, Operator):
    bl_idname = 'src.deselect_object'
    bl_description = 'Deselect this object'
    bl_label = 'Deselect'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_data = SceneData.get(context)
        object = bpy.data.objects[scene_data.objects_active]
        if object:
            object.select_set(False)

        return {'FINISHED'}
    

class SelectAllObjects(Operator):
    bl_idname = 'src.select_all_objects'
    bl_description = 'Select all tagged objects.'
    bl_label = 'Select All'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    def execute(self, context):
        for object in bpy.data.objects:
            if obj_has_data(object):
                object.select_set(True)
        return {'FINISHED'}


# Selected Object Operators
###############################################################################

class AddTags(Operator):
    bl_idname = 'src.add_tags'
    bl_description = 'Set tags for the selected objects'
    bl_label = 'Tag Object'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
    collision_mode: CollisionModeProperty

    @classmethod
    def poll(cls, context):
        # True ff any taggable objects are selected
        for obj in context.selected_objects:
            if obj_can_have_data(obj):
                return True
        return False

    def execute(self, context):
        last = None
        for obj in context.selected_objects:
            if obj_can_have_data(obj):
                if self.collision_mode == 'AUTO':
                    obj.sourcery_data.modified = True
                else:
                    obj.sourcery_data.collision_mode = self.collision_mode
                last = obj
        if last is not None:
            SceneData.get(context).objects_active = bpy.data.objects.find(last.name)
        return {'FINISHED'}

class RemoveTags(Operator):
    bl_idname = 'src.remove_tags'
    bl_description = 'Clear tags from selected objects'
    bl_label = 'Clear Tags'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        for obj in context.selected_objects:
            if obj_has_data(obj):
                return True
        return False

    def execute(self, context):
        scene_data = SceneData.get(context)
        for obj in context.selected_objects:
            obj.sourcery_data.reset()
            while scene_data.objects_active >= 0 and not obj_has_data(bpy.data.objects[scene_data.objects_active]):
                scene_data.objects_active -= 1

        return {'FINISHED'}


# Object Menu
###############################################################################

class ObjectMenu(bpy.types.Menu):
    bl_idname = "SRC_MT_object"
    bl_label = "Object"

    def draw(self, context):
        layout = self.layout
        layout.operator(SelectAllObjects.bl_idname)

# Sidebar Panel
###############################################################################

def draw_tab_objects(panel, layout: UILayout, context: Context):
    count = len(context.selected_objects)
    if count != 0:
        layout.label(text='Selected Objects (' + str(count) + ')', icon='OBJECT_DATA')
    else:
        layout.label(text='Selected Objects', icon='OBJECT_DATA')
    flow = layout.grid_flow(row_major=True, columns=0 if context.region.width < 200 else 2, even_columns=True, even_rows=False, align=False)
    flow.operator(AddTags.bl_idname, icon='TAG', text='Add Tags')
    flow.operator(RemoveTags.bl_idname, icon='PANEL_CLOSE', text='Clear Tags')

    for mode, icon in COLLISION_MODE_ICONS.items():
        if icon:
            flow.operator(AddTags.bl_idname, icon=icon, text=COLLISION_MODE_NAMES[mode]).collision_mode = mode

    #layout.separator(factor=2, type='LINE')

def draw_panel_object_list(panel, layout: UILayout, context):
    scene_data = SceneData.get(context)
    row = layout.row()
    object: Object = lists.draw_list_simple(row, 'SRC_UL_object_list', bpy.data, 'objects', scene_data, 'objects_active')

    col = row.column(align=True)
    col.operator(AddTags.bl_idname, icon='ADD', text='')
    col.operator(RemoveObject.bl_idname, icon='REMOVE', text='')
    col.separator()
    col.menu(ObjectMenu.bl_idname, icon='DOWNARROW_HLT', text="")

    row = layout.row(align=True)
    row.operator(SelectObject.bl_idname)
    row.operator(DeselectObject.bl_idname)

    if object:
        layout.separator()
        header, body = layout.panel("SRC_gltf_props")
        header.label(text=object.name)
        body.use_property_split = True
        ObjectData.draw(object.sourcery_data, body, context)

# Properties Panel
###############################################################################

class ObjectPanel(bpy.types.Panel):
    bl_idname = 'SRC_PT_object'
    bl_label = 'Sourcery'
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return obj_can_have_data(context.object)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        data: ObjectData = context.object.sourcery_data

        col = layout.column()
        col.enabled = False
        col.prop(data, 'modified')

        ObjectData.draw(data, layout, context)
