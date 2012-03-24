#! /usr/bin/env python
"""
Auto generate test skeletons for all classes in a (list of) module(s).
"""
import inspect
import os
import sys
import imp
from optparse import OptionParser


def options():
    usage = '%prog command [options] module1.py [module2.py ...]'
    parser = OptionParser(usage)

    parser.add_option("-o", "--output", default="tests", metavar="DIR",
            help="output test skeletons to DIR")
    opts, args = parser.parse_args()
    return opts, args


def class_test_dict(tpl):
    name, obj = tpl
    test_dict = {}
    test_dict[name] = map(lambda m: m[0], inspect.getmembers(obj))
    return test_dict


def generate_skeleton(path):
    """
    Use inspect to find all classes and methods in a module.
    Path is a path to a module.
    Make and return a dict of {module:{class: [methods], methods: [methods]}
    """
    mod = imp.load_source('module', path)
    skeleton = {}
    classes = inspect.getmembers(mod, inspect.isclass)
    classes = filter(lambda o: inspect.getfile(o[1]).startswith(path), classes)
    functions = inspect.getmembers(mod, inspect.isfunction)
    functions = filter(lambda o: inspect.getfile(o[1]).startswith(path), functions)
    methods = inspect.getmembers(mod, inspect.ismethod)
    methods = filter(lambda o: inspect.getfile(o[1]).startswith(path), methods)

    skeleton['classes'] = map(class_test_dict, classes)
    skeleton['methods'] = map(lambda m: m[0], methods)
    skeleton['functions'] = map(lambda m: m[0], functions)
    path, module = os.path.split(path)
    return {module.replace('.py',''):skeleton}


def create_test_stubs(skeleton, test_dir):
    """
    Make the test directory if it doesn't exist then write out test stubs
    """
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    header = """#!/usr/bin/env python
'''
Tests generated with gen_tests.py https://github.com/drsm79/gen_tests
'''
import unittest
from %s import *
"""
    footer = """
if __name__ == '__main__':
    unittest.main()
"""
    class_template = """
class %sTest(unittest.TestCase):
    '''
    Generated test case.
    '''
    def setUp(self):
        pass

    def tearDown(self):
        pass
    """
    method_template = """
    def test_%s(self):
        pass
    """

    for module in skeleton:
        for k, v in module.items():
            f = open("%s/%s_t.py" % (test_dir, k),"w")
            f.write(header % k)
            for c in v['classes']:
                for cl, methods in c.items():
                    f.write(class_template % cl)
                    for method in methods:
                        f.write(method_template % method)

            f.write(footer)
            f.close()


if __name__ == '__main__':
    # opts holds the output directory, args are the modules to process
    opts, args = options()
    skeletons = map(generate_skeleton, args)
    create_test_stubs(skeletons, opts.output)
    print "Generated tests written to %s" % opts.output
