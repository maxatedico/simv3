from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


# Pipeline Form for Inputs
class Pipeline(Form):
    dataset_name = StringField('data_set_reads', validators=[DataRequired()])
    fasta_ref = StringField('fastar', validators=[DataRequired()])
    vcf_path = StringField('vcf_path', validators=[DataRequired()])
    bed_path = StringField('bed_file', validators=[DataRequired()])
    mutate_rate = StringField('mutation_rate', validators=[DataRequired()])
    base_error_rate = StringField('base_error', validators=[DataRequired()])
    indel_error = BooleanField('indel_error', default=False)


# Mutate Form for Inputs
class Mutate(Form):
    dataset_mutate = StringField('data_set_mutate', validators=[DataRequired()])
    fasta_ref = StringField('fastar', validators=[DataRequired()])
    vcf_path = StringField('vcf_path', validators=[DataRequired()])
    bed_path = StringField('bed_file', validators=[DataRequired()])
    mutate_rate = StringField('mutation_rate', validators=[DataRequired()])


# Reads Form for Inputs
class Reads(Form):
    dataset_reads = StringField('data_set_reads', validators=[DataRequired()])
    base_error_rate = StringField('base_error', validators=[DataRequired()])
    indel_error = BooleanField('indel_error', default=False)

