import sys
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


def remove_envvar_values(env, var, names):
    """
    Removes a list of defined variable values (e.g. CPPDEFINES)
    from an environment
    """
    defines = env[var]
    if isinstance(defines, dict):
        for n in names:
            try:
                defines.pop(n)
            except:
                pass
    else:  # should be a list
        for n in names:
            try:  # if it's simply a list element remove it
                defines.remove(n)
                continue
            except:
                pass

            for i, d in enumerate(defines):
                # lists can also contain tuples and dicts of defines
                if isinstance(d, tuple):
                    if d[0] == n:
                        defines.pop(i)
                        break
                elif isinstance(d, dict):
                    try:
                        d.pop(n)
                    except:
                        pass

    env.Replace(var=defines)


def set_debug_mode(env, is_debug):
    # import pdb
    # pdb.set_trace()
    if is_debug:
        env.Append(CCFLAGS=["-g"])
        env.Append(CPPDEFINES={'RF_OPTION_DEBUG': None})
        remove_envvar_values(env, 'CPPDEFINES', ['NDEBUG'])
    else:
        env.Append(CPPDEFINES={'NDEBUG': None})
        remove_envvar_values(env, 'CPPDEFINES', ['RF_OPTION_DEBUG'])
        remove_envvar_values(env, 'CCFLAGS', ['-g'])

    # if is_debug:
    #     env.AppendUnique(CCFLAGS=["-g"])
    #     env.AppendUnique(CPPDEFINES={'RF_OPTION_DEBUG': None})
    #     remove_envvar_values(env, 'CPPDEFINES', ['NDEBUG'])
    # else:
    #     env.Append(CPPDEFINES={'NDEBUG': None})
    #     remove_envvar_values(env, 'CPPDEFINES', ['RF_OPTION_DEBUG'])
    #     remove_envvar_values(env, 'CCFLAGS', ['-g'])
