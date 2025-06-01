import bpy
from bpy.props import BoolProperty
from bpy.types import Object, UIList, UILayout, Operator, Context
from ...data.scene import SceneData, ObjectData, CollisionModeProperty
from .. import lists

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
    collision_mode_dummy: CollisionModeProperty
    filter_invisible: BoolProperty(name='Filter Invisible', default=False)
    filter_mesh: BoolProperty(name='Filter Mesh Colliders', default=False)
    filter_hull: BoolProperty(name='Filter Hull Colliders', default=False)
    filter_box: BoolProperty(name='Filter Box Colliders', default=False)
    filter_none: BoolProperty(name='Filter Non-Colliders', default=False)


    def draw_item(self, context, layout: UILayout, container, item: Object, icon, active_data, active_propname):
        data: ObjectData = item.sourcery_data
        if data.collision_mode != 'AUTO':
            layout.prop(item, 'name', text='', icon_value=layout.enum_item_icon(data, 'collision_mode', data.collision_mode), emboss=False, translate=False)
        else:
            layout.prop(item, 'name', text='', icon='RESTRICT_RENDER_ON' if not data.visible else 'OBJECT_DATA', emboss=False, translate=False)

    def filter_items(self, context, data, property):
        items = getattr(data, property)
        flag_hide = self.bitflag_filter_item if self.use_filter_invert else 0
        flag_show = self.bitflag_filter_item if not self.use_filter_invert else 0
        filter_modes = self.filter_mesh or self.filter_hull or self.filter_box or self.filter_none

        # Filter by name
        if self.filter_name:
            flags = bpy.types.UI_UL_list.filter_items_by_name(self.filter_name, self.bitflag_filter_item, items, 'name')
        else:
            flags = [flag_show] * len(items)
        
        # Filter by presence of data and collision mode
        for i, item in enumerate(items):
            if not obj_has_data(item):
                flags[i] = flag_hide
            elif filter_modes:
                if not self.filter_invisible and not item.sourcery_data.visible:
                    flags[i] = flag_hide
                elif not self.filter_mesh and item.sourcery_data.collision_mode == 'MESH':
                    flags[i] = flag_hide
                elif not self.filter_hull and item.sourcery_data.collision_mode == 'HULL':
                    flags[i] = flag_hide
                elif not self.filter_box and item.sourcery_data.collision_mode == 'BOX':
                    flags[i] = flag_hide
                elif not self.filter_none and item.sourcery_data.collision_mode == 'NONE':
                    flags[i] = flag_hide
                
        return (flags, [])
    
    def draw_filter(self, context, main_layout: UILayout):
        layout = main_layout.row()

        # Standard filters
        row = layout.column().row(align=True)
        row.prop(self, 'filter_name', text='')
        row.prop(self, 'use_filter_invert', icon='ARROW_LEFTRIGHT', icon_only=True)
        row = layout.column().row(align=True)
        row.prop(self, 'use_filter_sort_alpha', icon='SORTALPHA', icon_only=True)
        row.prop(self, 'use_filter_sort_reverse', icon=('SORT_DESC' if self.use_filter_sort_reverse else 'SORT_ASC'), icon_only=True)

        # Filter by collision mode
        row = layout.column().row(align=True)
        row.prop(self, 'filter_invisible', icon_only=True, icon='RESTRICT_RENDER_ON')
        row.prop(self, 'filter_mesh', icon_only=True, icon_value=layout.enum_item_icon(self, 'collision_mode_dummy', 'MESH'))
        row.prop(self, 'filter_hull', icon_only=True, icon_value=layout.enum_item_icon(self, 'collision_mode_dummy', 'HULL'))
        row.prop(self, 'filter_box', icon_only=True, icon_value=layout.enum_item_icon(self, 'collision_mode_dummy', 'BOX'))
        row.prop(self, 'filter_none', icon_only=True, icon_value=layout.enum_item_icon(self, 'collision_mode_dummy', 'NONE'))


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
    

# Selected Object Operators
###############################################################################

class AddTags(Operator):
    bl_idname = 'src.add_tags'
    bl_description = 'Add tags to the selected objects'
    bl_label = 'Tag Object'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
    collision_mode: CollisionModeProperty
    visible: BoolProperty(name='Visible', default=True)

    @classmethod
    def poll(cls, context):
        # True if any taggable objects are selected
        for obj in context.selected_objects:
            if obj_can_have_data(obj):
                return True
        return False

    def execute(self, context):
        last = None
        for obj in context.selected_objects:
            if obj_can_have_data(obj):
                if (self.collision_mode != 'AUTO'):
                    obj.sourcery_data.collision_mode = self.collision_mode
                if (self.visible != True):
                    obj.sourcery_data.visible = self.visible
                last = obj
        if last is not None:
            SceneData.get(context).objects_active = bpy.data.objects.find(last.name)
        return {'FINISHED'}

