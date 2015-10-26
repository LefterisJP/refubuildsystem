import os
from build_extra.utils import build_msg
# -- Get the user provided options --

allowedCompilers = ['gcc', 'clang', 'tcc', 'msvc']
Import('config_file')


def checkCompilerValue(key, value, environment):
    """A function to validate the compiler value"""
    if (value is not None and value not in allowedCompilers):
        print("**ERROR** The given compiler name is not supported. Please "
              "provide one of the supported compiler values")
        print(" ,".join(allowedCompilers))
        Exit(-1)
    if value is None:
        print("No compiler was given. Defaulting to GCC")
        value = 'gcc'
    return True


def sources_string_to_list(s):
    if s == "":
        build_msg("No test sources provided.", "Error")
        Exit(-1)
    sources = s.split(',')
    return sources

# Initialize the variables object
vars = Variables(config_file)


# Paths - Not Adding as PathVariable, since they may not exist,
# and as such we need to pull their respective repos
vars.Add(
    'CLIB_DIR', 'The root directory of the refu C library.'
    ' Absolute value',
    os.path.abspath(os.path.join(os.pardir, 'clib'))
)

vars.Add(
    'LANG_DIR', 'The root directory of the language core.'
    ' Absolute value',
    os.path.abspath(os.path.join(os.pardir, 'core'))
)

vars.Add(
    'BUILD_SYSTEM_DIR', 'The root directory of refu build system.'
    ' Absolute value',
    os.path.abspath(os.path.join(os.pardir, 'build_system'))
)

vars.Add(
    'DOCUMENTATION_DIR', 'The root directory of refu documentation.'
    ' Absolute value',
    os.path.abspath(os.path.join(os.pardir, 'documentation'))
)

vars.Add('COMPILER',
         'The compiler name. Allowed values are: {}'.format(
             ','.join(allowedCompilers)
         ),
         'gcc', validator=checkCompilerValue)

vars.Add(
    BoolVariable('ADDRESS_SANITIZER',
                 'If \'yes\' then the project will be build with address '
                 'sanitizing option on.',
                 'no'))

vars.Add(
    PathVariable('COMPILER_DIR', 'The directory of the compiler. Will try'
                 ' to search here if scons can\'t find the requested compiler'
                 ' automatically. Should be an absolute path', '.',
                 PathVariable.PathIsDir))

vars.Add(
    PathVariable('OBJ_DIR', 'The name of the directory to use (will create'
                 ' if it does not already exist)for dumping the object files.'
                 ' Its parent directory is the refu directory', 'obj',
                 PathVariable.PathIsDirCreate))


# ------------------------------------------
# ---------- CLIB Related options ----------
# ------------------------------------------
vars.Add('CLIB_OUT_NAME', 'The name of the output for the c library.'
         ' Prefix or suffixed will be automatically added by '
         'SCONS where needed', 'refu')

vars.Add(
    ListVariable('REFU_MODULES', 'The modules of refu library that you want'
                 ' to build. Accepted values are either ALL or a '
                 'comma-separated list of the names of the modules you '
                 'want to compile', ['ALL'],
                 [
                     'ALL',
                     'STRING',
                     'IO', 'TEXTFILE',
                     'DATA_STRUCTURES',
                     'INTRUSIVE_LIST',
                     'BINARY_ARRAY',
                     'TIME',
                     'PARALLEL',
                     'SYSTEM'])
)

vars.Add(
    EnumVariable('LOG_LEVEL_DEFAULT',
                 'This option specifies the default logging level'
                 'that the log system will be using.', 'LOG_ERROR',
                 allowed_values=(
                     'LOG_EMERGENCY',
                     'LOG_ALERT',
                     'LOG_CRITICAL',
                     'LOG_ERROR',
                     'LOG_WARNING',
                     'LOG_NOTICE',
                     'LOG_INFO',
                     'LOG_DEBUG',
                 ))
)

vars.Add('LOG_BUFFER_SIZE', 'The initial size to allocate for the Logging '
         'system buffer', 4096)


vars.Add('DEBUG', "This option determines if this will be a Debug Build (0"
         "or 1), and if more than 1 it can indicate a different debug level",
         0)

vars.Add(
    BoolVariable('SAFE_MEMORY_ALLOCATION',
                 'If \'yes\' then the malloc and calloc'
                 ' calls of the library check for failure and in case of '
                 'failure log an error and exit the process.If \'no\' then '
                 'malloc and calloc are called normally.Accepted values '
                 'for this option are \'yes\' and \'no\'.',
                 'no'))

vars.Add(
    BoolVariable('NULLPTR_CHECKS',
                 'If \'yes\' then the library\'s null pointers checks will be '
                 'activated. Some tests rely on this to be active since there '
                 'are some functions tested even with invalid input',
                 'yes'))

