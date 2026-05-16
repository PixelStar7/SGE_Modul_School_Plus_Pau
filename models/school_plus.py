# -*- coding: utf-8 -*- 
from odoo import models, fields, api, _ 
from odoo.exceptions import ValidationError 
from dateutil.relativedelta import relativedelta


class SchoolStudent(models.Model):
    _name = 'school.student'
    _description = 'Student Management'
    _order = 'last_name,first_name'

    # Dades obligatòries
    first_name = fields.Char('First Name', size=30, required=True)
    last_name = fields.Char('Last Name', size=40, required=True)
    birthdate = fields.Date('Birthdate', required=True) # Date per a les dates

    # Llista desplegable fixa [(valor1, valor2)]
        # valor1 --> Clau interna de la BD [male]
        # valor2 --> El que veu l'usuari a la pantalla [Male]
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Gender', required=True)

    phone = fields.Char('Phone', required=True)

    street1 = fields.Char('Street1', size=50, required=True)

    # Relació Many2one (Estudiants --> Nacionalitat).
    country_id = fields.Many2one('res.country', 'Citizenship', required=True)

    # Relació Many2one (Estudiants --> Estat).
    state_id = fields.Many2one('res.country.state', 'State', required=True)

    state_country = fields.Many2one('res.country', 'Country', related='state_id.country_id', readonly=True)
    
    # Relació Many2one (Estudiants --> Persona).
    customer_id = fields.Many2one('res.partner', 'Customer', required=True)

    # Camps related de customer_id
    ci_phone = fields.Char('Phone', related='customer_id.phone', readonly=True)
    ci_address = fields.Char('Address', related='customer_id.street', readonly=True)
    ci_zip = fields.Char('Zip', related='customer_id.zip', readonly=True)
    ci_city = fields.Char('City', related='customer_id.city', readonly=True)
    ci_state_id = fields.Many2one('res.country.state', 'State', related='customer_id.state_id', readonly=True)
    ci_country_id = fields.Many2one('res.country', 'Country', related='customer_id.country_id', readonly=True)


    zip = fields.Integer('Zip code', required=True)

    city = fields.Char('City', size=50, required=True)

    # Dades optatives
    email = fields.Char('eMail', size=60, required=False)
    street2 = fields.Char('Street2', size=50, required=False)    

    # Camps calculats
    age = fields.Integer('Age', compute='_compute_age', store=False)

    # Dades optatives/obligatòries segons condició
    # Les condicions s'han de posar a la vista formulari, no al model.
    tin = fields.Char('Tax ID', size=14) # NIF/CIF; Millor borrar la condició d'aqui
    parent_info = fields.Html('Parent Information') # Informació dels pares en format HTML

    # Relació One2many (Estudiant --> Matrícules).
    enrollment_ids = fields.One2many('school.enrollment', 'student_id', 'Enrollments', required=True)

    @api.depends('first_name', 'last_name')
    def _compute_display_name(self):
        for student in self:
            if student.first_name and student.last_name:
                student.display_name = student.last_name + ", " + student.first_name 
            else:
                student.display_name = ""


    @api.depends('birthdate')
    def _compute_age(self):
        today = fields.Date.today()
        for record in self:
            if record.birthdate:
                record.age = relativedelta(today, record.birthdate).years
            else:
                record.age = 0


class SchoolEnrollment(models.Model):
    _name = 'school.enrollment'
    _description = 'Enrollment Management'

    qualification = fields.Float('Qualification', required=True)

    # Relació Many2one (Matrícula --> Estudiant).
    # Model / Etiqueta
    student_id = fields.Many2one('school.student', 'Estudiant', required=True)

    # Camps related de student_id
    student_phone = fields.Char('Telèfon', related='student_id.phone')
    student_email = fields.Char('Correu-e', related='student_id.email')

    # Relació Many2one (Matrícula --> Edició).
    edition_course_id = fields.Many2one('school.course.edition', 'Edició de curs', required=True)

    date_start = fields.Date('Init Date', related='edition_course_id.date_start')
    date_end = fields.Date('End Date', related='edition_course_id.date_end')

    # Relació One2many (Matrícula --> Assignatures de Matrícula).
    # Model / Camp de SchoolEnrollmentSubject / Etiqueta
    subject_ids = fields.One2many('school.enrollment.subject', 'enrollment_id', 'Subjects', required=True)

    @api.constrains('qualification')
    def _check_qualification(self):
        for enrollment in self:
            if enrollment.qualification:
                if enrollment.qualification > 10 or enrollment.qualification < 0:
                    raise ValidationError (_('Qualification must be a number between 0 and 10'))

    # Sobreescriptura del mètode create
    @api.model_create_multi
    def create(self, vals):
        
        enrollments = super().create(vals)

        for e in enrollments:
            subjects = e.edition_course_id.course_id.course_subject_ids

            for s in subjects:

                enSubject = {}
                enSubject['qualification'] = 0
                enSubject['subject_id'] = s.id
                enSubject['enrollment_id'] = e.id

                self.env['school.enrollment.subject'].create(enSubject)
        
        return enrollments


class SchoolEnrollmentSubject(models.Model):
    _name = 'school.enrollment.subject'
    _description = 'Enrollment Subject Management'

    qualification = fields.Float('Qualification', required=True)

    # Relació Many2one (Assignatura de Matrícula --> Assignatura).
    subject_id = fields.Many2one('school.course.subject', 'Subject', required=True)

    # Relació Many2one (Assignatura de Matrícula --> Matrícula).
    enrollment_id = fields.Many2one('school.enrollment', 'Enrollment', required=True)


    @api.constrains('qualification')
    def _check_qualification(self):
        for es in self:
            if es.qualification:
                if es.qualification > 10 or es.qualification < 0:
                    raise ValidationError (_('Qualification must be a number between 0 and 10'))
            

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Relació inversa per saber quins estudiants depenen d'aquest client
    # Relació One2many (Persona --> Estudiants).
    student_ids = fields.One2many('school.student', 'customer_id', 'Students')