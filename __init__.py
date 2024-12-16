bl_info = {
    "name" : "Sourcery",
    "author" : "Alpyne",
    "description" : "Source Engine glTF tools.",
    "blender" : (4, 2, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

GLTF_EXTENSION_NAME = "SRC_scene_data"

import bpy
from . import auto_load
from .data.scene import CollectionData, ObjectData

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
        if 'sourcery_data' not in collection:
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
        if 'sourcery_data' not in blender_object:
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
