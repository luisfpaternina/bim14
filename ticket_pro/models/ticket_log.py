# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TicketLog(models.Model):
    _description = "Ticket Log"
    _name = 'ticket.log'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    @api.model
    def _needaction_domain_get(self):
        return [('name', '!=', '')]


    name = fields.Char('Código', default="Nuevo", copy=False)
    entry_date = fields.Datetime(
        'Fecha de Entrada', default=fields.Datetime.now)

    borrador = fields.Integer('Borrador')
    aprobado = fields.Integer('Aprobado')
    trabajando = fields.Integer('Trabajando')
    resuelto = fields.Integer('Resuelto')
    calificado = fields.Integer('Calificado')
    total_pendiente = fields.Integer('Total Pendiente')

    total = fields.Integer('Total')

    project_id = fields.Many2one('ticket.project', string='Proyecto')

    type = fields.Selection([
        ('manual', 'Manual'),
        ('automatico', 'Automático'),
        ('trabajando', 'Trabajando')],
        string='Estatus', index=True, readonly=True, default='manual',
        copy=False)

    @api.model
    def cron_start_create(self):
        project_obj = self.env['ticket.project'].search([('log', '=', True)])
        ticket_obj = self.env['ticket.pro']
        log_obj = self.env['ticket.log']
        if project_obj:
            for project in project_obj:
                borrador = ticket_obj.search_count(
                    [('project_id', '=', project.id), ('state', '=', 'borrador')])
                aprobado = ticket_obj.search_count(
                    [('project_id', '=', project.id), ('state', '=', 'aprobado')])
                trabajando = ticket_obj.search_count(
                    [('project_id', '=', project.id), ('state', '=', 'trabajando')])
                resuelto = ticket_obj.search_count(
                    [('project_id', '=', project.id), ('state', '=', 'resuelto')])
                calificado = ticket_obj.search_count(
                    [('project_id', '=', project.id), ('state', '=', 'calificado')])

                total = borrador + aprobado + trabajando + resuelto + calificado
                total_pendiente = total - resuelto - calificado

                log = log_obj.sudo().create({
                    'borrador': borrador,
                    'aprobado': aprobado,
                    'trabajando': trabajando,
                    'resuelto': resuelto,
                    'calificado': calificado,
                    'total_pendiente': total_pendiente,
                    'total': total,
                    'type': 'automatico',
                    'project_id': project.id,
                })

    @api.model
    def create(self, vals):
        if vals.get('name', "Nuevo") == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'ticket.pro') or "Nuevo"
        ###
        ticket = super(TicketLog, self).create(vals)
        return ticket