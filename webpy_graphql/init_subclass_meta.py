from utils import props
from inspect import isclass

class InitSubclassMeta(type):
    def __init__(self, classname, baseclasses, attrs):
        _Meta = getattr(self, "GraphQLMeta", None)
        _meta_props = {}
        if _Meta:
            if isinstance(_Meta, dict):
                _meta_props = _Meta
            elif isclass(_Meta):
                _meta_props = props(_Meta)
            else:
                raise Exception("Meta have to be either a class or a dict. Received {}".format(_Meta))
        attrs = attrs.update(**_meta_props)
