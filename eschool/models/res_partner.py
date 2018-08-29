# -*- coding: utf-8 -*-

from odoo import models, fields, api

class examtabulationwizard(models.Model):
    _inherit = 'res.partner'
    name_b=fields.Char("নামের প্রথম অংশ")
    middle_name_b=fields.Char("নামের মধ্যাংশ")
    last_name_b=fields.Char("নামের শেষাংশ")
    nid_no=fields.Integer('NID No')
    _sql_constraints = [
        ('nid_no', 'unique(nid_no)', "NID number must be unique!"),
    ]