bl_info = {
    "name" : "Sourcery",
    "author" : "Alpyne",
    "description" : "Source Engine glTF tools.",
    "blender" : (4, 2, 0),
    "version" : (0, 0, 2),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

from . import auto_load

auto_load.init()

def register():
    auto_load.register()

def unregister():
    auto_load.unregister()
