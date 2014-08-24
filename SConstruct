import os

# read the configuration file variable and the extra objects
(config_file, clib_dir) = SConscript("build_system/args_before_config.py")

# read build options and add them to the environment
vars = SConscript('build_system/options.py', exports='config_file')

env = Environment(variables=vars,
                  toolpath=['build_system/site_scons/site_tools'],
                  tools=['default', 'check'])
env['CLIB_DIR'] = clib_dir
# configure the environment
env = SConscript('build_system/config.py', exports='env')
# Perform the system check
compiler = env['COMPILER']
env = SConscript('build_system/build_extra/systemcheck/systemcheck.py',
                 exports='env')

clib = SConscript(os.path.join(env['CLIB_DIR'], 'SConstruct'), exports='env')

# generate help text for the variables
Help(vars.GenerateHelpText(env))
