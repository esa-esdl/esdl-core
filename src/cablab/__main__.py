import sys


def main(args=None):
    if not args:
        args = sys.argv[1:]
    print(">> Welcome to the CAB-LAB CLI! <<")
    print("args =", args)
    # Do argument parsing here (eg. with argparse) and anything else
    # you want your project to do.
    import cablab.core

    converter_classes, transformer_methods = cablab.core.load_all_extensions()

    print('converter_classes =', converter_classes)
    print('transformer_methods =', transformer_methods)

    for converter_class in converter_classes:
        converter_object = converter_class()
        for file in args:
            converter_object.run(file)

    for transformer_method in transformer_methods:
        for file in args:
            transformer_method(file)


# check if I'm invoked as script
if __name__ == "__main__":
    main()
