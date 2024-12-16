import bpy
from bpy.types import Panel, UIList, Operator, Collection, UILayout
from ..data.scene import SceneData
from ..data.prefs import SourcePreferences
from .exporter import draw_export_properties
from . import lists, tabs

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