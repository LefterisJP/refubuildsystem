import platform
import os


from build_extra.utils import build_msg
from build_extra.config import add_compiler_field
from build_extra.config import compilers
from build_extra.config import set_debug_mode


def CheckExecutable(context, executable):
    context.Message('Checking for existence of {} ...'.format(executable))
    path = WhereIs(executable)
    if not path:
        context.Result('FAIL!')
    else:
        context.Result('OK!')
    return path


def CheckCStatementExpr(context):
    context.Message('Checking if the C compiler supports '
                    'statements expressions ...')
    (rc, _) = context.TryRun(
        "int main(int argc, char **argv)"
        "{return ({ int x = argc; x == argc ? 0 : 1; });}",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('FAIL!')
        return False


def CheckCTypeOf(context):
    context.Message('Checking if the C compiler supports '
                    'the typeof() macro ...')
    rc = context.TryCompile(
        "#include <stddef.h>\n"
        "int main(int argc, char **argv)"
        "{typeof(int); return 0;}",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False


def CheckCAttributeCold(context):
    context.Message('Checking if the C compiler supports '
                    '__attribute__((cold)) ... ')
    rc = context.TryCompile(
        "static int __attribute__((cold)) func(int x) { return x; }",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False


def CheckCAttributeConst(context):
    context.Message('Checking if the C compiler supports '
                    '__attribute__((const)) ... ')
    rc = context.TryCompile(
        "static int __attribute__((const)) func(int x) { return x; }",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False


def CheckCAttributeUnused(context):
    context.Message('Checking if the C compiler supports '
                    '__attribute__((unused)) ... ')
    rc = context.TryCompile(
        "static int __attribute__((unused)) func(int x) { return x; }",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False


def CheckCBuiltinChooseExpr(context):
    context.Message('Checking if the C compiler supports '
                    '__builtin__choose__expr() ...')
    rc = context.TryCompile(
        "int main() {"
        "return __builtin_choose_expr(1, 0, \"garbage\");"
        "}",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False


def CheckCBuiltinTypesCompatibleP(context):
    context.Message('Checking if the C compiler supports '
                    '__builtin_types_compatible_p() ...')
    rc = context.TryCompile(
        "int main() {"
        "return __builtin_types_compatible_p(char *, int) ? 1 : 0;"
        "}",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False


def CheckCBuiltinConstantP(context):
    context.Message('Checking if the C compiler supports '
                    '__builtin_constant_p() ...')
    rc = context.TryCompile(
        "int main() {"
        "return __builtin_constant_p(1) ? 0 : 1;"
        "}",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False

def CheckCFlexibleArrayMembers(context):
    context.Message('Checking if the C compiler supports '
                    'flefible array members ...')
    rc = context.TryCompile(
        "struct foo { unsigned int x; int arr[]; };",
        ".c"
    )
    if rc == 1:
        context.Result('OK!')
        return True
    else:
        context.Result('Fail!')
        return False

def CheckEndianess(context):
    context.Message('Checking system byte order ...')
    (rc, output) = context.TryRun(
        """#include <stdio.h>\n
        #include <stdint.h>\n
        int littleEndianCheck(void)
        {
            union
            {
                uint32_t i;
                char c[4];
            } bint;
            bint.i = 42;
            return bint.c[0] == 42;
        }
        int main(int argc, char **argv)
        {printf("%d",littleEndianCheck());return 0;}""",
        '.c'
    )
    if rc != 1:
        build_msg("Could not compile/run endianess test program. "
                  "Should not happen")
        Exit(1)

    if output == "1":
        context.Result('Little Endian!')
        return 1
    else:
        context.Result('Big Endian!')
        return 0

Import('env')

conf = Configure(env, custom_tests={
    'CheckExecutable': CheckExecutable,
    'CheckCStatementExpr': CheckCStatementExpr,
    'CheckCTypeOf': CheckCTypeOf,
    'CheckEndianess': CheckEndianess,
    'CheckCAttributeCold': CheckCAttributeCold,
    'CheckCAttributeConst': CheckCAttributeConst,
    'CheckCAttributeUnused': CheckCAttributeUnused,
    'CheckCBuiltinChooseExpr': CheckCBuiltinChooseExpr,
    'CheckCBuiltinTypesCompatibleP': CheckCBuiltinTypesCompatibleP,
    'CheckCBuiltinConstantP': CheckCBuiltinConstantP,
    'CheckCFlexibleArrayMembers': CheckCFlexibleArrayMembers,
})

# Check for existence of check library for unit tests
if not conf.CheckLibWithHeader('check', 'check.h', 'c'):
    build_msg("Need libcheck for unit tests")
    Exit(1)

# Check if we have gperf
if not conf.CheckExecutable('gperf'):
    build_msg("Need 'gperf' for perfect hash table generation")
    Exit(1)

# Check for existence of libjson-c
if not conf.CheckLibWithHeader('json-c', 'json-c/json.h', 'c'):
    build_msg("Need libjson-c for exporting data to json format")
    Exit(1)

# Check if we have LLVM (check for llvm-config) TODO: find better way
if not conf.CheckExecutable('llvm-config'):
    build_msg("Need llvm. At the moment LLVM IR is the only backend")
    Exit(1)

# Check if we have antlr4
if not conf.CheckExecutable('antlr4'):
    env.SetDefault(has_antlr=False)
    if env['PARSER_IMPLEMENTATION'] == 'ANTLR':
        build_msg("Requested an antlr4 parser implementation but 'antlr4' "
                  "executable was not found in the system")
        Exit(1)
else:
    env.SetDefault(has_antlr=True)

# Check if we can run unit tests via valgrind
if not conf.CheckExecutable('valgrind'):
    build_msg("Will not run unit tests via valgrind", "Warning", env)
    env.SetDefault(has_valgrind=False)
else:
    env.SetDefault(has_valgrind=True)

# Check if the C compiler supports statement expressions
if not conf.CheckCStatementExpr():
    build_msg("Compiler not supported")
    Exit(1)
else:
    env.Append(CPPDEFINES="RF_HAVE_STATEMENT_EXPR")

# Check if the C compiler supports the typeof macro
if conf.CheckCTypeOf():
    env.Append(CPPDEFINES="RF_HAVE_TYPEOF")

# Check if the C compiler supports the cold attribute
if conf.CheckCAttributeCold():
    env['HAVE_ATTRIBUTE_COLD'] = True
else:
    env['HAVE_ATTRIBUTE_COLD'] = False

# Check if the C compiler supports the const function attribute
if conf.CheckCAttributeConst():
    env['HAVE_ATTRIBUTE_CONST'] = True
else:
    env['HAVE_ATTRIBUTE_CONST'] = False

# Check if the C compiler supports the unused function attribute
if conf.CheckCAttributeUnused():
    env['HAVE_ATTRIBUTE_UNUSED'] = True
else:
    env['HAVE_ATTRIBUTE_UNUSED'] = False

# Check if the C compiler supports the builtin choose expression
if conf.CheckCBuiltinChooseExpr():
    env['HAVE_BUILTIN_CHOOSE_EXPR'] = True
else:
    env['HAVE_BUILTIN_CHOOSE_EXPR'] = False

# Check if the C compiler supports the builtin types compatible predicate
if conf.CheckCBuiltinTypesCompatibleP():
    env['HAVE_BUILTIN_TYPES_COMPATIBLE_P'] = True
else:
    env['HAVE_BUILTIN_TYPES_COMPATIBLE_P'] = False

# Check if the C compiler supports the builtin constant predicate
if conf.CheckCBuiltinConstantP():
    env['HAVE_BUILTIN_CONSTANT_P'] = True
else:
    env['HAVE_BUILTIN_CONSTANT_P'] = False

# Check if the C compiler supports flexible array members
if conf.CheckCFlexibleArrayMembers():
    env['HAVE_FLEXIBLE_ARRAY_MEMBER'] = True
else:
    env['HAVE_FLEXIBLE_ARRAY_MEMBER'] = False


# Check the size of 'long' data type
env['LONG_SIZE'] = conf.CheckTypeSize('long')

# Check System endianess
if conf.CheckEndianess() == 1:
    env['ENDIANESS'] = 'LITTLE'
else:
    env['ENDIANESS'] = 'BIG'

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
set_debug_mode(env, env['DEBUG'] != 0)

# Define the cold attribute macro depending on existence or not
if env['HAVE_ATTRIBUTE_COLD']:
    env.Append(CPPDEFINES={"RFATTR_COLD": "__attribute__\(\(cold\)\)"})
else:
    env.Append(CPPDEFINES={"RFATTR_COLD": None})

# Define the const attribute macro depending on existence or not
if env['HAVE_ATTRIBUTE_CONST']:
    env.Append(CPPDEFINES={"RFATTR_CONST": "__attribute__\(\(const\)\)"})
else:
    env.Append(CPPDEFINES={"RFATTR_CONST": None})

# Define the unused attribute macro depending on existence or not
if env['HAVE_ATTRIBUTE_UNUSED']:
    env.Append(CPPDEFINES={"RFATTR_UNUSED": "__attribute__\(\(unused\)\)"})
else:
    env.Append(CPPDEFINES={"RFATTR_UNUSED": None})

# Define the flexible array member macro depending on existence
if env['HAVE_FLEXIBLE_ARRAY_MEMBER']:
    env.Append(CPPDEFINES={"RF_HAVE_FLEXIBLE_ARRAY_MEMBER": None})

# Define the endianess
if env['ENDIANESS'] == 'LITTLE':
    env.Append(CPPDEFINES={"RF_HAVE_LITTLE_ENDIAN": None})
else:
    env.Append(CPPDEFINES={"RF_HAVE_BIG_ENDIAN": None})

# if env['COMPILER'] == 'gcc':
#     env.Replace(tools=['gcc']])
# else:
#     build_msg('Only gcc is supported at the moment', 'Error', env)


# set compiler
env.Replace(CC=env['COMPILER'])
# set compiler specific options
if env['COMPILER'] == 'gcc':
    env.Append(CCFLAGS=['-static-libgcc', '-std=gnu99'])
# set compiler options irrespective of system
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
