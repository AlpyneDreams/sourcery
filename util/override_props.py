
def override_prop(cls, key, prop, base):
    # Copy keywords from base class prop
    for k in base.keywords:
        if k not in prop.keywords:
            prop.keywords[k] = base.keywords[k]
    return prop

def override_prop_recurse(cls, key, prop, root=True):
    # Check base classes
    for base in cls.__bases__:
        if key in base.__annotations__:
            return override_prop(cls, key, prop, base.__annotations__[key])
        
    # Recurse: check base of base classes
    for base in cls.__bases__:
        p = override_prop_recurse(base, key, prop, False)
        if p is not None:
            return p
    
    return prop if root else None

def override_props(cls):
    '''
    Decorator to override props from base classes
    without having to copy all the keywords
    '''
    for key in cls.__annotations__:
        prop = cls.__annotations__[key]
        if prop.__class__.__name__ == '_PropertyDeferred':
            cls.__annotations__[key] = override_prop_recurse(cls, key, prop)
    return cls

