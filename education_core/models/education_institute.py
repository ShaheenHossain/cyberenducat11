
from odoo import fields, models


class EducationInstitute(models.Model):
    _inherit = 'res.company'

    affiliation = fields.Char(string='Affiliation')
    register_num = fields.Char(string='Register')

    base_class = fields.Many2one('education.class', string="Lower class")
    higher_class = fields.Many2one('education.class', string="Higher class")


class EducationInstitutes(models.Model):
    _name = 'education.institute'
    _description = "Educational Institutions"

    name = fields.Char(string="School name", required=True)
    affiliation = fields.Char(string='Affiliation')
    register_num = fields.Char(string='Register Number')
    base_class = fields.Many2one('education.class', string="Lower class")
    higher_class = fields.Many2one('education.class', string="Higher class")
    description = fields.Text(string='Description', help="Description about the Other Institute")

    _sql_constraints = [
        ('register_num', 'unique(register_num)', "Another Institute already exists with this code!"),
    ]


class EducationResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(string="Is a Student")
    is_parent = fields.Boolean(string="Is a Parent")


class ReligionReligion(models.Model):
    _name = "religion.religion"
    _description = "Religion"

    name = fields.Char(string="Religion", required=True)


class Religion(models.Model):
    _name = 'religion.caste'
    _description = "Caste"

    name = fields.Char(string="Caste", required=True)
