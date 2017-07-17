#!/usr/bin/python
#import logging
import subprocess

#logger = logging.getLogger(__name__)


def clean_up(input_error):
    try:

        path = "/mnt/archive/adam_and_max/"
        cmd = path + "clean_read_info.pl_ < " + input_error + " > " + path + "clean.read.info"
        cmd_2 = path + "xform_read.info.pl_ < " + path + "clean.read.info > " + path + "read.info.xform"

        print cmd
        print cmd_2

        #logger.info("Clean-Up Command: {}".format(cmd))
        #logger.info("ReAlign Command: {}".format(cmd_2))
        subprocess.check_output(cmd, shell=True)
        subprocess.check_output(cmd_2, shell=True)

    except Exception() as e:
        #logging.error('Error message %s' % e)
        raise

clean_up("/mnt/archive/sim_data/pirs_simulator/vlrd_chr1_normalNoise_varRate0.002_indelErrors1_errorRate1_varRate0.002/pirs_100_180.read.info.gz")
