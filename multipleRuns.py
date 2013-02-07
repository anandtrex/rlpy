######################################################
# Developed by Alborz Geramiard Nov 30th 2012 at MIT #
######################################################

# Run the main file multiple times and store the result of each run in a separate directory:
from main import *
from os import *
import platform

StartID         = 1
FinishId        = 10
RUNS            = arange(StartID,FinishId+1)
PROJECT_PATH    = 'Results/13ICML-BatchiFDD/Pendulum/AlborzSparsityTest-sparse2'
max_cpu         = multiprocessing.cpu_count()

if(platform.system() == 'Windows'):
    for i in RUNS: # .py files executable by default
        print "Started job %d" % i
        os.system('main.py %d %s %d %d &' % (i, PROJECT_PATH, 0, 1))
else:
    for i in RUNS:
        os.system('chmod +x main.py')
        os.system('./main.py %d %s %d %d &' % (i, PROJECT_PATH, 0, 1))
        print "Started job %d" % i