class AddTagsDropdown(bpy.types.Menu):
    bl_idname       = "SRC_MT_add_tags"
    bl_label        = "Add Selected Objects"
    bl_description  = "Add tags to the selected objects."

    def draw(self, context):
        if len(context.selected_objects) == 0:
            self.layout.label(text='No meshes selected.', icon='ERROR')
            self.layout.separator()
        for id, name, desc, icon, number in CollisionModeProperty.keywords['items']:
            if id != 'AUTO':
                self.layout.operator(AddTags.bl_idname, icon=icon, text=name).collision_mode = id

class RemoveTags(Operator):
    bl_idname       = 'src.remove_tags'
    bl_description  = 'Clear tags from selected objects'
    bl_label        = 'Clear Tags'
    bl_options      = {'INTERNAL', 'REGISTER', 'UNDO'}

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


# Object List Menu
###############################################################################

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
    

class SelectObjectsByTag(Operator):
    bl_idname = 'src.select_objects_by_tag'
    bl_description = 'Select objects based on their tags.'
    bl_label = 'Select By Tag'
    bl_options = {'INTERNAL', 'REGISTER', 'UNDO'}
    collision_mode: CollisionModeProperty

    def execute(self, context):
        for object in bpy.data.objects:
            if obj_has_data(object) and object.sourcery_data.collision_mode == self.collision_mode:
                object.select_set(True)
        return {'FINISHED'}

class ObjectMenu(bpy.types.Menu):
    bl_idname = "SRC_MT_object"
    bl_label = "Object List"

    def draw(self, context):
        layout = self.layout
        layout.operator(SelectAllObjects.bl_idname, icon='SELECT_SET')
        layout.separator()
        for id, name, desc, icon, number in CollisionModeProperty.keywords['items']:
            if id != 'AUTO':
                layout.operator(SelectObjectsByTag.bl_idname, icon=icon, text='Select Colliders: ' + name).collision_mode = id

# Sidebar Panels
###############################################################################

def draw_tab_objects(panel, layout: UILayout, context: Context):
    layout.label(text='Collision Tags', icon='MESH_ICOSPHERE')
    flow = layout.grid_flow(row_major=True, columns=0 if context.region.width < 200 else 2, even_columns=True, even_rows=False, align=False)

    # Collision Tag Buttons
    for id, name, desc, icon, number in CollisionModeProperty.keywords['items']:
        if id != 'AUTO':
            flow.operator(AddTags.bl_idname, icon=icon, text=name).collision_mode = id

    layout.operator(AddTags.bl_idname, icon='RESTRICT_RENDER_ON', text='Invisible').visible = False
    layout.operator(RemoveTags.bl_idname, icon='TRASH', text='Clear Tags')

    #layout.separator(factor=2, type='LINE')

def draw_panel_object_list(panel, layout: UILayout, context):
    scene_data = SceneData.get(context)
    row = layout.row()
    object: Object = lists.draw_list_simple(row, 'SRC_UL_object_list', bpy.data, 'objects', scene_data, 'objects_active')

    col = row.column(align=True)
    col.menu(AddTagsDropdown.bl_idname, icon='ADD', text='')
    col.operator(RemoveObject.bl_idname, icon='REMOVE', text='')
    col.separator()
    col.menu(ObjectMenu.bl_idname, icon='DOWNARROW_HLT', text="")

    row = layout.row(align=True)
    row.operator(SelectObject.bl_idname)
    row.operator(DeselectObject.bl_idname)

    if object:
        layout.separator()
        layout.use_property_decorate = False
        layout.use_property_split = True

        header, layout = layout.panel("SRC_gltf_props")
        header.label(text=object.name)
        
        # Object Data
        data: ObjectData = object.sourcery_data
        
        row = layout.split(factor=0.4)
        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text='Visibility')
        row.use_property_split = False
        row.column().prop(data, 'visible', text='Invisible', toggle=True, invert_checkbox=True, icon='RESTRICT_RENDER_ON')

        row = layout.split(factor=0.4)
        col = row.column()
        col.alignment = 'RIGHT'
        col.label(text='Collision')
        if context.region.width < 250:
            row = row.column(align=True)
            row.use_property_split = False
            row.prop_enum(data, 'collision_mode', 'AUTO')
        else:
            col = row.column(align=True)
            col.use_property_split = False
            col.prop_enum(data, 'collision_mode', 'AUTO')
            row = col.grid_flow(align=True, columns=2)
        row.prop_enum(data, 'collision_mode', 'MESH')
        row.prop_enum(data, 'collision_mode', 'HULL')
        row.prop_enum(data, 'collision_mode', 'BOX')
        row.prop_enum(data, 'collision_mode', 'NONE')


# Properties Panel
###############################################################################

class ObjectPanel(bpy.types.Panel):
    bl_idname       = 'SRC_PT_object'
    bl_label        = 'Sourcery'
    bl_space_type   = "PROPERTIES"
    bl_region_type  = "WINDOW"
    bl_context      = "object"
    bl_options      = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return obj_can_have_data(context.object)

    def draw(self, context):
        layout = self.layout.column()
        layout.use_property_split = True
        layout.use_property_decorate = False
        ObjectData.draw(context.object.sourcery_data, layout, context)
