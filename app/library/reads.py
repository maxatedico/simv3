#!/usr/bin/python
import logging
import subprocess
import ConfigParser
import requests

Config = ConfigParser.ConfigParser()
Config.read("../config")
logger = logging.getLogger(__name__)


# BCFTOOLS - generate FASTAS
def generate_bcf(fasta_ref, truth_vcf, gender, output):
    try:
        # variables
        out_dir_root = output
        newfasta = '.fa'

        if gender == 0:
            newfasta = '1.fa'

        if gender == 1:
            newfasta = '2.fa'

        # execute
        if gender == 0:
            cmd = "bcftools consensus -c " + out_dir_root + "liftover1.txt -H 1 -f " + fasta_ref + " " + truth_vcf \
                  + " 1> " + out_dir_root + newfasta + " 2> " + out_dir_root + "varerror1.txt"

        if gender == 1:
            cmd = "bcftools consensus -c " + out_dir_root + "liftover2.txt -H 1 -f " + fasta_ref + " " + truth_vcf \
                  + " 1> " + out_dir_root + newfasta + " 2> " + out_dir_root + "varerror2.txt"

        logger.info("bcftools cmd:     {}".format(cmd))
        subprocess.check_output(cmd, shell=True)

        return newfasta

    except Exception() as e:
        logging.error('Error message %s' % e)
        raise


# run PIRS simulation
def run_pirs(base, indel, output, pe100, indel_profile, gcdep_profile): 
    try:
        # variables
        out_dir_root = output
        PE100 = pe100
        indels = indel_profile
        gcdep = gcdep_profile
        error_rate = base
        are_indels = indel

        # generate reads
        if are_indels:
            cmd = "pirs simulate -l 100 -x 20 -o " + out_dir_root[:-9] + "pirs --insert-len-mean=180 " \
                  "--insert-len-sd=18 --diploid --base-calling-profile=" + PE100 + " --indel-error-profile=" + \
                  indels + " --gc-bias-profile=" + gcdep + " --error-rate=" + error_rate + \
                  " --phred-offset=33 --no-gc-bias -c \"gzip\" -t 48 " \
                  + out_dir_root + "1.fa " + " " + out_dir_root + "2.fa &> " + out_dir_root + "_pirs.log"

        if not are_indels:
            cmd = "pirs simulate -l 100 -x 20 -o " + out_dir_root[:-9] + " --insert-len-mean=180 " \
                                                                         "--insert-len-sd=18 --diploid " \
                  "--base-calling-profile=" + PE100 + " --indel-error-profile=" + indels + \
                  " --gc-bias-profile=" + gcdep + " --error-rate=" + error_rate + \
                  " --phred-offset=33 --no-indel-errors --no-gc-bias -c \"gzip\" -t 48 " + out_dir_root \
                  + "1.fa " + " " + out_dir_root + "2.fa &> " + out_dir_root + "_pirs.log"

        logger.info("pirs cmd:     {}".format(cmd))
        subprocess.check_output(cmd, shell=True)

    except Exception() as e:
        logging.error('Error message %s' % e)
        raise


def get_from_db(dataset_name, key_name):
    url = "http://data.edicogenome.com/api/get"

    filter = \
        {
            'name': dataset_name,
            'get_x': key_name
        }

    res = requests.get(url, params=filter)
    res.raise_for_status()
    return res.text


def upload_to_db(key_name, dataset_name, value):
    url = "http://data.edicogenome.com/api/set"

    data = \
        {
            'set_x': key_name,
            'name': dataset_name,
            'value': value
        }

    res = requests.post(url, params=data)
    res.raise_for_status()
    return res.text


def get_ref(dataset_name):
    ref_type = get_from_db(dataset_name, 'ref_type')
    return ref_type


def get_fasta_ref(ref_type):
    fasta_ref = get_from_db(ref_type, 'fasta_file')
    return fasta_ref


def get_truth_vcf(dataset_name):
    truth_vcf = get_from_db(dataset_name, 'truth_set_vcf')
    return truth_vcf


# main
def simulate(fasta_ref, truth_vcf, base, indel, output, pe100, indelss, gcdeppp):

    generate_bcf(fasta_ref, truth_vcf, 0, output)

    logging.info('Generated first FASTA')

    generate_bcf(fasta_ref, truth_vcf, 1, output)

    logging.info('Generated second FASTA')
    logging.info('Beginning pIRS simulation')

    run_pirs(base, indel, output, pe100, indelss, gcdeppp)

    logging.info('Generated FASTQs')


def upload_data(dataset_name, root):
    out_dir_root = root
    upload_to_db('fastq_location_1', dataset_name, out_dir_root + '_100_180_1.fq')
    upload_to_db('fastq_location_2', dataset_name, out_dir_root + '_100_180_2.fq')