vars.Add('FGETS_READ_BYTESN', 'This option is the number of bytes that will '
         'be read each time by the library\'s version of fgets. Must be a '
         'positive integer number.', 512)

vars.Add('STRINGX_CAPACITY_MULTIPLIER', 'This is the multiplier by which a'
         ' StringX\'s buffer will get allocated/reallocated by when there'
         ' is a need for buffer extension. Also when the StringX gets '
         'initialized this is how much bigger than the given String the '
         'buffer will be. Must be a positive integer.', 2)

vars.Add('DYNAMICARRAY_CAPACITY_MULTIPLIER', 'This is the multiplier by which '
         'a Dynamic array\'s buffer will get allocated/reallocated by when'
         ' there is a need for buffer extension. Also when the List gets '
         'initialized this is how much bigger than the given initial size '
         'the buffer will be. Must be a positive integer.', 2)

vars.Add('LOCALSTACK_MEMORY_SIZE',
         'This is the default size in bytes of the main'
         ' thread\'s Local Stack of the Refu Library. All objects that are'
         ' initialized as temporary objects such as with the  RFS_() macro'
         ' or the RFXML_() macro are initialized in this stack. Make sure '
         'to provide a big enough value so that no overflow happens for your'
         ' program. The default value is used if '
         'no specific value is provided at rf_init()', 1048576)

vars.Add('MAX_WORKER_THREADS',
         'The maximum number of worker threads we can have', 32)

vars.Add('WORKER_SLEEP_MICROSECONDS',
         'The amount of time in microseconds for worker threads to sleep '
         'while waiting for jobs to appears on their queues', 1000)

vars.Add(
    BoolVariable('TEXTFILE_ADD_BOM', 'This control whether to add a '
                 'BOM(ByteOrderMark) at the beginning of newly created '
                 'TextFiles. Provides \'yes\' to add and \'no\', not to. ',
                 'yes'))

vars.Add('THREADX_MSGQUEUE_SIZE', 'This option affects The extended thread'
         ' objects RF_ThreadX, and it denotes what should the default value'
         ' of the size of the message queue of a newly created RF_ThreadX.'
         'You still have the option to change that in run-rime through the '
         'initialization functions but if a value is not provided this will '
         'be the default value.', 10)

vars.Add('HASHMAP_LOAD_FACTOR', 'This option determines when the hashmap '
         'will rehash all of its slots. When during a hashmap insertion '
         'the ratio of occupied slots over the map\'s size is greater '
         'than this value then rehashing of the map will take place.',
         0.7)


# ------------------------------------------
# ------------ refulang options ------------
# ------------------------------------------

vars.Add(
    EnumVariable(
        'VERBOSE_LEVEL_DEFAULT',
        'The default verbosity level. Should range between 1 and 4',
        '1',
        allowed_values=('1', '2', '3', '4')))

vars.Add(
    EnumVariable('PARSER_IMPLEMENTATION',
                 'Specify the parser implementation to use in the font end',
                 'RECURSIVE_DESCENT',
                 allowed_values=(
                     'RECURSIVE_DESCENT',
                     'ANTLR'
                 ))
)

vars.Add(
    EnumVariable('LANG_BACKEND',
                 'Specify the backend of the compiler to use',
                 'LLVM',
                 allowed_values=(
                     'LLVM'
                 ))
)

vars.Add('INFO_CTX_BUFF_INITIAL_SIZE',
         'The initial size in bytes of the info context buffer. This is the '
         'buffer used by the compiler to store all messages', 512)

vars.Add('INPUT_FILE_BUFF_INITIAL_SIZE',
         'The initial size in bytes of the buffer that will hold the input of each file', 1024)

vars.Add('INPUT_STRING_STARTING_LINES',
         'The initial number of lines for the line indexer of the buffered input file', 256)

# ------------------------------------------
# ---------- unit testing options ----------
# ------------------------------------------
vars.Add(
    BoolVariable(
        'TEST_VIA_VALGRIND',
        'If true, then tests will also be ran via valgrind',
        'True')
)

vars.Add(
    EnumVariable(
        'TEST_OUTPUT', 'This options determines the way that the '
        'outputs of the tests shall be shown. Since we are using Check '
        'as the unit testing framework here is an explanation of the possible '
        'values: '
        'http://check.sourceforge.net/doc/check_html/check_8.html#Index',
        'CK_NORMAL',
        allowed_values=(
            'CK_SILENT',
            'CK_MINIMAL',
            'CK_NORMAL',
            'CK_VERBOSE'
        )))


vars.Add(
    BoolVariable(
        'TEST_FORK', 'This options determines whether the tests will '
        'run in their own address space. Change it to no only if you need to '
        'debug them with GDB',
        True)
)

vars.Add(
    'TEST_CASE',
    'If given then this is the test case from the unit tests target to run',
    '')

vars.Add(
    'TEST_SUITE',
    'If given then this is the test suite from the unit tests target to run',
    '')


Return('vars')
