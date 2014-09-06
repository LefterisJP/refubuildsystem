import os
from SCons.Script import *
from SCons import Action
import SCons.Defaults
import SCons.Tool
import SCons.Util

gperf_action = SCons.Action.Action("$GPERFCOMM", "$GPERFCOMMSTR")


def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True


def gperf_emitter(target, source, env):
    """ Emit a header file with the same name """
    targetBase, targetExt = os.path.splitext(SCons.Util.to_String(target[0]))
    target = targetBase + '.h'
    return target, source


def generate(env, **kw):
    env.SetDefault(GPERF='gperf')
    env.SetDefault(GPERFFLAGS='-t')
    env.SetDefault(
        GPERFCOMM="$GPERF $GPERFFLAGS --output-file=$TARGET $SOURCES")
    env.SetDefault(GPERFCOMMSTR='Generating perfect hash table from $SOURCES')

    bld = Builder(action=gperf_action, emitter=gperf_emitter)
    env.Append(BUILDERS={'Gperf': bld})
    return True
