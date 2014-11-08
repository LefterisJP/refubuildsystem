import os


class Module:
    """Represents a module of the code with its names, its list of sources
       its #ifdef macro and a list of other modules it depends on
    """
    def __init__(self, name,
                 sources=[],
                 macro="",
                 win32_sources=[],
                 linux_sources=[],
                 dependencies=[]):
            self.name = name
            self.sources = sources
            self.macro = macro
            self.win32_sources = win32_sources
            self.linux_sources = linux_sources
            self.dependencies = dependencies

    def add(self, sources, env, deps=[], check=True):
        """Addition of a module's sources including
           additional check for dependencies and
           recursive addition of said dependencies

           -sources: The list of sources for compilation
           -env: The Scons environment
           -deps: A list of current modules to build -- helps in
            avoiding duplication
           -check: A flag to determine whether we should check for
            dependencies or not
        """
        env.Append(CPPDEFINES={self.macro: None})
        sources.extend(self.sources)
        if(env['TARGET_SYSTEM'] == 'Windows'):
            sources.extend(self.win32_sources)
        else:
            sources.extend(self.linux_sources)
        if check:
            needed = set(self.dependencies)-set(deps)
            for m in modules:
                if m.name in needed:
                    deps.append(m.name)
                    m.add(sources, env, deps, True)


# empty list of modules and sources
sources = []
modules = []

# add all the modules one by one
modules.append(
    Module("CORE",
           ['refu.c', 'Utils/endianess.c', 'Utils/log.c',
            'Utils/localmem.c', 'Utils/math.c',
            'Persistent/buffers.c', 'Utils/buffer.c',
            'Utils/array.c',
            'Utils/rf_unicode.c',
            'Utils/hash.c',
            'Numeric/Integer/conversion.c'])
)

modules.append(
    Module("STRING",
           ['String/rf_str_common.c', 'String/rf_str_commonp.c',
            'String/rf_str_conversion.c',
            'String/rf_str_conversionp.c',
            'String/rf_str_core.c', 'String/rf_str_corex.c',
            'String/rf_str_files.c',
            'String/rf_str_filesx.c', 'String/rf_str_module.c',
            'String/rf_str_manipulation.c',
            'String/rf_str_manipulationx.c', 'String/rf_str_retrieval.c',
            'String/rf_str_traversalx.c'],
           macro="RF_MODULE_STRINGS",
           dependencies=['IO'])
)

modules.append(
    Module("PARALLEL",
           ['Parallel/rf_threading.c'],
           win32_sources=[''],
           linux_sources=['Parallel/rf_worker_pool_linux.c',
                          'Parallel/rf_threading_linux.c'],
           macro="RF_MODULE_PARALLEL",
           dependencies=["INTRUSIVE_LIST"])
)

modules.append(
    Module("IO",
           ['IO/rf_file.c'],
           macro="RF_MODULE_IO",
           win32_sources=[],
           linux_sources=[])
)

modules.append(
    Module("TEXTFILE",
           ['IO/rf_textfile.c'],
           macro="RF_MODULE_IO_TEXTFILE",
           dependencies=['STRING'])
)

modules.append(
    Module("INTRUSIVE_LIST",
           ['Data_Structures/intrusive_list.c'],
           macro="RF_MODULE_INTRUSIVE_LIST")
)

modules.append(
    Module("HTABLE",
           ['Data_Structures/htable.c'],
           macro="RF_MODULE_HTABLE")
)

modules.append(
    Module("MEMORY_POOL",
           ['Utils/fixed_memory_pool.c'],
           macro="RF_MODULE_MEMORY_POOL")
)

modules.append(
    Module("BINARY_ARRAY",
           ['Data_Structures/binaryarray.c'],
           macro="RF_MODULE_BINARYARRAY")
)

modules.append(
    Module("TIME",
           win32_sources=['Time/time_win32.c'],
           linux_sources=['Time/time_linux.c'],
           macro="RF_MODULE_TIME_TIMER")
)

modules.append(
    Module("SYSTEM",
           [],
           win32_sources=[
               'System/rf_system_win32.c',
               'System/rf_system_info_win32.c'
           ],
           linux_sources=[
               'System/rf_system_linux.c',
               'System/rf_system_info_linux.c'
           ],
           macro="RF_MODULE_SYSTEM"))


Import('local_env')
env = local_env

if 'ALL' not in env['REFU_MODULES']:
    # add the core and system modules
    if 'CORE' not in env['REFU_MODULES']:
        env['REFU_MODULES'].append('CORE')
        if 'SYSTEM' not in env['REFU_MODULES']:
            env['REFU_MODULES'].append('SYSTEM')
            # make a copy of the dependencies
            deps = env['REFU_MODULES'][:]
            for mod in modules:
                if mod.name in env['REFU_MODULES']:
                    mod.add(sources, env, deps)
else:  # all modules requested
    for mod in modules:
        mod.add(sources, env, check=False)

Return('modules sources')
