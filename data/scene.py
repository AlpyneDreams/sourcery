import bpy
from bpy.types import PropertyGroup, UIList, Collection
from bpy.props import StringProperty, PointerProperty, CollectionProperty, FloatProperty
from .surfaceprops import SurfaceProp

class CollectionData(PropertyGroup):
    collision: PointerProperty(name='Collision', type=Collection)
    surfaceprops: CollectionProperty(type=SurfaceProp)
    surfaceprop: StringProperty(name='Surface Property', default='default')
    scale: FloatProperty(name='Scale', default=0.4) # TODO: Either pre-scale the mesh or embed scale value

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

###############################################################################

def register():
    bpy.types.Scene.sourcery_data = bpy.props.PointerProperty(type=SourceData)
    bpy.types.Collection.sourcery_data = bpy.props.PointerProperty(type=CollectionData)

