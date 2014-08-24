from SCons.Script import *
from SCons import Action


def determine_url(reponame):
    d = {
        'clib': 'ssh://git@lefvps/git/refuclib.git',
        'lang': 'ssh://git@lefvps/git/refu.git',
        'build_system': 'ssh://git@lefvps/git/refubuildsystem.git',
    }
    return d.get(reponame, None)


def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True


def build_update_str(target, source, env):
    return "Updating repository {}".format(source[0].get_path())


def build_update(target, source, env):
    target_name = os.path.basename(target[0].get_path())
    local_env = env.Clone()
    reponame = source[0].get_path()

    url = determine_url(reponame)
    if not url:
        return -1

    if (os.path.lexists(reponame)):
        print("is there!")
        update_repo = local_env.Command(
            target='update_repo', source=source,
            action='cd {} && git pull origin'.format(reponame)
        )
        Alias(target_name, update_repo)
    else:
        get_repo = local_env.Command(
            target='get_repo', source=source,
            action='git clone {} {}'.format(url, reponame)
        )
        Alias(target_name, get_repo)

    # success
    return 0


def generate(env, **kw):
    """
    The generate() function modifies the passed-in environment to set up
    variables so that the tool can be executed; it may use any keyword
    arguments that the user supplies (see below) to vary its initialization.
    """
    bld = Builder(action=Action.Action(build_update, build_update_str))
    env.Append(BUILDERS={'UpdateRepo': bld})
    return True
