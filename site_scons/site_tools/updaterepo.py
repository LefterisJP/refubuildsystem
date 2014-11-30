import os
from SCons.Script import *
from SCons import Action


repos = {
    'clib': 'ssh://git@lefvps/git/refuclib.git',
    'lang': 'ssh://git@lefvps/git/refu.git',
    'build_system': 'ssh://git@lefvps/git/refubuildsystem.git',
    'documentation': 'ssh://git@lefvps/git/refudocumentation.git',
}


def determine_url(reponame):
    return repos.get(reponame, None)


def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True


def build_update_str(target, source, env):
    return "Updating repository {}".format(source[0].get_path())


def update_single_repo(reponame, source, target_name, url, env):
    if os.path.lexists(reponame):
        update_repo = env.Command(
            target='update_repo_{}'.format(reponame),
            source=source,
            action='cd {} && git pull origin'.format(reponame)
        )
        env.Alias(target_name, update_repo)
    else:
        get_repo = env.Command(
            target='get_repo_{}'.format(reponame),
            source=source,
            action='git clone {} {}'.format(url, reponame)
        )
        env.Alias(target_name, get_repo)


def build_update(target, source, env):
    target_name = os.path.basename(target[0].get_path())
    local_env = env.Clone()
    reponame = source[0].get_path()

    if reponame != 'build_system/SConstruct':
        url = determine_url(reponame)
        if not url:
            return -1

    # use ssh environment variables of the system if existing
    pid = os.environ.get('SSH_AGENT_PID')
    askpass = os.environ.get('SSH_ASKPASS')
    authsock = os.environ.get('SSH_AUTH_SOCK')
    if pid:
        local_env.Append(ENV={'SSH_AGENT_PID': pid})
    if askpass:
        local_env.Append(ENV={'SSH_ASKPASS': askpass})
    if authsock:
        local_env.Append(ENV={'SSH_AUTH_SOCK': authsock})

    if reponame != 'build_system/SConstruct':
        update_single_repo(reponame, source, target_name, url, local_env)
    else:
        for k, v in repos.iteritems():
            update_single_repo(k, source, target_name, v, local_env)
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
