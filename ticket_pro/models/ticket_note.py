# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class TicketNotes(models.Model):
    _description = "Ticket Notes"
    _name = 'ticket.notes'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _order = 'id desc'

    name = fields.Char(string='Secuencia', default="Nuevo", copy=False)
    title = fields.Char(string='Título')
    date_note = fields.Date(string='Fecha', default=fields.Date.today)
    note = fields.Text(string='Nota')
    ticket_ids = fields.One2many('ticket.pro', 'note_id')
    ticket_count = fields.Integer(string='Tickets', compute='compute_tickets')

    @api.model
    def create(self, vals):
        if vals.get('name', "Nuevo") == "Nuevo":
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'ticket.notes') or "Nuevo"
        return super(TicketNotes, self).create(vals)

    def compute_tickets(self):
        for record in self:
            record.ticket_count = len(record.ticket_ids)

    def view_tickets(self):
        ticket_ids = self.mapped('ticket_ids')
        action = self.env.ref('ticket_pro.action_ticket_pro').read()[0]
        if len(ticket_ids) == 1:
            action['views'] = [(False, "form")]
            action['res_id'] = self.ticket_ids.id
        elif len(ticket_ids) > 1:
            action['domain'] = [('id', 'in', ticket_ids.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action