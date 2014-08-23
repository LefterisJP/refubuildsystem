import ast
import os

args_before = Variables()
args_before.Add(PathVariable(
    'CONFIG_FILE',
    'This is the path to the configuration file where all the variables'
    'will be read from.',
    os.path.abspath(os.path.join(os.pardir, 'build_system', 'refu.config')),
    PathVariable.PathIsFile))

args_before.Add(
    PathVariable(
        'CLIB_DIR', 'The root directory of the refu C library.'
        ' Absolute value',
        os.path.abspath(os.path.join(os.pardir, 'clib')),
        PathVariable.PathIsDir
    )
)

# return the variables, and make sure the paths are absolute
temp = Environment(variables=args_before)
config_file = os.path.abspath(temp['CONFIG_FILE'])
clib_dir = os.path.abspath(temp['CLIB_DIR'])

Return('config_file clib_dir')
