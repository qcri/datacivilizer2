import sys
import os
import importlib

def import_all_files(dirname):
    modules = []
    for filename in os.listdir(dirname):
        filepath = os.path.join(dirname, filename)
        if os.path.isfile(filepath) and filepath.endswith('.py'):
            modules.append(import_file(filepath))
    return modules

def import_file(filepath):
    filename, _ = os.path.splitext(filepath)
    spec = importlib.util.spec_from_file_location(filename, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    dic = {'segments': 2,'a': 1}
    modules = import_all_files('splitter')
    for module in modules:
        intersect = dic.keys() & module.dic.keys()
        rest = module.dic.keys() - intersect
        print("Ok")
        for i in rest:
            dic.update({i: module.dic.get(i)})
        print(dic)
        print("Not ok")
        for i in intersect:
            print("Unable to add " + i + " from file " + module.__name__)
            print("Key already exist")


if __name__ == '__main__':
    main()