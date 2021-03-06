import os

# read the configuration file variable and the extra objects
config_file = SConscript("build_system/args_before_config.py")

# read build options and add them to the environment
vars = SConscript('build_system/options.py', exports='config_file')

env = Environment(variables=vars,
                  toolpath=['build_system/site_scons/site_tools'],
                  tools=[
                      'default',
                      'check',
                      'updaterepo',
                      'gperf',
                      'clangformat'
                  ])

# - Targets for updating repositories
update_clib = env.UpdateRepo(
    target="update_clib",
    source=Dir(env['CLIB_DIR']))
Alias('update_clib', update_clib)

update_lang = env.UpdateRepo(
    target="update_lang",
    source=Dir(env['LANG_DIR']))
Alias('update_lang', update_lang)

update_build_system = env.UpdateRepo(
    target="update_build_system",
    source=Dir(env['BUILD_SYSTEM_DIR']))
Alias('update_build_system', update_build_system)

update_documentation = env.UpdateRepo(
    target="update_documentation",
    source=Dir(env['DOCUMENTATION_DIR']))
Alias('update_documentation', update_documentation)

# very ugly way to update all repos. Gotta use something better
update_all = env.UpdateRepo(
    target="update_all",
    # source=Dir('.'))
    source='build_system/SConstruct')  # random file to act as target, is ugly
Alias('update_all', update_all)

# - Targets for style formatting the repositories
format_clib = env.ClangFormat(
    target="format_clib",
    source=Dir(env['CLIB_DIR']))
Alias('format_clib', format_clib)

format_core = env.ClangFormat(
    target="format_core",
    source=Dir(env['LANG_DIR']))
Alias('format_ccore', format_core)


# configure the environment
env = SConscript('build_system/config.py', exports='env')
env.Append(CCFLAGS=['-Wall', '-Wextra', '-Werror'])

# Build the various repos
if os.path.lexists(env['CLIB_DIR']):
    clib_static = SConscript(
        os.path.join(env['CLIB_DIR'], 'SConstruct'),
        exports='env')
    env.Alias('clib', clib_static)

if os.path.lexists(env['LANG_DIR']):
    lang = SConscript(
        os.path.join(env['LANG_DIR'], 'SConstruct'),
        exports='env clib_static')
    Depends(lang, 'clib_static')
    env.Alias('refu', lang)


# Default(lang)
# generate help text for the variables
Help(vars.GenerateHelpText(env))
