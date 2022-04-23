# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError

class TicketPro(models.Model):
    _description = "Ticket Pro"
    _name = 'ticket.pro'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    @api.model
    def _needaction_domain_get(self):
        return [('state', '!=', 'resuelto')]

    name = fields.Char('Código', default="Nuevo", copy=False)
    title = fields.Char('Título', size=100)
    obs = fields.Text('Observación')
    obs_solucion = fields.Text('Solución')
    obs_stop = fields.Text('Stop Note')
    entry_date = fields.Datetime(
        'Fecha de Entrada', default=fields.Datetime.now)
    end_date = fields.Datetime('F. Salida')
    end_will_end = fields.Datetime('Fecha Prevista', tracking=True)
    user_id = fields.Many2one('res.users', string='Creado',
                              default=lambda self: self.env.user)

    note_id = fields.Many2one('ticket.notes')

    hours = fields.Integer("Horas")
    price = fields.Float("Precio")

    category_id = fields.Many2one('ticket.category', string='Categoría')
    ticket_id = fields.Many2one('ticket.pro', string='Relacionado')
    project_id = fields.Many2one('ticket.project', string='Proyecto')

    numero_veces = fields.Integer('# Veces', default=1)

    advance = fields.Integer('% Avance' ,tracking=True)

    user_error_id = fields.Many2one(
        'res.users', string='Usuario', default=lambda self: self.env.user)

    user_work_id = fields.Many2one('res.users', string='Asignado', tracking=True)

    char_note = fields.Char('Notas')
    module_odoo = fields.Char('Módulo')

    comprobante_01_name = fields.Char("Adjunto")
    comprobante_01 = fields.Binary(
        string='Adjunto',
        copy=False,
        help='Adjunto')

    company_id = fields.Many2one(
        'res.company', string="Compañia", required=True,
        default=lambda self: self.env.user.company_id.id)

    type = fields.Selection([
        ('internal', 'Interno'),
        ('external', 'Público')],
        string='Tipo', index=True, default='external',
        copy=False)

    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('stop', 'Espera'),
        ('aprobado', 'Aprobado'),
        ('trabajando', 'Trabajando'),
        ('actualizar', 'Actualizar'),
        ('resuelto', 'Resuelto'),
        ('calificado', 'Calificado')],
        string='Estatus', index=True, readonly=True, default='borrador',
        tracking=True,
        copy=False)

    clasificacion = fields.Selection([
        ('soporte', 'Soporte'),
        ('desarrollo', 'Desarrollo')],
        string='Clasificación', index=True, default='soporte', copy=False)

    calificacion = fields.Selection([
        ('0', 'Malo'),
        ('1', 'Regular'),
        ('2', 'Bueno'),
        ('3', 'Excelente')],
        string='Calificación', default='0', copy=False)

    obs_calificacion = fields.Text('Nota Calificación')

    prioridad = fields.Selection(
        [('baja', 'Baja'),
         ('media', 'Media'),
         ('alta', 'Alta')],
        default='baja', copy=False)

    user_task_id = fields.Many2one(
        'user.task', string='U.T', compute='_compute_user_task_id', index=True)

    contract_type = fields.Selection(string='Tipo C.', selection=[('c', 'Contrato'), ('e', 'Evolutivo')], default='e')
    question_ids = fields.One2many('ticket.questions.and.answers', 'task_id', string='Preguntas y Respuestas')

    def _compute_user_task_id(self):
        control_line_obj = self.env['progress.control.line']
        for record in self:
            progress_control_obj = control_line_obj.search([('task_id','=',record.id)], limit=1)
            if progress_control_obj:
                record.user_task_id = progress_control_obj.progress_control_id.user_task_id.id
            else:
                record.user_task_id = False

    def exe_autorizar(self):
        for record in self:
            record.state = 'aprobado'
            record.message_post(
                body=_("Ticket Aprobado por: %s") % record.env.user.name)

    def exe_stop(self):
        for record in self:
            record.state = 'stop'
            record.message_post(
                body=_("Ticket a Stop por: %s") % record.env.user.name)

    def exe_actualizar(self):
        for record in self:
            record.state = 'actualizar'
            record.message_post(
                body=_("Ticket a Actualizar por: %s") % record.env.user.name)

    def exe_work(self):
        for record in self:
            record.user_work_id = record.env.user
            record.state = 'trabajando'
            record.message_post(
                body=_("Iniciando el trabajo: %s") % record.env.user.name)

    def exe_resuelto(self):
        template = self.env.ref('ticket_pro.email_ticket_close')
        attach_obj = self.env['ir.attachment']
        for record in self:
            record.user_work_id = record.env.user
            record.state = 'resuelto'
            record.message_post(body=_("Nota Solución: %s") %
                                record.obs_solucion)
            record.end_date = fields.Datetime.now()

            """Enviamos el Email"""

            if record.comprobante_01:
                attachment = attach_obj.create({
                    'name': record.comprobante_01_name,
                    'datas': record.comprobante_01,
                    'store_fname': record.comprobante_01_name,
                    'res_model': 'ticket.pro',
                    'type': 'binary'
                })
                template.attachment_ids = [(6, 0, attachment.ids)]
            mail = template.send_mail(record.id, force_send=True)  # envia mail
            if mail:
                record.message_post(
                    body=_("Aviso Ticket Terminado: %s" % record.category_id.name))

    def exe_abrir(self):
        attach_obj = self.env['ir.attachment']
        template = self.env.ref('ticket_pro.email_ticket_pro_open')
        for record in self:
            record.numero_veces = record.numero_veces + 1
            record.state = 'borrador'
            record.message_post(body=_("Se Abre de nuevo: %s") %
                                record.env.user.name)

            if self.comprobante_01:
                attachment = attach_obj.create({
                    'name': self.comprobante_01_name,
                    'datas': self.comprobante_01,
                    'store_fname': self.comprobante_01_name,
                    'res_model': 'ticket.pro',
                    'type': 'binary'
                })
                template.attachment_ids = [(6, 0, attachment.ids)]
            mail = template.send_mail(self.id, force_send=True)  # envia mail
            if mail:
                self.message_post(
                    body=_("Enviado email a Soporte: %s" % self.category_id.name))

    def exe_close(self):
        if self.calificacion == '0':
            raise ValidationError(
                "Por favor califica nuestro trabajo así mejoramos con tu ayuda, muchas gracias.")
        for record in self:
            record.state = 'calificado'
            record.message_post(body=_("Calificado como: %s") %
                                record.calificacion)

    @api.model
    def retrieve_dashboard(self):
        self.env.cr.execute("""
        SELECT (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
        ) total_open,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_open_this_year,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date)
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_open_this_month,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date) - 1
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_open_last_month,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
            AND DATE_PART('week', entry_date) = DATE_PART('week', current_date)
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date)
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_open_this_week,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
            AND DATE_PART('week', entry_date) = DATE_PART('week', current_date) - 1
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date)
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_open_last_week,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state not in ('resuelto', 'calificado')
            AND prioridad = 'alta'
        ) total_open_high_priority,

        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
        ) total_done,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_done_this_year,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date)
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_done_this_month,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date) - 1
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_done_last_month,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
            AND DATE_PART('week', entry_date) = DATE_PART('week', current_date)
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date)
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_done_this_week,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
            AND DATE_PART('week', entry_date) = DATE_PART('week', current_date) - 1
            AND DATE_PART('month', entry_date) = DATE_PART('month', current_date)
            AND DATE_PART('year', entry_date) = DATE_PART('year', current_date)
        ) total_done_last_week,
        (
            SELECT count(id)
            FROM ticket_pro
            WHERE state in ('resuelto', 'calificado')
            AND prioridad = 'alta'
        ) total_done_high_priority
        """)
        return self.env.cr.dictfetchall()[0]

    @api.model
    def create(self, vals):
        if vals.get('name', "Nuevo") == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'ticket.pro') or "Nuevo"
        if 'category_id' not in vals:
            vals['category_id'] = self.env.ref('ticket_pro.ticket_proc_01').id
        ticket = super(TicketPro, self).create(vals)
        template = self.env.ref('ticket_pro.email_ticket_pro')
        attachment = False
        if ticket.comprobante_01:
            attachment = self.env['ir.attachment'].create({
                'name': ticket.comprobante_01_name,
                'datas': ticket.comprobante_01,
                'store_fname': ticket.comprobante_01_name,
                'res_model': 'ticket.pro',
                'type': 'binary'
            })
        template.attachment_ids = [
            (6, 0, attachment.ids)] if attachment else [(5,)]
        mail = template.send_mail(ticket.id, force_send=True)  # envia mail
        if mail:
            ticket.message_post(
                body=_("Enviado email a Soporte: %s" % ticket.category_id.name))
        remote_ids = self.env['ticket.server'].search([]).create_remote_tickets(ticket)
        for server, remote_id in remote_ids.items():
            ticket.message_post(body=f'Creado <a href="{server.url}/web#id={remote_id}&model=ticket.pro&view_type=form" target="_blank">Ticket {ticket.name}</a> en servidor remoto <a href="{server.url}" alt="Servidor remoto">{server.url}</a>')
        return ticket

    def unlink(self):
        for record in self:
            if self.env.user.has_group('ticket_pro.ticket_pro_user_delete'):
                super(TicketPro, record).unlink()
            else:
                raise UserError("Usted no tiene permiso para borrar tickets")
        return True


class TicketQuestionsandAnswers(models.Model):
    _name = 'ticket.questions.and.answers'
    _description = 'Ticket Questions and Answers'

    task_id = fields.Many2one(
        'ticket.pro', 'Ticket', ondelete='cascade')
    question = fields.Char('Pregunta')
    answer = fields.Char('Respuesta')
    user_id = fields.Many2one(
        'res.users', string='Usuario', default=lambda self: self.env.user)
    entry_date = fields.Datetime(
        'Fecha', default=fields.Datetime.now)

