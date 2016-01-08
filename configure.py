import optparse
import os
import sys
import shutil
import platform
import fnmatch
import os

script_dir = os.path.dirname(__file__)
root_dir = os.path.normpath(script_dir)
output_dir = os.path.join(os.path.abspath(root_dir), 'out')
curl_root = os.path.join(os.path.abspath(root_dir), 'curl')
openssl_root = os.path.join(os.path.abspath(root_dir), 'openssl\\openssl')
openssl_inc = os.path.join(os.path.abspath(root_dir), 'openssl\\openssl\\include\\openssl')

sys.path.insert(0, os.path.join(root_dir, 'build', 'gyp', 'pylib'))

try:
    import gyp
except ImportError:
    print('You need to install gyp in build/gyp first. See the README.')
    sys.exit(42)

# parse our options
parser = optparse.OptionParser()

parser.add_option("--toolchain",
                  action="store",
                  type="choice",
                  dest="toolchain",
                  choices=['2008', '2010', '2012', '2013', '2015', 'auto'],
                  help="msvs toolchain to build for. [default: %default]",
                  default='auto')

parser.add_option("--target-arch",
                  action="store",
                  dest="target_arch",
                  type='choice',
                  choices=['x86', 'x64'],
                  help="CPU architecture to build for. [default: %default]",
                  default='x86')

(options, args) = parser.parse_args()


def getoption(value, default):
    if not value:
        return default
    return value


def configure_defines(o):
    """
    Configures libcurl
    """
    o.extend(['-D', 'target_arch=%s' % getoption(options.target_arch, host_arch())])
    o.extend(['-D', 'host_arch=%s' % getoption(options.target_arch, host_arch())])
    o.extend(['-D', 'library=static_library'])


def configure_buildsystem(o):
    """
    Configures buildsystem
    """
    global output_dir

    # gyp target
    args.append(os.path.join(root_dir, 'curl.gyp'))

    # includes
    args.extend(['-I', os.path.join(root_dir, 'common.gypi')])

    # msvs
    o.extend(['-f', 'msvs'])

    # msvs toolchain
    if options.toolchain:
        o.extend(['-G', 'msvs_version=' + options.toolchain])
        output_dir = os.path.join(output_dir, 'vs' + options.toolchain)

    # target arch
    output_dir = os.path.join(output_dir, options.target_arch)

    # gyp
    o.append('--depth=' + root_dir)
    o.append('-Goutput_dir=' + output_dir)
    o.append('--generator-output=' + output_dir)
    o.append('--suffix=.' + options.target_arch)

    # copy curlbuild.h
    shutil.copy(os.path.join(root_dir, "build\\curlbuild.h"),
                os.path.join(curl_root, "include\\curl\\curlbuild.h"))

    # copy tool_hugehelp.c
    shutil.copy(os.path.join(root_dir, "build\\tool_hugehelp.c"),
                os.path.join(curl_root, "lib\\tool_hugehelp.c"))

    # copy openssl headers
    def copy_headers(src, dst):
      matches = []
      for root, dirnames, filenames in os.walk(src):
        for filename in fnmatch.filter(filenames, '*.h'):
          shutil.copy(os.path.join(root, filename), dst)

    try:
      os.makedirs(openssl_inc)
    except:
      pass

    shutil.copy(os.path.join(openssl_root, "..\\config\opensslconf.h"), openssl_inc)
    shutil.copy(os.path.join(openssl_root, "e_os.h"), openssl_inc)
    shutil.copy(os.path.join(openssl_root, "e_os2.h"), openssl_inc)
    copy_headers(os.path.join(openssl_root, "crypto"), openssl_inc)
    copy_headers(os.path.join(openssl_root, "ssl"), openssl_inc)


def host_arch():
    machine = platform.machine()
    if machine == 'i386':
        return 'ia32'
    return 'x64'


def run_gyp(args):
    """
    Executes gyp
    """
    rc = gyp.main(args)
    if rc != 0:
        print 'Error running GYP'
        sys.exit(rc)

# gyp arguments
args = []
args.append("--no-parallel")

# gyp configure
configure_buildsystem(args)
configure_defines(args)

# build
gyp_args = list(args)
run_gyp(gyp_args)
