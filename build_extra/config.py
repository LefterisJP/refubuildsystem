from utils import build_msg


class Compiler:
    name = ""
    path = ""
    bin = ""
    dlink = ""
    slink = ""
    toolsValues = {}
    coptions = {}
    cflags = {}
    lflags = {}
    debug_flags = {}

    def __init__(self, name, path=0, bin=0, dlink=0, slink=0, coptions=0,
                 cflags=0, lflags=0, libs=0, toolsValues=0, debug_flags=0):
        self.name = name
        self.path = path
        self.bin = bin
        self.dlink = slink
        self.cflags = cflags
        self.lflags = lflags
        self.libs = libs
        self.toolsValues = toolsValues
        self.coptions = coptions
        self.debug_flags = debug_flags

# Defining the compilers
compilers = {}
# GCC
compilers['gcc'] = Compiler(
    name='gcc',
    coptions={
        'all': [
            '-static-libgcc',
            '-std=gnu99'  # gnu99 for c99 + gcc extensions (e.g: typeof)
        ],
        'Windows': [],
        'Linux': []},
    cflags={'all': {}, 'Windows': {}, 'Linux': {'_GNU_SOURCE': None}},
    lflags={'all': [], 'Windows': [], 'Linux': []},
    libs={'all': [], 'Windows': [], 'Linux': ['rt', 'pthread', 'm']},
    toolsValues={'Windows': ['mingw'], 'Linux': ['gcc']},
    debug_flags={'all': ["-g"], 'Windows': [], 'Linux': []}
)


def add_compiler_field(env, os, compiler_name, attribute, compiler_field):
    """
       Adds a particular compiler options field  to the build environment
       Depending on the build environment attribute that this affects
       the function either updates a dictionary or extends a list.

       --env: The build environment to extend/update
       --os: The operating system the library compiles in
       --compiler_name: The name of the compiler
       --attribute: The environment attribute we are changing. For example
         'CCFLAGS' or 'CPPDEFINES'
       --compiler_field: The compiler field we are using. For example
         'debug_flags' or 'libs'
    """
    cdict = compilers[compiler_name].__dict__
    l = ['all', os]
    for v in l:
        if cdict[compiler_field][v] != []:
            if isinstance(env[attribute], dict):
                env[attribute].update(cdict[compiler_field][v])
            else:
                env[attribute].extend(cdict[compiler_field][v])
