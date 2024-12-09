import bpy
from bpy.types import PropertyGroup, UIList, Collection, UILayout
from bpy.props import StringProperty, PointerProperty, CollectionProperty, FloatProperty, EnumProperty
from .surfaceprops import SurfaceProp

SCALES = {
    'SCALE_40': 40.0,
    'SCALE_39': (100 * (12 / 30.48)),
    'SCALE_52': (100 * (16 / 30.48)),
    'SCALE_100': 100.0,
    'SCALE_1': 1.0,
}

class CollectionData(PropertyGroup):
    #collision: PointerProperty(name='Collision', type=Collection)
    #surfaceprops: CollectionProperty(type=SurfaceProp)
    #surfaceprop: StringProperty(name='Surface Property', default='default')
    scale_mode: EnumProperty(
        name='Scale',
        items=(
            ('SCALE_40',    "40.00 (1 hu ≈ 1″)",    'Rounded to 40 units per meter for easy metric conversion.'),
            ('SCALE_39',    "39.37 (1 hu = 1″)",    'Exact scale with inches in Blender equal to Hammer Units.'),
            ('SCALE_52',    "52.49 (1 hu = 0.75″)", 'Oversized scale used in HL2 and CSS maps where 16 hu = 1 ft.'),
            ('SCALE_100',   "100.0 (1 hu = 1 cm)",  'Treat centimeters as Hammer Units. This is the default in Source 2.'),
            ('SCALE_1',     "1.000 (1 hu = 1 m)",   'No scaling. Treat Blender meters as Hammer Units.'),
            ('CUSTOM',      "Custom",   'No scaling. Treat Blender meters as Hammer Units.'),
        ),
        description='Scale in number of Hammer Units per Blender meter. This applies regardless of what units your scene uses.',
        default='SCALE_40'
    )
    scale: FloatProperty(name='Custom Scale', default=40.0)
    #collision: PointerProperty(name='Collision', type=Collection)
    collision_mode: EnumProperty(
        name='Collision',
        items=(
            ('AUTO',        "Auto",                 'Automatic based on model size.', '', 0),
            ('MESH',        "Mesh",                 'Concave mesh collider.', 'MESH_MONKEY', 1),
            ('HULL',        "Hull",                 'Convex hull collider.', 'MESH_ICOSPHERE', 2),
            ('BOX',         "Box",                  'Box collider.', 'MESH_CUBE', 3),
            ('NONE',        "None",                 'No collision.', 'PANEL_CLOSE', 4),
        ),
        description='Type of collisions to use.',
        default='AUTO'
    )

    @staticmethod
    def save_to_gltf(self, data):
        if self.scale_mode == 'CUSTOM':
            data['$scale'] = self.scale
        elif self.scale_mode in SCALES:
            data['$scale'] = SCALES[self.scale_mode]

        match self.collision_mode:
            case 'AUTO': pass
            case mode: data['$collision'] = mode.lower()

    @staticmethod
    def draw(self, layout: UILayout, context):
        layout.row().prop(self, 'collision_mode', expand=True)
        layout.prop(self, 'scale_mode')
        if self.scale_mode == 'CUSTOM':
            layout.prop(self, 'scale')
        #layout.prop(data, 'collision', icon='MESH_ICOSPHERE')
        #layout.prop_search(
        #    data, 'surfaceprop',
        #    prefs, 'surfaceprops',
        #    text='Surface Property',
        #    results_are_suggestions=True,
        #    icon='PLAY_SOUND'
        #)

'''
class ModelData(CollectionData):
    name: StringProperty(name='Name', default='Model')
    collection: PointerProperty(name='Reference', type=Collection)

class SceneData(PropertyGroup):
    models: CollectionProperty(type=ModelData)
    models_active: bpy.props.IntProperty(default=-1)

    @property
    def data_path(self):
        return f'scene.sourcery_data'

    @staticmethod
    def get(context) -> 'SceneData':
        return context.scene.sourcery_data
'''

###############################################################################

def register():
    #bpy.types.Scene.sourcery_data = bpy.props.PointerProperty(type=SceneData)
    bpy.types.Collection.sourcery_data = bpy.props.PointerProperty(type=CollectionData)

