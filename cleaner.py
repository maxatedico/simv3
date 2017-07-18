#!/usr/bin/python
import subprocess


def clean_up(input_error):
    path = "/mnt/archive/adam_and_max/"
    cmd = path + "clean_read_info.pl_ < " + input_error + " > " + path + "clean.read.info"
    cmd_2 = path + "xform_read_info.pl_ < " + path + "clean.read.info > " + path + "read.info.xform"

    print cmd
    print cmd_2

    subprocess.check_output(cmd, shell=True)
    #subprocess.check_output(cmd_2, shell=True)

clean_up("/mnt/archive/sim_data/pirs_simulator/vlrd_chr1_normalNoise_varRate0.002_indelErrors1_errorRate1_varRate0.002/pirs_100_180.read.info.gz")
