bl_info = {
    "name" : "Sourcery",
    "author" : "Alpyne",
    "description" : "Source Engine glTF tools.",
    "blender" : (4, 2, 0),
    "version" : (1, 1, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

GLTF_EXTENSION_NAME = "SRC_scene_data"

import bpy
import bpy.types
from . import auto_load
from .data.scene import CollectionData, ObjectData
import io_scene_gltf2.io.com.gltf2_io as gltf2

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()

# glTF Extension Handler
class glTF2ExportUserExtension:

    def __init__(self):
        # We need to wait until we create the gltf2UserExtension to import the gltf2 modules
        # Otherwise, it may fail because the gltf2 may not be loaded yet
        from io_scene_gltf2.io.com.gltf2_io_extensions import Extension
        self.Extension = Extension

    def gather_gltf_extensions_hook(self, gltf2_plan, export_settings):

        collection_id = export_settings['gltf_collection']
        if not collection_id:
            return # Not a collection export

        collection = bpy.data.collections.get((collection_id, None))
        if not collection:
            return print(f"[Sourcery] Error: Failed to find collection '{collection_id}'")
        
        # Get Sourcery data
        if not hasattr(collection, 'sourcery_data'):
            return print(f"[Sourcery] Error: Collection '{collection_id}' has no Sourcery data")
        data = collection.sourcery_data
        if not data:
            return print(f"[Sourcery] Error: Collection '{collection_id}' has no Sourcery data")

        # Save to glTF
        extension = {}
        CollectionData.save_to_gltf(data, extension)

        if gltf2_plan.extensions is None:
            gltf2_plan.extensions = {}
        gltf2_plan.extensions[GLTF_EXTENSION_NAME] = self.Extension(
            name=GLTF_EXTENSION_NAME,
            extension=extension,
            required=False
        )

    def gather_node_hook(self, gltf2_node, blender_object, export_settings):
        if not hasattr(blender_object, 'sourcery_data'):
            return
    
        data = blender_object.sourcery_data
        extension = {}
        ObjectData.save_to_gltf(data, extension)

        if extension:
            gltf2_node.extensions[GLTF_EXTENSION_NAME] = self.Extension(
                name=GLTF_EXTENSION_NAME,
                extension=extension,
                required=False
            )

    def gather_mesh_hook(self, gltf2_mesh: gltf2.Mesh, blender_mesh: bpy.types.Mesh, blender_object, vertex_groups, modifiers, materials, export_settings):
        # Get number of color attributes
        num_color_attrs = len(blender_mesh.color_attributes)

        # For each primitive
        prim: gltf2.MeshPrimitive
        for prim in gltf2_mesh.primitives:
            # Check if we have a fake COLOR_0 (glTF exporter loves to add this)
            has_fake_color0 = num_color_attrs < sum(1 for attr in prim.attributes if attr.startswith('COLOR_'))

            # For each color attribute
            for i in range(num_color_attrs):
                colors = blender_mesh.color_attributes[i]

                # Assign color attribute names to glTF accessors
                attr = f'COLOR_{i+1}' if has_fake_color0 else f'COLOR_{i}'
                if attr in prim.attributes:
                    prim.attributes[attr].name = colors.name
