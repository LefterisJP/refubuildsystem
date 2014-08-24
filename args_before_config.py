import ast
import os

args_before = Variables()
args_before.Add(PathVariable(
    'CONFIG_FILE',
    'This is the path to the configuration file where all the variables'
    'will be read from.',
    os.path.abspath(os.path.join(os.pardir, 'build_system', 'refu.config')),
    PathVariable.PathIsFile))

# Not Adding as PathVariable, since it may not exist, and as such we need to
# pull the repo
args_before.Add(
    'CLIB_DIR', 'The root directory of the refu C library.'
    ' Absolute value',
    os.path.abspath(os.path.join(os.pardir, 'clib'))
)

# return the variables, and make sure the paths are absolute
temp = Environment(variables=args_before)
config_file = os.path.abspath(temp['CONFIG_FILE'])
Return('config_file')
