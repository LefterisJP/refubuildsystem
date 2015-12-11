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


def tryCompile(msg, program):
    def tryCompileFn(context):
        context.Message(
            "Checking if the C compiler supports {} ...".format(msg)
        )
        if context.TryCompile(program, '.c'):
            context.Result('OK!')
            return True
        else:
            context.Result('Fail!')
            return False
    return tryCompileFn


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


class configValue():
    def __init__(self, fn_name, msg, prog, envsetter_fn):
        self.fn_name = fn_name
        self.msg = msg
        self.prog = prog
        self.envsetter_fn = envsetter_fn

    def getTest(self):
        return self.fn_name, tryCompile(self.msg, self.prog)

    def runTest(self, conf, env):
        succ = getattr(conf, self.fn_name)()
        self.envsetter_fn(env, succ)

configMatrix = [
    configValue(
        'CheckCTypeOf', 'typeof() macro',
        '#include <stddef.h>\n'
        'int main(int argc, char **argv)'
        '{typeof(int); return 0;}',
        lambda env, succ: env.Append(CPPDEFINES="RF_HAVE_TYPEOF") if succ else None
    ),
    configValue(
        'CheckCAttributeCold',
        '__attribute__((cold))',
        'static int __attribute__((cold)) func(int x) { return x; }',
        lambda env, succ: env.Append(CPPDEFINES={"RFATTR_COLD": "__attribute__\(\(cold\)\)"}) if succ else env.Append(CPPDEFINES={"RFATTR_COLD": None})
    ),
    configValue(
        'CheckCAttributeConst',
        '__attribute__((const))',
        'static int __attribute__((const)) func(int x) { return x; }',
        lambda env, succ: env.Append(CPPDEFINES={"RFATTR_CONST": "__attribute__\(\(const\)\)"}) if succ else env.Append(CPPDEFINES={"RFATTR_CONST": None})
    ),
    configValue(
        'CheckCAttributeUnused',
        '__attribute__((unused))',
        'static int __attribute__((unused)) func(int x) { return x; }',
        lambda env, succ: env.Append(CPPDEFINES={"RFATTR_UNUSED": "__attribute__\(\(unused\)\)"}) if succ else env.Append(CPPDEFINES={"RFATTR_UNUSED": None})
    ),
    configValue(
        'CheckCBuiltinChooseExpr',
        '__builtin__choose__expr()',
        'int main() { return __builtin_choose_expr(1, 0, \"garbage\"); }',
        lambda env, succ: env.Append(CPPDEFINES="RF_HAVE_BUILTIN_CHOOSE_EXPR") if succ else None
    ),
    configValue(
        'CheckCBuiltinTypesCompatibleP',
        '__builtin_types_compatible_p',
        'int main(){return __builtin_types_compatible_p(char *, int) ? 1 : 0;}',
        lambda env, succ: env.Append(CPPDEFINES="RF_HAVE_BUILTIN_TYPES_COMPATIBLE_P") if succ else None
    ),
    configValue(
        'CheckCBuiltinConstantP',
        '__builtin_constant_p',
        'int main() { return __builtin_constant_p(1) ? 0 : 1; }',
        lambda env, succ: env.Append(CPPDEFINES="RF_HAVE_BUILTIN_CONSTANT_P") if succ else None
    ),
    configValue(
        'CheckCFlexibleArrayMembers',
        'flexible array members',
        'struct foo { unsigned int x; int arr[]; };',
        lambda env, succ: env.Append(CPPDEFINES="RF_HAVE_FLEXIBLE_ARRAY_MEMBER") if succ else None
    )
]

testsDict = dict([v.getTest() for v in configMatrix])
testsDict.update({
    'CheckEndianess': CheckEndianess,
    'CheckExecutable': CheckExecutable,
    'CheckCStatementExpr': CheckCStatementExpr,
})
conf = Configure(env, custom_tests=testsDict)


# Check for existence of check library for unit tests
if not conf.CheckLibWithHeader('check', 'check.h', 'c'):
    build_msg("Need libcheck for unit tests")
    Exit(1)

# Check if we have graphviz
if conf.CheckLibWithHeader('gvc', 'graphviz/gvc.h', 'c'):
    env.SetDefault(has_graphviz=True)
else:
    env.SetDefault(has_graphviz=False)

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

# Check if we have antlr3
if not conf.CheckExecutable('antlr3'):
    env.SetDefault(has_antlr=False)
else:
    env.SetDefault(has_antlr=True)

# Check if we have pcre2
# Refer to: http://www.pcre.org/current/doc/html/
if not conf.CheckExecutable('pcre2-config'):
    build_msg("Did not find PCRE2(Perl Compatible Regular Expressions) library",
              "Warning", env)
    env.SetDefault(has_pcre2=False)
else:
    env.SetDefault(has_pcre2=True)

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

# Check the size of 'long' data type
env['LONG_SIZE'] = conf.CheckTypeSize('long')

# Check System endianess
if conf.CheckEndianess() == 1:
    env.Append(CPPDEFINES={"RF_HAVE_LITTLE_ENDIAN": None})
else:
    env.Append(CPPDEFINES={"RF_HAVE_BIG_ENDIAN": None})

# run all other config tests
for v in configMatrix:
    v.runTest(conf, env)

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

if env['ADDRESS_SANITIZER']:
    env.Append(CCFLAGS=['-fsanitize=address'])
    env.Append(LINKFLAGS=['-fsanitize=address'])

# set compiler
if env['COMPILER'] == 'gcc':
    env.Replace(CC='gcc')
    env.Replace(CXX='g++')
    env.Append(CCFLAGS=['-static-libgcc', '-std=gnu99'])
elif env['COMPILER'] == 'clang':
    env.Replace(CC='clang')
    env.Replace(CXX='clang++')
else:
    build_msg("Unsuported Compiler \"{}\" "
              "Requested...Quitting".format(env['COMPILER']), "Error")
    Exit(1)

# set compiler options irrespective of compiler
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
