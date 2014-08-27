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


def emit_check(target, source, env):
    variant_dir = env.get('CHECK_VARIANT_DIR', 'build_test')
    test_dir = env.get('CHECK_TEST_DIR', 'test')
    src_dir = env.get('CHECK_SRC_DIR', 'src')
    exec_name = env.get('CHECK_EXEC_NAME', 'check_exec')

    # Create a Variant dir for the tests and sources
    env.VariantDir(os.path.join(variant_dir, test_dir),
                   test_dir,
                   duplicate=1)
    env.VariantDir(os.path.join(variant_dir, src_dir),
                   src_dir,
                   duplicate=1)

    new_sources = [os.path.join(variant_dir, s.get_path()) for s in source]
    new_targets = [
        os.path.splitext(os.path.join(variant_dir, s.get_path()))[0] + 'o'
        for s in source
    ]
    env.Clean(target, variant_dir)
    env.Clean(target, exec_name)
    return target + new_targets, new_sources


def build_check_str(target, source, env):
    return "Building Check unit tests for target {}".format(
        target[0].get_path())


def build_check(target, source, env):
    target_dir = os.path.dirname(target[0].get_path())
    target_name = os.path.basename(target[0].get_path())
    exec_name = os.path.join(target_dir, 'check_exec')
    extra_defines = env.get('CHECK_EXTRA_DEFINES', [])

    # local_env = env.Clone()
    local_env = env
    local_env.Append(LIBS='check')
    defines = local_env['CPPDEFINES']
    defines = remove_defines(defines, ['RF_OPTION_DEBUG'])
    local_env.Append(CCFLAGS="-g")
    local_env.Replace(CPPDEFINES=defines)
    local_env.Append(CPPDEFINES=extra_defines)

    check_exec = local_env.Program(exec_name, source)

    # if we got specific case or suite modify the environment
    # and also switch to verbose output
    if local_env['TEST_CASE'] != '':
        local_env.Append(ENV={'CK_RUN_CASE': local_env['TEST_CASE']})
        local_env['TEST_OUTPUT'] = 'CK_VERBOSE'
    if local_env['TEST_SUITE'] != '':
        local_env.Append(ENV={'CK_RUN_SUITE': local_env['TEST_SUITE']})
        local_env['TEST_OUTPUT'] = 'CK_VERBOSE'

    # run the tests
    run = local_env.Command(
        target='run', source=check_exec,
        action='{} {} {}'.format(
            exec_name,
            local_env['TEST_OUTPUT'],
            local_env['TEST_FORK']))
    Alias(target_name, run)

    if local_env['has_valgrind'] and local_env['TEST_VIA_VALGRIND']:
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
            source=check_exec,
            action=(
                " ".join(valgrind_cmd) +
                " {} {} {}".format(
                    exec_name,
                    local_env['TEST_OUTPUT'],
                    False)))
        Alias(target_name, run_val)
    # success
    return 0


def generate(env, **kw):
    """
    The generate() function modifies the passed-in environment to set up
    variables so that the tool can be executed; it may use any keyword
    arguments that the user supplies (see below) to vary its initialization.
    """
    bld = Builder(action=Action.Action(build_check, build_check_str),
                  emitter=emit_check)
    env.Append(BUILDERS={'Check': bld})
    return True