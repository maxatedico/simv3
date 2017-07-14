#!/usr/bin/python
import logging
from flask import render_template, request, redirect, url_for
from app import app
from .forms import Pipeline
from .forms import Mutate
from .forms import Reads
from library import reads
from library import mutate
import ConfigParser

logging.basicConfig(filename='app/logger.log', level=logging.INFO, filemode='w', format='%(asctime)s %(message)s', datefmt='%m/%d - %I:%M:%S')

Config = ConfigParser.ConfigParser()
Config.read("app/config")


# Redirector for '/'
@app.route('/')
def index():
    return redirect(url_for('pipeline'))


# Stream for Log
@app.route('/stream')
def stream():
    other_root = Config.get('Paths', 'log_root')

    def generate():
        with open(other_root + 'logger.log') as f:
            lines = f.readlines()
            liner = [x.strip() + '\n' for x in lines]
            result = []
            for line in liner:
                if "stream" not in line:
                    result.append(line)
                    if len(result) > 10:
                        result.pop(0)
            return result

    return app.response_class(generate(), mimetype='text/plain')


# Pipeline
@app.route('/pipeline', methods=['GET', 'POST'])
def pipeline():
    form = Pipeline()

    if request.method == 'POST':

        if request.form['submit'] == 'Run Pipeline':

            # Acquire root directory
            out_dir_root = Config.get('Paths', 'out_dir_root')

            # Profiles
            PE100 = Config.get('Profiles', 'PE100')
            indels = Config.get('Profiles', 'indels')
            gcdep = Config.get('Profiles', 'gcdep')

            # Create variables and acquire inputs
            output = out_dir_root + 'mutations.vcf'
            dataset_name = form.dataset_name.data
            bed_file_path = form.bed_path.data
            fasta_ref = form.fasta_ref.data
            vcf = form.vcf_path.data
            mutate_rate = int(form.mutate_rate.data)


            logging.info('New VCF Path: ' + output)
            logging.info("Acquired Values")

            # Create downsized VCF
            mutate.mutating(mutate_rate, vcf, output, bed_file_path)

            logging.info("Created VCF")

            # Zip
            mutate.bgzip(output)

            logging.info('Zipped VCF')

            # Create and Uplaod to DB
            mutate.check_if_dataset_exists(dataset_name)
            mutate.upload_to_db('ref-type', dataset_name, fasta_ref)
            mutate.upload_to_db('truth_set_vcf', dataset_name, output + '.gz')

            logging.info("Uploaded to Database")

            # Create and Assign Variables for PIRS
            ref_number = reads.get_ref(dataset_name)
            fasta_ref = reads.get_fasta_ref(ref_number)
            base_error_rate = form.base_error_rate.data
            indel_error = form.indel_error.data
            truth_vcf = reads.get_truth_vcf(dataset_name)
            new_output = reads.get_truth_vcf(dataset_name)[:-13]

            logging.info('Acquired Values')
            logging.info('Reference FASTA: ' + ref_number)
            logging.info('Truth VCF: ' + truth_vcf)

            # Simulate FASTAs and Reads
            reads.simulate(fasta_ref, truth_vcf, base_error_rate, indel_error, new_output, PE100, indels, gcdep)

            logging.info('Finished!')

            # Upload
            reads.upload_data(dataset_name, out_dir_root)

            logging.info("Uploaded FASTQs to Database")

    return render_template('base.html', title='Pipeline', form=form)


@app.route('/vcf', methods=['GET', 'POST'])
def dbmutate():
    form = Mutate()

    if request.method == 'POST':

        if request.form['submit'] == 'Create Truth VCF':

            out_dir_root = Config.get('Paths', 'out_dir_root')

            output = out_dir_root + 'mutations.vcf'
            mutate_rate = int(form.mutate_rate.data)
            bed_file_path = form.bed_path.data
            vcf = form.vcf_path.data
            fasta_ref = form.fasta_ref.data

            logging.info("Acquired Values")
            logging.info('New VCF Path: ' + output)

            mutate.mutating(mutate_rate, vcf, output, bed_file_path)

            logging.info("Created VCF")

            mutate.bgzip(output)

            logging.info('Zipped VCF')

            mutate.check_if_dataset_exists(form.dataset_mutate.data, fasta_ref)

            mutate.upload_to_db('truth_set_vcf', form.dataset_mutate.data, output + '.gz')

            logging.info("Uploaded to Database")

    return render_template('mutations.html', title='Create VCF', form=form)


@app.route('/reads', methods=['GET', 'POST'])
def simreads():
    form = Reads()

    if request.method == 'POST':

        if request.form['submit'] == 'Generate Reads':

            PE100 = Config.get('Profiles', 'PE100')
            indels = Config.get('Profiles', 'indels')
            gcdep = Config.get('Profiles', 'gcdep')
            out_dir_root = Config.get('Paths', 'out_dir_root')

            ref = reads.get_ref(form.dataset_reads.data)
            fasta = reads.get_fasta_ref(ref)
            vcf = reads.get_truth_vcf(form.dataset_reads.data)
            output = reads.get_truth_vcf(form.dataset_reads.data)[:-13]
            base = form.base_error_rate.data
            indel = form.indel_error.data

            logging.info('Acquired Values')
            logging.info('Reference FASTA: ' + ref)
            logging.info('Truth VCF: ' + vcf)

            reads.simulate(fasta, vcf, base, indel, output, PE100, indels, gcdep)

            logging.info('Finished!')

            reads.upload_data(form.dataset_reads.data, out_dir_root)

            logging.info("Uploaded FASTQs to Database")

    return render_template('reads.html', title='Create Reads', form=form)

