from SCons.Script import *
from SCons import Action


def remove_defines(defines, names):
    if isinstance(defines, dict):
        for n in names:
            try:
                defines.pop(n)
            except:
                pass
    else:  # should be a list
        for n in names:
            try:
                defines.remove(n)
                continue
            except:
                pass
            for i, d in enumerate(defines):
                if isinstance(d, tuple):
                    if d[0] == n:
                        defines.pop(i)
                        break

    return defines


def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True


def build_check_str(target, source, env):
    return "Building Check unit tests for target {}".format(
        target[0].get_path())


def build_check(target, source, env):
    target_name = os.path.basename(target[0].get_path())
    local_env = env.Clone()
    local_env.Append(LIBS='check')
    clib = local_env.get('CLIB', None)
    if clib:
        local_env.Append(LIBS=clib)
    local_env.Append(LIBPATH=local_env['CLIB_DIR'])

    defines = local_env['CPPDEFINES']
    defines = remove_defines(defines, ['RF_OPTION_DEBUG'])
    local_env.Append(CCFLAGS="-g")
    local_env.Replace(CPPDEFINES=defines)
    local_env.Append(CPPDEFINES={
        'CLIB_TESTS_PATH':
        "\\\"" + os.path.join(env['CLIB_DIR'], 'test/') + "\\\""
    })

    check_exec = local_env.Program('check', source)
    run = local_env.Command(
        target='run', source='check',
        action='./check {} {}'.format(
            local_env['UNIT_TESTS_OUTPUT'],
            local_env['UNIT_TESTS_FORK']))
    Alias(target_name, run)

    if local_env['has_valgrind']:
        valgrind_cmd = [
            "valgrind",
            "--tool=memcheck",
            "--leak-check=yes",
            "--track-origins=yes",
            "--show-reachable=yes",
            "--num-callers=20",
            "--track-fds=yes"
        ]
        run_val = local_env.Command(
            target='run_val',
            source='check',
            action=(
                " ".join(valgrind_cmd) +
                " ./check {} {}".format(
                    local_env['UNIT_TESTS_OUTPUT'],
                    False)))
        Alias(target_name, run_val)

    # setup cleaning (TODO, this does not work for now)
    local_env.Clean(target_name, check_exec)

    # success
    return 0


def generate(env, **kw):
    """
    The generate() function modifies the passed-in environment to set up
    variables so that the tool can be executed; it may use any keyword
    arguments that the user supplies (see below) to vary its initialization.
    """
    bld = Builder(action=Action.Action(build_check, build_check_str))
    env.Append(BUILDERS={'Check': bld})
    return True
