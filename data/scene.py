import bpy
from bpy.types import PropertyGroup, UIList, Collection
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

    @staticmethod
    def save_to_gltf(self, data):
        if self.scale_mode == 'CUSTOM':
            data['$scale'] = self.scale
        elif self.scale_mode in SCALES:
            data['$scale'] = SCALES[self.scale_mode]


'''
class ModelData(CollectionData):
    name: StringProperty(name='Name', default='Model')
    collection: PointerProperty(name='Reference', type=Collection)

class SourceData(PropertyGroup):
    models: CollectionProperty(type=ModelData)
    models_active: bpy.props.IntProperty(default=-1)

    @property
    def data_path(self):
        return f'scene.sourcery_data'

    @staticmethod
    def get(context) -> 'SourceData':
        return context.scene.sourcery_data
'''

###############################################################################

def register():
    #bpy.types.Scene.sourcery_data = bpy.props.PointerProperty(type=SourceData)
    bpy.types.Collection.sourcery_data = bpy.props.PointerProperty(type=CollectionData)

