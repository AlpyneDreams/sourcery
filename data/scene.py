import bpy
from bpy.types import PropertyGroup, UIList, Collection, UILayout, Context
from bpy.props import StringProperty, PointerProperty, BoolProperty, FloatProperty, EnumProperty
from .surfaceprops import SurfaceProp

SCALES = {
    'SCALE_40': 40.0,
    'SCALE_39': (100 * (12 / 30.48)),
    'SCALE_52': (100 * (16 / 30.48)),
    'SCALE_100': 100.0,
    'SCALE_1': 1.0,
}

CollisionModeProperty = EnumProperty(
    name='Collision',
    items=(
        ('AUTO',        "Auto",                 'Automatic based on model size.', 'MESH_UVSPHERE', 0),
        ('MESH',        "Mesh",                 'Concave mesh collider.', 'MESH_DATA', 1),
        ('HULL',        "Hull",                 'Convex hull collider.', 'MESH_ICOSPHERE', 2),
        ('BOX',         "Box",                  'Box collider.', 'MOD_WIREFRAME', 3),
        ('NONE',        "None",                 'No collision.', 'GHOST_DISABLED', 4),
    ),
    description='Type of collisions to use.',
    default='AUTO'
)

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
    collision_mode: CollisionModeProperty

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
    def draw(self, layout: UILayout, context: Context):
        compact = context.region.width < 500
        
        (layout if compact else layout.row()).prop(self, 'collision_mode', expand=True)
        
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

class ObjectData(PropertyGroup):
    visible: BoolProperty(name='Visible', default=True)
    collision_mode: CollisionModeProperty

    @staticmethod
    def save_to_gltf(self, data):
        match self.collision_mode:
            case 'AUTO': pass
            case mode: data['$collision'] = mode.lower()
        if not self.visible:
            data['$visible'] = False

    @staticmethod
    def draw(self, layout: UILayout, context: Context):
        # See also: draw_panel_object_list in tab_objects.py
        layout.prop(self, 'visible')
        (layout.row() if context.region.width > 500 else layout).prop(self, 'collision_mode', expand=True)

    def is_empty(self):
        return self.visible and self.collision_mode == 'AUTO'
    
    def reset(self):
        self.visible = True
        self.collision_mode = 'AUTO'

'''
class ModelData(CollectionData):
    name: StringProperty(name='Name', default='Model')
    collection: PointerProperty(name='Reference', type=Collection)
'''
    
class SceneData(PropertyGroup):
    #models: CollectionProperty(type=ModelData)
    models_active: bpy.props.IntProperty(default=-1)
    objects_active: bpy.props.IntProperty(default=-1)

    @property
    def data_path(self):
        return f'scene.sourcery_data'

    @staticmethod
    def get(context) -> 'SceneData':
        return context.scene.sourcery_data

###############################################################################

def register():
    bpy.types.Object.sourcery_data = bpy.props.PointerProperty(type=ObjectData)
    bpy.types.Scene.sourcery_data = bpy.props.PointerProperty(type=SceneData)
    bpy.types.Collection.sourcery_data = bpy.props.PointerProperty(type=CollectionData)

