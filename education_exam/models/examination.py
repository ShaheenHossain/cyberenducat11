# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EducationExam(models.Model):
    _name = 'education.exam'

    name = fields.Char(string='Name', default='New')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    exam_type = fields.Many2one('education.exam.type', string='Type', required=True)
    school_class_division_wise = fields.Selection([('school', 'School'), ('class', 'Class'), ('division', 'Division')],
                                                  related='exam_type.school_class_division_wise',
                                                  string='School/Class/Division Wise')
    class_division_hider = fields.Char(string='Class Division Hider')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    subject_line = fields.One2many('education.subject.line', 'exam_id', string='Subjects')
    state = fields.Selection([('draft', 'Draft'), ('ongoing', 'On Going'), ('close', 'Closed'), ('cancel', 'Canceled')],
                             default='draft')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    @api.model
    def create(self, vals):
        res = super(EducationExam, self).create(vals)
        if res.division_id:
            res.class_id = res.division_id.class_id.id
        return res

    @api.onchange('class_division_hider')
    def onchange_class_division_hider(self):
        self.school_class_division_wise = 'school'

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(_("Start date must be Anterior to end date"))

    @api.multi
    def close_exam(self):
        self.state = 'close'

    @api.multi
    def cancel_exam(self):
        self.state = 'cancel'

    @api.multi
    def confirm_exam(self):
        if len(self.subject_line) < 1:
            raise UserError(_('Please Add Subjects'))
        name = str(self.exam_type.name) + '-' + str(self.start_date)[0:10]
        if self.division_id:
            name = name + ' (' + str(self.division_id.name) + ')'
        elif self.class_id:
            name = name + ' (' + str(self.class_id.name) + ')'
        self.name = name
        self.state = 'ongoing'


class SubjectLine(models.Model):
    _name = 'education.subject.line'

    subject_id = fields.Many2one('education.subject', string='Subject', required=True)
    date = fields.Date(string='Date', required=True)
    time_from = fields.Float(string='Time From', required=True)
    time_to = fields.Float(string='Time To', required=True)
    mark = fields.Integer(string='Mark')
    exam_id = fields.Many2one('education.exam', string='Exam')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())


class EducationExamType(models.Model):
    _name = 'education.exam.type'

    name = fields.Char(string='Name', required=True)
    school_class_division_wise = fields.Selection([('school', 'School'), ('class', 'Class'), ('division', 'Division'), ('final', 'Final Exam (Exam that promotes students to the next class)')],
                                                  string='Exam Type', default='class')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
