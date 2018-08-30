# -*- coding: utf-8 -*-


from odoo import models, fields, api


class EducationExamResults(models.Model):
    _name = 'education.exam.results'

    name = fields.Char(string='Name')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line', 'result_id', string='Subjects')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Float(string='Total Pass Mark', store=True, readonly=True, compute='_total_marks_all')
    total_max_mark = fields.Float(string='Total Max Mark', store=True, readonly=True, compute='_total_marks_all')
    total_mark_scored = fields.Float(string='Total Marks Scored', store=True, readonly=True, compute='_total_marks_all')
    overall_pass = fields.Boolean(string='Overall Pass/Fail', store=True, readonly=True, compute='_total_marks_all')
    @api.depends('subject_line.mark_scored')
    def _total_marks_all(self):
        for results in self:
            total_pass_mark = 0
            total_max_mark = 0
            total_mark_scored = 0
            overall_pass = True
            for subjects in results.subject_line:
                total_pass_mark += subjects.pass_mark
                total_max_mark += subjects.max_mark
                total_mark_scored += subjects.mark_scored
                if not subjects.pass_or_fail:
                    overall_pass = False
            results.total_pass_mark = total_pass_mark
            results.total_max_mark = total_max_mark
            results.total_mark_scored = total_mark_scored
            results.overall_pass = overall_pass


class ResultsSubjectLine(models.Model):
    _name = 'results.subject.line'

    tut_mark = fields.Float(string='Tutorial')
    subj_mark = fields.Float(string='Subjective')
    obj_mark = fields.Float(string='Objective')
    prac_mark = fields.Float(string='Practical')
    grade=fields.Char('Grade',compute='_compute_grade')
    score=fields.Float('GP')
    name = fields.Char(string='Name')
    subject_id = fields.Many2one('education.subject', string='Subject')
    max_mark = fields.Float(string='Max Mark')
    pass_mark = fields.Float(string='Pass Mark')
    mark_scored = fields.Float(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    result_id = fields.Many2one('education.exam.results', string='Result Id')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    academic_year = fields.Many2one('education.academic.year', string='Academic Year',
                                    related='division_id.academic_year_id', store=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    @api.multi
    @api.depends('mark_scored')
    def _compute_grade(self):
        for record in self:
            per_obtained=(record.mark_scored * 100)/record.max_mark
            grades = self.env['education.result.grading'].search([['id', '>', '0']])
            for gr in grades:
                if gr.min_per <= per_obtained and \
                        gr.max_per >= per_obtained:
                    record.grade = gr.result
                    record.score = gr.score
