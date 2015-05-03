import os
import fnmatch
from SCons.Script import *
from SCons import Action
import SCons.Defaults
import SCons.Tool
import SCons.Util


def find_files(dir):
    matches = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, '*.[ch]'):
            matches.append(os.path.join(root, filename))
    return matches


def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True


def clangformat_str(target, source, env):
    return "Style Formatting repo {}".format(source[0].get_path())


def build_clangformat(source, target, env):
    target_name = os.path.basename(target[0].get_path())
    reponame = source[0].get_path()
    files = find_files(os.path.join(reponame, 'src'))
    files += find_files(os.path.join(reponame, 'include'))
    format_repo = env.Command(
        target='format_repo_{}'.format(reponame),
        source=source,
        action='clang-format -style=file -i {}'.format(' '.join(files))
        )
    env.Alias(target_name, format_repo)


def generate(env, **kw):
    bld = Builder(action=Action.Action(build_clangformat, clangformat_str))
    env.Append(BUILDERS={'ClangFormat': bld})
    return True
