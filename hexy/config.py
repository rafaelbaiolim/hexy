"""
This module provides a handy wrapper class for the config file.
"""

import ConfigParser
import json
import os
import sys

class Config(object):
    """
    This class is a convenience wrapper around the hexy.cfg file.
    """
    def __init__(self, filename=None):
        self.filename = filename
        if filename is None:
            directory = os.path.dirname(__file__)
            directory = os.path.dirname(directory)
            self.filename = os.path.join(directory, 'hexy.cfg')
            filename = self.filename
            if not os.path.isfile(self.filename):
                filename = os.path.join(directory, 'hexy_default.cfg')
            
        if not os.path.isfile(filename):
            raise ValueError('%r is not a file' % filename)
        
        self.cfg_parser = ConfigParser.ConfigParser()
        self.cfg_parser.read(filename)
    
    def __setitem__(self, item, value):
        self.cfg_parser.set('default', item, json.dumps(value))

    def __getitem__(self, item):
        return json.loads(self.cfg_parser.get('default', item))

    def keys(self):
        return [k for k,v in self.cfg_parser.items('default')]

    def items(self):
        return [(k, json.loads(v))
                 for k, v in self.cfg_parser.items('default')]

    def save(self):
        with open(self.filename, 'w') as outfile:
            self.cfg_parser.write(outfile)

    def dumps(self):
        self.cfg_parser.write(sys.stdout)
        
