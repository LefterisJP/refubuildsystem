import os

# read the configuration file variable and the extra objects
config_file = SConscript("build_system/args_before_config.py")

# read build options and add them to the environment
vars = SConscript('build_system/options.py', exports='config_file')

env = Environment(variables=vars,
                  toolpath=['build_system/site_scons/site_tools'],
                  tools=['default', 'check', 'updaterepo'])

# - Targets for updating repositories
update_clib = env.UpdateRepo(
    target="update_clib",
    source=Dir(env['CLIB_DIR']))
Alias('update_clib', update_clib)

update_lang = env.UpdateRepo(
    target="update_lang",
    source=Dir(env['LANG_DIR']))
Alias('update_lang', update_lang)


# configure the environment
env = SConscript('build_system/config.py', exports='env')
# Perform the system check
env = SConscript('build_system/build_extra/systemcheck/systemcheck.py',
                 exports='env')


# Build the various repos
if os.path.lexists(env['CLIB_DIR']):
    clib_static = SConscript(
        os.path.join(env['CLIB_DIR'], 'SConstruct'),
        exports='env')

if os.path.lexists(env['LANG_DIR']):
    lang = SConscript(
        os.path.join(env['LANG_DIR'], 'SConstruct'),
        exports='env clib_static')
    Depends(lang, 'clib_static')
    env.Alias('refu', lang)


# Default(clib)
# generate help text for the variables
Help(vars.GenerateHelpText(env))
