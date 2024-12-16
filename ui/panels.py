import bpy
from bpy.types import Panel
from ..data.scene import ObjectData
from ..data.prefs import SourcePreferences
from . import tabs

class SourcePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Sourcery'


###############################################################################

class MainPanel(SourcePanel, Panel):
    bl_idname = 'SRC_PT_main'
    bl_label = 'Sourcery'
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        prefs = SourcePreferences.get()

        layout.prop(prefs, 'tab_active', expand=True)
        
        if prefs.tab_active == 'MODELS':
            tabs.draw_tab_models(self, layout, context)
        elif prefs.tab_active == 'OBJECTS':
            tabs.draw_tab_objects(self, layout, context)

class ObjectListPanel(SourcePanel, Panel):
    bl_idname = 'SRC_PT_objects'
    bl_label = 'Tagged Objects'
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return SourcePreferences.get().tab_active == 'OBJECTS'

    def draw(self, context):
        tabs.draw_panel_object_list(self, self.layout, context)


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