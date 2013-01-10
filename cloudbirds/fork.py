import subprocess
import sys
import time

subprocess.call("python %s" % (" ".join(sys.argv)), shell=True)

time.sleep(10)