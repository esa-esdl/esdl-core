from pkg_resources import iter_entry_points

converter_classes = []
for entry_point in iter_entry_points(group='cablab.converter.classes', name=None):
    converter_class = entry_point.load()
    converter_classes.append(converter_class)

transformer_methods = []
for entry_point in iter_entry_points(group='cablab.transformer.methods', name=None):
    transformer_method = entry_point.load()
    transformer_methods.append(transformer_method)

print('converter_classes =', converter_classes)
print('transformer_methods =', transformer_methods)

for converter_class in converter_classes:
    converter_object = converter_class()


for transformer_method in transformer_methods:
    result = transformer_method()