# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, date


class BimBudget(models.Model):
    _inherit = 'bim.budget'

    def_client_type = fields.Selection([('hotel', 'Hoteles/Camping'),('institution', 'Instituciones'),
                                        ('private', 'Privado')], string='Client Type')
    def_business_line = fields.Selection([('wood', 'Savia Wood'),('play', 'Savia Play'),
                                          ('acuat', 'Savia Acuatic'),('lic', 'Licitación'),
                                          ('project', 'Obra/Proyecto'),('maint', 'Mantenimiento')], string='Business Line')
    project_code = fields.Char('Project Code', required=True)
    delivery_address = fields.Char('Delivery Address', required=True)
    partner_id = fields.Many2one('res.partner', related='project_id.customer_id')
    contact_person = fields.Many2one('res.partner', string='Contact Person', domain="['|',('parent_id','=',partner_id),('id','=',partner_id)]", required=True)
    invoice_address = fields.Many2one('res.partner', string='Invoice Address', domain="['|',('parent_id','=',partner_id),('id','=',partner_id)]", required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    access_states = fields.Char('Access States', required=True)
    other_info = fields.Text('Other', required=True)
