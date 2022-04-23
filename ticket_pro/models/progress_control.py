# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProgressControl(models.Model):
    _description = "Progress Control"
    _name = 'progress.control'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    name = fields.Char('Código', default="Nuevo", copy=False)
    entry_date = fields.Datetime(
        'Fecha de Entrada', default=fields.Datetime.now)
    end_date = fields.Datetime(
        'Fecha Fin')
    end_pre_date = fields.Datetime(
        'Fecha Prevista de Salida')
    user_id = fields.Many2one('res.users', string='Creado',
                              default=lambda self: self.env.user)
    obs = fields.Text('Observación')

    user_task_id = fields.Many2one(
        'user.task', 'User Task', ondelete='cascade')

    @api.model
    def create(self, vals):
        if vals.get('name', "Nuevo") == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'progress.control') or "Nuevo"
        ticket = super(ProgressControl, self).create(vals)
        return ticket

    line_ids = fields.One2many(
        'progress.control.line', 'progress_control_id', string='Líneas de Control')

    line_count = fields.Integer("Cantidad de Ticket", compute='_compute_giveme_count')
    line_end_count = fields.Integer("Tickets Resueltos", compute='_compute_giveme_end_count')
    ticket_pend = fields.Integer("Tickets Pendientes", compute='_compute_ticket_pend')


    def _compute_giveme_count(self):
        for record in self:
            record.line_count = len(record.line_ids)

    def _compute_giveme_end_count(self):
        for record in self:
            line_end_count = 0
            for line in record.line_ids:
                if line.task_id.state in ['resuelto','calificado']:
                    line_end_count += 1
            record.line_end_count = line_end_count

    def _compute_ticket_pend(self):
        for record in self:
            record.ticket_pend = record.line_count - record.line_end_count



class ProgressControlLine(models.Model):
    _name = 'progress.control.line'
    _description = 'Líneas de Control de Procesos'
    task_id = fields.Many2one(
        'ticket.pro', 'Ticket', ondelete='cascade')
    title = fields.Char('Título', size=100, related='task_id.title')
    entry_date = fields.Datetime(
        'Fecha de Entrada', default=fields.Datetime.now)
    cant_horas = fields.Float('Cantidad Horas')
    state = fields.Selection(string='Estatus', related='task_id.state')
    progress_control_id = fields.Many2one(
        'progress.control', 'Progress Control', ondelete='cascade')
