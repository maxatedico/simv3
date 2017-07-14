#!/usr/bin/python
import logging
import ConfigParser
import requests
import subprocess
import json

Config = ConfigParser.ConfigParser()
Config.read("../config")
logger = logging.getLogger(__name__)


# Final VCF Zipper
def bgzip(file_path):
    if '.gz' in file_path:
        raise Exception('Input VCF must be uncompressed')

    cmd = "bgzip -f " + file_path
    logger.info('bgzip cmd:     {}'.format(cmd))
    subprocess.check_output(cmd, shell=True)

    vcf_gz = file_path + '.gz'

    cmd = 'tabix -f {}'.format(vcf_gz)
    logger.info('tabix cmd:     {}'.format(cmd))
    subprocess.check_output(cmd, shell=True)


# Run VCF Downsizer
def mutating(desired_interval, input_vcf, output_vcf, bed_file):
    previous_chromosome = None

    # open either vcf or vcf.gz
    logging.info("Checking if imput vcf has .gz ending")

    if '.gz' in input_vcf:
        import gzip
        open_gz_safe = gzip.open

    else:
        open_gz_safe = open

    if bed_file != "":
        out_dir_root = Config.get('Paths', 'out_dir_root')
        bedtoolsrun = "bedtools intersect -a " + input_vcf + " -b " + bed_file + " > " + out_dir_root

        logging.info(bedtoolsrun)
        logging.info("Running bedtools intersect function")

        try:
            subprocess.check_output(bedtoolsrun, shell=True)

        except RuntimeError:
            logging.info("Bedtools failed due to runtime error.")

        except TypeError:
            logging.info("Bedtools failed due to type error.")

        except ValueError:
            logging.info("Bedtools failed due to value  error.")

        except NameError:
            logging.info("Bedtools failed due to name  error.")

    else:
        intersection_name = input_vcf
    logging.info("Beginning to take interval samples from outputted vcf")

    with open(output_vcf, 'w') as stream_out:
        with open_gz_safe(intersection_name) as stream_in:
            for i, line in enumerate(stream_in):

                if line[0] == '#':
                    stream_out.write(line)
                    # print(line)
                    continue

                # import pdb; pdb.set_trace()
                this_chromosome = line.split()[0]
                this_variant_position = int(line.split()[1])

                if this_chromosome != previous_chromosome:
                    previous_chromosome = this_chromosome
                    ref_position = this_variant_position
                    stream_out.write(line)
                    belowline = line
                    below = this_variant_position
                    target = ref_position + desired_interval
                    continue

                if this_variant_position > target:
                    above = this_variant_position

                    if (above - target) < (target - below):
                        stream_out.write(line)
                        ref_position = above

                    else:

                        if below > ref_position:
                            stream_out.write(belowline)
                            ref_position = below

                        else:
                            stream_out.write(line)
                            ref_position = above

                    target = ref_position + desired_interval

                else:
                    below = this_variant_position
                    belowline = line

    logging.info("done")


# Acquire Values from DataBase
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


# Upload Values to Database
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


# Check if Dataset Exists and if not, Create an Entry
def check_if_dataset_exists(dataset_name):
    logging.info('Check if dataset exists')
    url = "http://data.edicogenome.com/api/get"

    filter = {'name': dataset_name,
              'get_x': 'ref_type'}

    r = requests.get(url, params=filter)
    r.raise_for_status()
    r = r.text

    if r:
        logging.info('Dataset exists')

    else:
        logging.info('Dataset does not exist')
        create_dna_dataset(dataset_name)


# Supporter for Above
def post_requests(data):
    headers = {'content-type': 'application/json'}
    r = requests.post(
        "http://data.edicogenome.com/api/dataset/submit",
        data=json.dumps(data),
        headers=headers)
    logging.info("status code: {}".format(r.status_code))
    logging.info("reason: {}".format(r.reason))
    r.raise_for_status()


# Dataset creator
def create_dna_dataset(dataset_name):
    print('Create dataset: {}, with ref: {}'.
          format(dataset_name))
    data = {
        "name": dataset_name,
        "group_id": "2",
        "user": "simulator",
        "values": [
            {"key": 37, "value": "", "type": "text"},
            {"key": 38, "value": "", "type": "text"},
            {"key": 39, "value": "", "type": "text"},
            {"key": 40, "value": "", "type": "text"},
            {"key": 41, "value": "", "type": "text"},
            {"key": 42, "value": "", "type": "text"},
            {"key": 43, "value": "", "type": "text"}],
    }
    post_requests(data)


