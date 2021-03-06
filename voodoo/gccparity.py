#tools to make clang compile gcc code
import os
import subprocess
import re

emulateGCCInClangPreinclude = os.path.join( os.path.dirname( __file__ ), "emulate_gcc_in_clang_preinclude.h" )

_cachedGCCIncludePath = None
def gccIncludePath():
    global _cachedGCCIncludePath
    if _cachedGCCIncludePath is None:
        with open( os.devnull, "r" ) as noInput:
            output = subprocess.check_output( [ "cpp", "-Wp,-v" ], stderr = subprocess.STDOUT, stdin = noInput )
            _cachedGCCIncludePath = re.findall( r"\n (\S+)", output )
    return _cachedGCCIncludePath
