from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired


class Pipeline(Form):
    data_set = StringField('data_set_reads', validators=[DataRequired()])
    base_error = StringField('base_error', validators=[DataRequired()])
    indel_error = BooleanField('indel_error', default=False)
    vcf_path = StringField('vcf_path', validators=[DataRequired()])
    mutation_rate = StringField('mutation_rate', validators=[DataRequired()])
    bed_vcf_name = StringField('bed_vcf_name', validators=[DataRequired()])
    bed_file = StringField('bed_file', validators=[DataRequired()])


class Mutate(Form):
    data_set_mutate = StringField('data_set_mutate', validators=[DataRequired()])
    vcf_path = StringField('vcf_path', validators=[DataRequired()])
    mutation_rate = StringField('mutation_rate', validators=[DataRequired()])
    bed_vcf_name = StringField('bed_vcf_name', validators=[DataRequired()])
    bed_file = StringField('bed_file', validators=[DataRequired()])


class Reads(Form):
    data_set_reads = StringField('data_set_reads', validators=[DataRequired()])
    base_error = StringField('base_error', validators=[DataRequired()])
    indel_error = BooleanField('indel_error', default=False)

