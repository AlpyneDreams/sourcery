import bpy
from .. import ui
from bpy.types import AddonPreferences, Operator, PropertyGroup, UIList
from bpy.props import StringProperty, CollectionProperty, IntProperty, PointerProperty
from .surfaceprops import SurfaceProp, SURFACEPROPS

class GameInfo(PropertyGroup):
    name: StringProperty(
        name='Name',
        description='Name of the game',
        default='Game'
    )
    gamedir: StringProperty(
        name='Game Folder', 
        subtype='DIR_PATH',
        description='Path to folder containing gameinfo.txt',
        default=''
    )

###############################################################################

class SourcePrefs:
    games: CollectionProperty(type=GameInfo)
    games_active: IntProperty(default=-1)
    surfaceprops: CollectionProperty(type=SurfaceProp)

class SourcePrefsProp(SourcePrefs, PropertyGroup):
    pass
    
###############################################################################

class GameList(UIList):
    bl_idname = 'SRC_UL_game_list'
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, 'name', text='', icon='FILE_FOLDER', emboss=False, translate=False)

###############################################################################

package_parts = __package__.split('.')
package_name = '.'.join(package_parts[:-1])

class SourcePreferences(SourcePrefs, AddonPreferences):
    bl_idname = package_name

    @staticmethod
    def get() -> 'SourcePreferences':
        return bpy.context.preferences.addons[package_name].preferences
    
    @property
    def data_path(self):
        return f'preferences.addons["{package_name}"].preferences'
    
    def save(self, data):
        for key, value in self.items():
            data[key] = value

    def load(self, data):
        for key, value in data.items():
            self[key] = value

    def draw(self, context):
        layout = self.layout
        prefs = SourcePreferences.get()

        game = ui.draw_list(layout, 'SRC_UL_game_list', prefs, 'games', prefs, 'games_active', rows=(4 if len(self.games) > 1 else 3))
        
        if game is not None:
            col = layout.column()
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(game, 'name')
            col.prop(game, 'gamedir')

###############################################################################

def register():
    bpy.types.WindowManager.sourcery_prefs = PointerProperty(type=SourcePrefsProp)

    prefs = SourcePreferences.get()

    # Load prefs if they're already saved
    if hasattr(bpy.context.window_manager, 'sourcery_prefs'):
        prefs.load(bpy.context.window_manager.sourcery_prefs)

    if len(prefs.surfaceprops) != len(SURFACEPROPS):
        prefs.surfaceprops.clear()
        for prop in SURFACEPROPS:
            prefs.surfaceprops.add().name = prop
        
        

def pre_unregister():
    # Save prefs to the WindowManager so they aren't cleared when we reload the addon
    SourcePreferences.get().save(bpy.context.window_manager.sourcery_prefs)
