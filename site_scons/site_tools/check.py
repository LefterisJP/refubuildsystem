from SCons.Script import *

def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True

def build_check(target, source, env):
    local_env = env.Clone()
    local_env.Append(LIBS=['check'])

    defines = local_env['CPPDEFINES']
    defines['RF_OPTION_DEBUG'] = None
    defines['RF_OPTION_INSANITY_CHECKS'] = None
    defines['CLIB_TESTS_PATH'] = "\\\"" + os.path.join(
        env['CLIB_DIR'], 'test/') + "\\\""
    local_env.Replace(CPPDEFINES=defines)
    program = local_env.Program('check', source)
    run_check = local_env.Command(
        target="test_run",
        source='check',
        action="./check {} {}".format(
            local_env['UNIT_TESTS_OUTPUT'],
            local_env['UNIT_TESTS_FORK']))

    if local_env['has_valgrind']:
        valgrind_cmd = ("valgrind --tool=memcheck "
                        "--leak-check=yes "
                        "--track-origins=yes "
                        "--show-reachable=yes "
                        "--num-callers=20 "
                        "--track-fds=yes")
        run_check_val = local_env.Command(
            target="test_run_val",
            source='check',
            action="{} ./check {} {}".format(
                valgrind_cmd,
                local_env['UNIT_TESTS_OUTPUT'],
                False))  # do not fork tests when running in valgrind

    # success
    return 0


def generate(env, **kw):
    """
    The generate() function modifies the passed-in environment to set up
    variables so that the tool can be executed; it may use any keyword
    arguments that the user supplies (see below) to vary its initialization.
    """
    bld = Builder(action=build_check)
    env.Append(BUILDERS={'Check': bld})
    return True
