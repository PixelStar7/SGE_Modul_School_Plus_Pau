# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError 
from dateutil.relativedelta import relativedelta


class EditionEnrollmentWizard(models.TransientModel):
    _name = 'school.edition.enrollment.wizard'
    _description = 'Edition Enrollment Wizard'

    course_edition_id = fields.Many2one('school.school_course_edition', string="Course Edition")

    enrolled_students = fields.Integer('Number of Students', readonly=True)
    aproved_students = fields.Integer('Number of Approved Students', readonly=True)
    suspended_students = fields.Integer('Number of Suspended Students', readonly=True)


    # El camp "state" és especial
    # L'usarem per indicar quins camps s'invisibilitzen, però en aquest cas podria tenir un altre nom
    state = fields.Selection([('init', 'Init'), ('done', 'Done')], 'State', default='init')

    def count_students(self):
        all_enrollments = self.env['school.enrollment']

        total = all_enrollments.search_count([
            ('edition_course_id', '=', self.course_edition_id.id)
        ])

        total_aproved = all_enrollments.search_count([
            ('edition_course_id', '=', self.course_edition_id.id),
            ('qualification', '>=', 5)
        ])

        total_suspended = all_enrollments.search_count([
            ('edition_course_id', '=', self.course_edition_id.id),
            ('qualification', '<', 5)
        ])

        self.write({
            'enrolled_students': total,
            'aproved_students': total_aproved,
            'suspended_students': total_suspended,
            'state': 'done'
        })

        return {
            'name': 'Edition Entollment Wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'res_model': 'school.edition.enrollment.wizard',
            'type': 'ir.actions.act_window',
        }

