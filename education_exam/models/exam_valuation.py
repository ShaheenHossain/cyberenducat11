# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError


class EducationExamValuation(models.Model):
    _name = 'education.exam.valuation'

    name = fields.Char(string='Name', default='New')
    exam_id = fields.Many2one('education.exam', string='Exam', required=True, domain=[('state', '=', 'ongoing')])
    class_id = fields.Many2one('education.class', string='Class', required=True)
    division_id = fields.Many2one('education.class.division', string='Division', required=True)
    teachers_id = fields.Many2one('education.faculty', string='Evaluator')
    mark = fields.Float(string='Max Mark', compute='calculate_marks')
    pass_mark = fields.Float(string='Pass Mark', compute='calculate_marks')
    tut_mark = fields.Integer('Tutorial Mark')
    tut_pass_mark = fields.Integer('Tutorial Pass Mark')
    subj_mark = fields.Integer('Subjective Mark')
    subj_pass_mark = fields.Integer('Subjective Pass Mark')

    obj_mark = fields.Integer('Objective Mark')
    obj_pass_mark = fields.Integer('Objective Pass Mark')

    prac_mark = fields.Integer('Practical Mark')
    prac_pass_mark = fields.Integer('Practical Pass Mark')

    state = fields.Selection([('draft', 'Draft'), ('completed', 'Completed'), ('cancel', 'Canceled')], default='draft')
    valuation_line = fields.One2many('exam.valuation.line', 'valuation_id', string='Students')
    subject_id = fields.Many2one('education.subject', string='Subject', required=True)
    mark_sheet_created = fields.Boolean(string='Mark sheet Created')
    date = fields.Date(string='Date', default=fields.Date.today)
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    @api.onchange('tut_mark','tut_pass_mark','subj_mark','subj_pass_mark','obj_mark','obj_pass_mark','prac_mark','prac_pass_mark')
    def calculate_marks(self):
        for rec in self:
            rec.mark=rec.tut_mark+rec.subj_mark+rec.obj_mark+rec.prac_mark
            rec.pass_mark=rec.tut_pass_mark+rec.subj_pass_mark+rec.obj_pass_mark+rec.prac_pass_mark





    @api.onchange('class_id')
    def onchange_class_id(self):
        domain = []
        if self.division_id.class_id != self.class_id:
            self.division_id = ''
        if self.class_id:
            domain = [('class_id', '=', self.class_id.id)]
        return {'domain': {'division_id': domain}}

    @api.onchange('pass_mark')
    def onchange_pass_mark(self):
        if self.pass_mark > self.mark:
            raise UserError(_('Pass mark must be less than Max Mark'))
        for records in self.valuation_line:
            if records.mark_scored >= self.pass_mark:
                records.pass_or_fail = True
            else:
                records.pass_or_fail = False

    @api.onchange('exam_id', 'subject_id')
    def onchange_exam_id(self):
        if self.exam_id:
            if self.exam_id.division_id:
                self.class_id = self.exam_id.class_id
                self.division_id = self.exam_id.division_id
            elif self.exam_id.class_id:
                self.class_id = self.exam_id.class_id
            else:
                self.class_id = ''
                self.division_id = ''
            self.mark = ''
            if self.subject_id:
                for sub in self.exam_id.subject_line:
                    if sub.subject_id.id == self.subject_id.id:
                        if sub.mark:
                            self.mark = sub.mark
        domain = []
        subjects = self.exam_id.subject_line
        for items in subjects:
            domain.append(items.subject_id.id)
        return {'domain': {'subject_id': [('id', 'in', domain)]}}

    @api.multi
    def create_mark_sheet(self):
        valuation_line_obj = self.env['exam.valuation.line']
        students = self.division_id.student_ids
        if len(students) < 1:
            raise UserError(_('There are no students in this Division'))
        for student in students:
            data = {
                'student_id': student.id,
                'student_name': student.name,
                'valuation_id': self.id,
            }
            valuation_line_obj.create(data)
        self.mark_sheet_created = True

    @api.model
    def create(self, vals):
        res = super(EducationExamValuation, self).create(vals)
        valuation_obj = self.env['education.exam.valuation']
        search_valuation = valuation_obj.search(
            [('exam_id', '=', res.exam_id.id), ('division_id', '=', res.division_id.id),
             ('subject_id', '=', res.subject_id.id), ('state', '!=', 'cancel')])
        if len(search_valuation) > 1:
            raise UserError(
                _('Valuation Sheet for \n Subject --> %s \nDivision --> %s \nExam --> %s \n is already created') % (
                    res.subject_id.name, res.division_id.name, res.exam_id.name))
        return res

    @api.multi
    def valuation_completed(self):
        self.name = str(self.exam_id.exam_type.name) + '-' + str(self.exam_id.start_date)[0:10] + ' (' + str(
            self.division_id.name) + ')'
        result_obj = self.env['education.exam.results']
        result_line_obj = self.env['results.subject.line']
        for students in self.valuation_line:
            search_result = result_obj.search(
                [('exam_id', '=', self.exam_id.id), ('division_id', '=', self.division_id.id),
                 ('student_id', '=', students.student_id.id)])
            if len(search_result) < 1:
                result_data = {
                    'name': self.name,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result = result_obj.create(result_data)
                result_line_data = {
                    'name': self.name,
                    'tut_mark': students.tut_mark,
                    'obj_mark': students.obj_mark,
                    'subj_mark': students.subj_mark,
                    'prac_mark': students.prac_mark,
                    'subject_id': self.subject_id.id,
                    'max_mark': self.mark,
                    'pass_mark': self.pass_mark,
                    'mark_scored': students.mark_scored,
                    'pass_or_fail': students.pass_or_fail,
                    'result_id': result.id,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result_line_obj.create(result_line_data)
            else:
                result_line_data = {
                    'subject_id': self.subject_id.id,
                    'max_mark': self.mark,
                    'pass_mark': self.pass_mark,
                    'tut_mark': students.tut_mark,
                    'obj_mark': students.obj_mark,
                    'subj_mark': students.subj_mark,
                    'prac_mark': students.prac_mark,
                    'mark_scored': students.mark_scored,
                    'pass_or_fail': students.pass_or_fail,
                    'result_id': search_result.id,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result_line_obj.create(result_line_data)
        self.state = 'completed'

    @api.multi
    def set_to_draft(self):
        result_line_obj = self.env['results.subject.line']
        result_obj = self.env['education.exam.results']
        for students in self.valuation_line:
            search_result = result_obj.search(
                [('exam_id', '=', self.exam_id.id), ('division_id', '=', self.division_id.id),
                 ('student_id', '=', students.student_id.id)])
            search_result_line = result_line_obj.search(
                [('result_id', '=', search_result.id), ('subject_id', '=', self.subject_id.id)])
            search_result_line.unlink()
        self.state = 'draft'

    @api.multi
    def valuation_canceled(self):
        self.state = 'cancel'


class StudentsExamValuationLine(models.Model):
    _name = 'exam.valuation.line'

    student_id = fields.Many2one('education.student', string='Students')
    student_name = fields.Char(string='Students')
    mark_scored = fields.Float(string='Mark',compute='calculate_marks')
    tut_mark=fields.Float(string='Tutorial')
    subj_mark=fields.Float(string='Subjective')
    obj_mark=fields.Float(string='Objective')
    prac_mark=fields.Float(string='Practical')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    valuation_id = fields.Many2one('education.exam.valuation', string='Valuation Id')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    @api.onchange('mark_scored', 'pass_or_fail')
    def onchange_mark_scored(self):
        if self.mark_scored > self.valuation_id.mark:
            raise UserError(_('Mark Scored must be less than Max Mark'))
        # if self.mark_scored >= self.valuation_id.pass_mark:
        #     self.pass_or_fail = True
        # else:
        #     self.pass_or_fail = False
        if self.tut_mark >= self.valuation_id.tut_pass_mark and \
                self.prac_mark >= self.valuation_id.prac_pass_mark and \
                self.subj_mark >= self.valuation_id.subj_pass_mark and \
                self.obj_mark >= self.valuation_id.obj_pass_mark :
           self.pass_or_fail=True
        else :
            self.pass_or_fail=False

    @api.multi
    @api.onchange('tut_mark','subj_mark','obj_mark','prac_mark')
    def calculate_marks(self):
        for rec in self:
            rec.mark_scored=rec.tut_mark+ rec.obj_mark+rec.subj_mark+rec.prac_mark
