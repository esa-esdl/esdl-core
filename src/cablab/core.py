from pkg_resources import iter_entry_points


def load_all_extensions():
    converter_classes = []
    for entry_point in iter_entry_points(group='cablab.converter.classes', name=None):
        converter_class = entry_point.load()
        # TODO: Check that it is a class type and that it has our expected interface
        converter_classes.append(converter_class)

    transformer_methods = []
    for entry_point in iter_entry_points(group='cablab.transformer.methods', name=None):
        transformer_method = entry_point.load()
        # TODO: Check that it is a callable type and that it has our expected parameters
        transformer_methods.append(transformer_method)

    return converter_classes, transformer_methods
