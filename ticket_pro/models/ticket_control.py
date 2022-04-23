# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class TicketControl(models.Model):
    _description = "Ticket Control"
    _name = 'ticket.control'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    name = fields.Char('Código', default="Nuevo", copy=False)
    entry_date = fields.Datetime(
        'Fecha de Entrada', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', string='Usuario',
                              default=lambda self: self.env.user)

    obs = fields.Text('Observación Solución')

    sum_hh = fields.Float("Horas")

    @api.onchange('lines_ids')
    def onchange_lines_ids(self):
        for record in self:
            suma = 0
            for line in record.lines_ids:
                suma = suma + line.hh

            record.sum_hh = suma




    @api.model
    def create(self, vals):
        if vals.get('name', "Nuevo") == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'ticket.control') or "Nuevo"
        ticket = super(TicketControl, self).create(vals)
        return ticket

    lines_ids = fields.One2many(
        'control.line', 'control_id', string='Líneas')

class ControLine(models.Model):
    _name = 'control.line'
    _description = 'Control Line'

    control_id = fields.Many2one(
        'ticket.control', 'control', ondelete='cascade')

    name = fields.Many2one('ticket.pro', string='Ticket')
    obs = fields.Text('Notas')
    hh = fields.Float('Horas')