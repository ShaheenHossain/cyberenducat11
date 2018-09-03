
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationSubject(models.Model):
    _name = 'education.subject'

    name = fields.Char(string='Name', required=True, help="Name of the Subject")
    is_language = fields.Boolean(string="Language", help="Tick if this subject is a language")
    is_lab = fields.Boolean(string="Lab", help="Tick if this subject is a Lab")
    code = fields.Char(string="Code", help="Enter the Subject Code")
    type = fields.Selection([('compulsory', 'Compulsory'), ('elective', 'Elective')],
                            string='Type', default="compulsory",
                            help="Choose the type of the subject")
    weightage = fields.Float(string='Weightage', default=1.0,
                             help="Enter the weightage for this subject")
    description = fields.Text(string='Description')

    _sql_constraints = [
        ('code', 'unique(code)', "Another Subject already exists with this code!"),
    ]

    @api.constrains('weightage')
    def check_weightage(self):
        """return warning if the weightage given is not a possitive value"""
        for rec in self:
            if rec.weightage <= 0:
                raise ValidationError(_('Weightage must be Possitive'))


class StandardMedium(models.Model):
    _name = "education.medium"
    _description = "Standard Medium"

    name = fields.Char(string='Name', required=True,
                       help="Enter the Name of the Medium")
    code = fields.Char(string='Code', help="Enter the Medium Code")
    description = fields.Text(string='Description')


class EducationMotherTongue(models.Model):
    _name = "education.mother.tongue"
    _description = "Mother Tongue Language"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code')


class EducationSyllabus(models.Model):
    _name = 'education.syllabus'

    name = fields.Char('Name', required=True)
    class_id = fields.Many2one('education.class', string='Class')
    subject_id = fields.Many2one('education.subject', string='Subject')
    total_hours = fields.Float(string='Total Hours')
    description = fields.Text(string='Syllabus Modules')

    @api.constrains('total_hours')
    def validate_time(self):
        """returns validation error if the hours is not a possitive value"""
        for rec in self:
            if rec.total_hours <= 0:
                raise ValidationError(_('Hours must be greater than Zero'))
