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

# ---------------------------------------
# -- Setup environment for all projects
# ---------------------------------------
env['TARGET_SYSTEM'] = platform.system()

if env['TARGET_SYSTEM'] == 'Windows':
    env.Append(CPPDEFINES={'REFU_WIN32_VERSION': None})
    env.Append(CPPDEFINES={'_WIN32_WINNT': '0x501'})
elif env['TARGET_SYSTEM'] == 'Linux':
    env.Append(CPPDEFINES={'REFU_LINUX_VERSION': None})
    env.Append(CPPDEFINES={'_LARGEFILE64_SOURCE': None})
    env.Append(CPPDEFINES={'_GNU_SOURCE': None})
else:
    build_msg("Unsuported Operating System value \"{}\" "
              "Detected...Quitting".format(target_system), "Error")
    Exit(1)
env.Append(CPPDEFINES={'_FILE_OFFSET_BITS': 64})

# Debug or not?
if env['DEBUG'] != 0:
    env.Append(CCFLAGS=["-g"])
    env.Append(CPPDEFINES={'RF_OPTION_DEBUG': None})
else:
    env.Append(CPPDEFINES={'NDEBUG': None})


# if env['COMPILER'] == 'gcc':
#     env.Replace(tools=['gcc']])
# else:
#     build_msg('Only gcc is supported at the moment', 'Error', env)

# set compiler options irrespective of system
env.Append(CCFLAGS=['-static-libgcc', '-std=gnu99'])
env.Append(LIBS=['rt', 'pthread', 'm'])
env.Append(CPPDEFINES={'REFU_COMPILING': None})
env.Append(CPPPATH=os.path.join(env['CLIB_DIR'], 'include'))

# set some defines depending on options --
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

# These are variables from options.py which are True/False
# and will be added to the build as preprocessor defines (or not)
truevars_for_compile_time = [
    'NULLPTR_CHECKS',
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