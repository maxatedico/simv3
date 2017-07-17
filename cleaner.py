#!/usr/bin/python
import logging
import subprocess

logger = logging.getLogger(__name__)


def clean_up(input_error):
    try:

        path = "/mnt/archive/adam_and_max/"
        cmd = path + "clean_read_info.pl < " + path + input_error + " > " + path + "clean.read.info"
        cmd_2 = path + "xform_read.info.pl < " + path + "clean.read.info > " + path + "read.info.xform"

        logger.info("Clean-Up Command: {}".format(cmd))
        logger.info("ReAlign Command: {}".format(cmd_2))
        subprocess.check_output(cmd, shell=True)
        subprocess.check_output(cmd_2, shell=True)

    except Exception() as e:
        logging.error('Error message %s' % e)
        raise
