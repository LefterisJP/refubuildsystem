import platform
import os


from build_extra.utils import build_msg
from build_extra.config import add_compiler_field
from build_extra.config import compilers


def CheckExecutable(context, executable):
    context.Message('Checking for existence of {} ...'.format(executable))
    path = WhereIs(executable)
    if not path:
        context.Result('FAIL!')
    else:
        context.Result('OK!')
    return path

Import('env')

conf = Configure(env, custom_tests={'CheckExecutable': CheckExecutable})

# Check for existence of check library for unit tests
if not conf.CheckLibWithHeader('check', 'check.h', 'c'):
    build_msg("Need libcheck for unit tests")
    Exit(1)

# Check if we can run unit tests via valgrind
if not conf.CheckExecutable('valgrind'):
    build_msg("Will not run unit tests via valgrind", "Warning", env)
    env.SetDefault(has_valgrind=False)
else:
    env.SetDefault(has_valgrind=True)
env = conf.Finish()


# --setup some other stuff
target_system = platform.system()
env['TARGET_SYSTEM'] = target_system
compilerdir = env['COMPILER_DIR']
compiler_name = env['COMPILER']
# add general options and defines for the refu project
if target_system == 'Windows':
    env.Append(CPPDEFINES={'REFU_WIN32_VERSION': None})
    env.Append(CPPDEFINES={'_WIN32_WINNT': '0x501'})
elif target_system == 'Linux':
    env.Append(CPPDEFINES={'REFU_LINUX_VERSION': None})
    env.Append(CPPDEFINES={'_LARGEFILE64_SOURCE': None})
else:
    build_msg("Unsuported Operating System value \"{}\" "
              "Detected...Quitting".format(target_system), "Error")
    Exit(1)
env.Append(CPPDEFINES={'_FILE_OFFSET_BITS': 64})

# add debug symbols to the compiler if Debug is not 0
if env['DEBUG'] != 0:
    add_compiler_field(env, target_system, compiler_name, 'CCFLAGS', 'debug_flags')
    env.Append(CPPDEFINES={'RF_OPTION_DEBUG': None})
else:
    env.Append(CPPDEFINES={'NDEBUG': None})

# figure out the tools value
env.Replace(tools=compilers[compiler_name].toolsValues[target_system])
# if a compiler dir has been given then use that.
# Not given is the '.' directory
if compilerdir != '.':
    build_msg("Using \"{}\" as the compiler directory as instructed"
              "".format(compilerdir), 'Info', env)
    env.Replace(ENV={'PATH': compilerdir})

# set compiler defines, and compile and link options
add_compiler_field(env, target_system, compiler_name, 'CCFLAGS', 'coptions')
add_compiler_field(env, target_system, compiler_name, 'CPPDEFINES', 'cflags')
# it is possible that env['LIBS'] does not exist yet here and since
# inside add_compiler_field I am not using env.Append() I need to make
# sure that there are no key errors by doing this:
env['LIBS'] = []
add_compiler_field(env, target_system, compiler_name, 'LIBS', 'libs')


# setting needed flags, paths and defines
env.Append(CPPDEFINES={'REFU_COMPILING': None})
env.Append(CPPPATH=os.path.join(env['CLIB_DIR'], 'include'))
env.Append(CCFLAGS=env['COMPILER_FLAGS'])
env.Append(LINKFLAGS=env['LINKER_SHARED_FLAGS'])





# -- set some defines depending on options --
# These are variables from variables.py which contain a value
# and will be added to the build as preprocessor defines
vars_for_compile_time = [
    'FGETS_READ_BYTESN',
    'STRINGX_CAPACITY_MULTIPLIER',
    'DYNAMICARRAY_CAPACITY_MULTIPLIER',
    'LOCALSTACK_MEMORY_SIZE',
    'THREADX_MSGQUEUE_SIZE',
    'HASHMAP_LOAD_FACTOR',
    'LOG_LEVEL_DEFAULT',
    'LOG_BUFFER_SIZE',
    'WORKER_SLEEP_MICROSECONDS',
    'MAX_WORKER_THREADS'
]

# These are variables from variables.py which are True/False
# and will be added to the build as preprocessor defines (or not)
truevars_for_compile_time = [
    'INSANITY_CHECKS',
    'SAFE_MEMORY_ALLOCATION',
    'DEBUG',
    'TEXTFILE_ADD_BOM'
]

# add to the environment all the compile time vars that are just defs
for v in truevars_for_compile_time:
    if env[v]:
        var_name = "RF_OPTION_{}".format(v)
        build_msg("Adding \"{}\" to the build environment".format(
            var_name), 'Info', env)
        env.Append(CPPDEFINES={var_name: None})
# add to the environment all the compile time vars with a value
for v in vars_for_compile_time:
    var_name = "RF_OPTION_{}".format(v)
    build_msg("Adding \"{}={}\" to the build environment".format(
        var_name, env[v]), 'Info', env)
    env.Append(CPPDEFINES={'RF_OPTION_{}'.format(v):
                           env[v]})



Return('env')
