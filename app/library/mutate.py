#!/usr/bin/python
import logging
import ConfigParser
import requests
import os
import subprocess

Config = ConfigParser.ConfigParser()
Config.read("../config")
logger = logging.getLogger(__name__)


def mutating(desired_interval, input_vcf, intersection_name, output_vcf, bed_file):
    previous_chromosome = None
    this_variant_position = None

    # open either vcf or vcf.gz
    logging.info("Checking if imput vcf has .gz ending")
    if '.gz' in input_vcf:
        import gzip
        open_gz_safe = gzip.open
    else:
        open_gz_safe = open
    if bed_file != "":
        bedtoolsrun ="bedtools intersect -a " + input_vcf +" -b "+ bed_file +" > " + intersection_name
        logging.info(bedtoolsrun)
        logging.info( "Running bedtools intersect function")
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
                        # print("interval a: ", above - ref_position)
                        # print(line)
                        ref_position = above
                    else:
                        if below > ref_position:
                            stream_out.write(belowline)
                            # print("interval b: ", below - ref_position)
                            # print(line)
                            ref_position = below
                    target = ref_position + desired_interval
                else:
                    below = this_variant_position
                    belowline = line

    logging.info("done")


def get_from_db(dataset_name, key_name):
    url = "http://data.edicogenome.com/api/get"

    filter = \
        {
            'name': dataset_name,
            'get_x': key_name
        }

    res = requests.get(url, params=filter)
    res.raise_for_status()

    print key_name + "--" + res.text
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

    print key_name + "--" + res.text
    return res.text


















