import bpy
from bpy.types import Context, Operator

def draw_list(
        layout, list_type_name, data, key, data_index, key_index,
        add='src.add_item', remove='src.remove_item', move_up='src.move_item_up', move_down='src.move_item_down',
        *args, **kwargs):
    row = layout.row()
    row.template_list(list_type_name, '', data, key, data_index, key_index, *args, **kwargs)

    list = getattr(data, key)
    index = getattr(data_index, key_index)

    col = row.column(align=True)
    op = col.operator(add, icon='ADD', text='')
    if add == 'src.add_item':
        op.list_obj = data.data_path
        op.list_key = key
        op.index_obj = data_index.data_path
        op.index_key = key_index

    if index >= 0:
        op = col.operator(remove, icon='REMOVE', text='')
        if remove == 'src.remove_item':
            op.list_obj = data.data_path
            op.list_key = key
            op.index_obj = data_index.data_path
            op.index_key = key_index
    else:
        op = col.operator('src.remove_item_disabled', icon='REMOVE', text='')

    col.separator()

    length = len(list)
    if length > 1:
        if index > 0:
            op = col.operator(move_up, icon='TRIA_UP', text='')
            if move_up == 'src.move_item_up':
                op.list_obj = data.data_path
                op.list_key = key
                op.index_obj = data_index.data_path
                op.index_key = key_index
        else:
            op = col.operator('src.move_item_up_disabled', icon='TRIA_UP', text='')
        
        if index >= 0 and index < length - 1:
            op = col.operator(move_down, icon='TRIA_DOWN', text='')
            if move_down == 'src.move_item_down':
                op.list_obj = data.data_path
                op.list_key = key
                op.index_obj = data_index.data_path
                op.index_key = key_index
        else:
            op = col.operator('src.move_item_down_disabled', icon='TRIA_DOWN', text='')

    if index >= 0 and index < length:
        return list[index]
    else:
        return None

###############################################################################

class ListOp:
    list_obj: bpy.props.StringProperty()
    list_key: bpy.props.StringProperty()
    index_obj: bpy.props.StringProperty()
    index_key: bpy.props.StringProperty()

    def get_list(self, context):
        list_obj = context.path_resolve(self.list_obj)
        return getattr(list_obj, self.list_key)
    
    def get_index(self, context):
        index_obj = context.path_resolve(self.index_obj)
        return getattr(index_obj, self.index_key)

    def set_index(self, context, index):
        index_obj = context.path_resolve(self.index_obj)
        setattr(index_obj, self.index_key, index)


class AddItem(ListOp, Operator):
    bl_idname = 'src.add_item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Add Item'
    bl_description = 'Add a new item'

    def execute(self, context):
        list = self.get_list(context)
        list.add()
        self.set_index(context, len(list) - 1)
        return {'FINISHED'}
    

class RemoveItem(ListOp, Operator):
    bl_idname = 'src.remove_item'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Remove Item'
    bl_description = 'Remove selected item'

    def execute(self, context):
        list = self.get_list(context)
        index = self.get_index(context)
        list.remove(index)
        self.set_index(context, min(index, len(list) - 1))
        return {'FINISHED'}

class MoveItemUp(ListOp, Operator):
    bl_idname = 'src.move_item_up'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Move Up'
    bl_description = 'Move selected item up in the list'

    def execute(self, context):
        list = self.get_list(context)
        index = self.get_index(context)
        list.move(index, index - 1)
        self.set_index(context, index - 1)
        return {'FINISHED'}
    
class MoveItemDown(ListOp, Operator):
    bl_idname = 'src.move_item_down'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Move Down'
    bl_description = 'Move selected item down in the list'

    def execute(self, context):
        list = self.get_list(context)
        index = self.get_index(context)
        list.move(index, index + 1)
        self.set_index(context, index + 1)
        return {'FINISHED'}

class Disabled:
    @classmethod
    def poll(cls, context):
        return False
    
    def execute(self, context):
        return {'CANCELLED'}

class RemoveItemDisabled(Disabled, Operator):
    bl_idname = 'src.remove_item_disabled'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Remove Item'
    bl_description = 'Remove selected item'

class MoveItemUpDisabled(Disabled, Operator):
    bl_idname = 'src.move_item_up_disabled'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Move Up'
    bl_description = 'Move selected item up in the list'

class MoveItemDownDisabled(Disabled, Operator):
    bl_idname = 'src.move_item_down_disabled'
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    bl_label = 'Move Down'
    bl_description = 'Move selected item down in the list'
