# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ApplicationClassDetails(models.Model):
    _name = 'class.details'
    _description = "Student Allocation"

    student_class = fields.Many2one('education.class', string="Admission For", readonly=True,
                                    help="Select the Class to which the students applied")
    assigned_by = fields.Many2one('res.users', string='Assigned By', default=lambda self: self.env.uid,
                                  help="Student Assigning is done by")
    class_id = fields.Many2one('education.class.division', string="Class", required=True,
                               help="Students are alloted to this Class")
    roll_no=fields.Integer()
    @api.multi
    def action_assign_class(self):
        """Assign the class for the selected students after admission by the faculties"""
        for rec in self:
            assign_request = self.env['education.student.class'].browse(self.env.context.get('active_ids'))
            assign_request.get_student_list()
            if not assign_request.student_list:
                raise ValidationError(_('No Student Lines'))
            for line in assign_request.student_list:
                line.student_id.class_id = rec.class_id.id
            assign_request.write({
                'state': 'done',
                'admitted_class': rec.class_id.id,
                'assigned_by': rec.assigned_by.id
            })
