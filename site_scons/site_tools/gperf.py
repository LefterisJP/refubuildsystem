import os
from SCons.Script import *
from SCons import Action
import SCons.Defaults
import SCons.Tool
import SCons.Util


def change_extension(source, new_ext):
    base, ext = os.path.splitext(SCons.Util.to_String(source))
    return base + '.' + new_ext


def exists(env):
    """
    The exists() function should return a true value if the tool is
    available. Tools in the toolpath are used before any of the built-in ones
    """
    return True


def gperf_emitter(target, source, env):
    """ Emit a header file with the same name """
    target = []
    for s in source:
        src = str(s)
        targetBase, targetExt = os.path.splitext(SCons.Util.to_String(src))
        target.append(targetBase + '.h')

    return target, source


def gperf_generator(source, target, env, for_signature):
    return [SCons.Action.Action(
        "$GPERF $GPERFFLAGS --output-file={} {}".format(
            t,  change_extension(t, 'gperf')),
        "Generating pergect hash table for {}".format(SCons.Util.to_String(t)))
        for t in target]


def generate(env, **kw):
    env.SetDefault(GPERF='gperf')
    env.SetDefault(GPERFFLAGS='-t')
    env.SetDefault(
        GPERFCOMM="$GPERF $GPERFFLAGS --output-file=$TARGET $SOURCE")
    env.SetDefault(GPERFCOMMSTR='Generating perfect hash table from $SOURCES')

    bld = Builder(generator=gperf_generator, emitter=gperf_emitter)
    env.Append(BUILDERS={'Gperf': bld})
    return True
