# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError

class academicTranscript(models.Model):
    _name ='academic.transcript'
    _description='print academic transcript for selected exams'
    academic_year=fields.Many2one('education.academic.year',"Academic Year")
    level=fields.Many2one('education.class',"Level")
    exams=fields.Many2many('education.exam','transcript_id')
    section=fields.Many2one('education.class.division')
    specific_student=fields.Boolean('For a specific Student')
    student=fields.Many2one('education.student','Student')

    @api.multi
    @api.onchange('level', 'section')
    def get_student_domain(self):
        for rec in self:
            domain = []
            if rec.section:
                domain.append(('class_id','=',rec.section.id))
            else:
                domain.append(('class_id.class_id.id', '=', rec.level.id))

        return {'domain': {'student':domain}}

    # def domain4subject(self):
    #     domain = []
    #     for rec in self:
    #         if rec.division_id.id:
    #             result_created = self.env['education.exam.valuation'].search(
    #                 [('exam_id.id', '=', rec.exam_id.id), ('division_id.id', '=', rec.division_id.id)])
    #             for res in result_created:
    #                 domain.append(res.subject_id.id)
    #     return {'domain': {'subject_id': [('id', '!=', domain)]}}
