import os
import yaml
import glob

from source.build import Build
from source.target import Target
from source.script import Script
from source.colors import colors

# Global helper functions
def split(d, pr, defns):
    prop = d[pr]
    if isinstance(prop, str):
        prop = prop.split(', ')
    
    for i in range(len(prop)):
        if prop[i] in defns:
            prop[i] = defns[prop[i]]

    return prop

def concat(ldicts):
    out = {}
    for d in ldicts:
        out.update(d)
    return out

# Config class
class Config:
    # Constructor takes no argument
    def __init__(self):
        # Initialize targets to empty
        self.targets = {}

        # Get config files from current dir
        configs = []
        for root, _, files in os.walk('.'):
            for file in files:
                if file == 'smake.yaml':
                    configs.append(os.path.join(root, file))

        # Load all files from the current directory
        for file in configs:
            self.load_file(file)

    # Reads definitions from variables like sources, includes, etc.
    def load_definitions(self, smake):
        # TODO: error on duplicate definition

        # Output dictionary
        defns = {}
        
        # Load sources
        if 'sources' in smake:
            for sgroup in smake['sources']:
                defns.update(sgroup)
        
        # Return the dictionary
        return defns
    
    # Create a build object
    def load_build(self, build, defns):
        name = list(build)[0]
        properties = {}
        for d in build[name]:
            properties.update(d)

        # Preprocess properties
        sources = split(properties, 'sources', defns)

        # Optional properties
        includes = []
        libraries = []
        flags = []

        if 'includes' in properties:
            includes = split(properties, 'includes', defns)
        
        if 'libraries' in properties:
            libraries = split(properties, 'libraries', defns)
        
        if 'flags' in properties:
            flags = split(properties, 'flags', defns)

        # Create and return the object
        return Build('smake-build', name, sources, includes, libraries, flags)

    def load_all_builds(self, smake, defns):
        # TODO: check that builds actually exists

        blist = {}
        for b in smake['builds']:
            name = list(b)[0]
            build = self.load_build(b, defns)
            blist.update({name: build})
        
        return blist

    def load_target(self, target, blist, defns):
        name = list(target)[0]
        properties = {}
        for d in target[name]:
            properties.update(d)
        
        # Preprocess properties
        modes = split(properties, 'modes', defns)

        # Gets builds and postbuilds
        builds = concat(properties['builds'])

        postbuilds = {}
        if 'postbuild' in properties:
            postbuilds = concat(properties['postbuild'])

        # Preprocess predefined things
        # TODO: separate methods
        for b in builds:
            bname = builds[b]

            if bname in blist:
                builds[b] = blist[bname]
                builds[b].set_target(name)
            # TODO: errir handling here
        
        # If the postbuild is a string, then convert to Script
        for pe in postbuilds:
            pname = postbuilds[pe]

            if pname in defns:
                postbuilds[pe] = defns[pname]
            else:
                postbuilds[pe] = Script(pname)

        return Target(name, modes, builds, postbuilds)

    def load_all_targets(self, smake, builds, defns):
        tlist = {}
        for t in smake['targets']:  # TODO: error handle presence of targets
            name = list(t)[0]
            target = self.load_target(t, builds, defns)
            tlist.update({name: target})

        return tlist

    def load_file(self, file):
        # Open and read the config
        with open(file, 'r') as file:
            smake = yaml.safe_load(file)
        
        # Load the definitions
        defns = self.load_definitions(smake)

        # Load all builds
        builds = self.load_all_builds(smake, defns)

        # Load all targets
        self.targets = self.load_all_targets(smake, builds, defns)
    
    # Run the correct target
    def run(self, target, mode = 'default'):
        # Check if the target is valid
        if target in self.targets:
            self.targets[target].run(mode)
        else:
            print(colors.FAIL + f'No target {target} found.' + \
                ' Perhaps you meant one of the following:' + colors.ENDC)
            for valid in list(self.targets.keys()):
                print(colors.PURPLE + f'\t{valid}' + colors.ENDC)