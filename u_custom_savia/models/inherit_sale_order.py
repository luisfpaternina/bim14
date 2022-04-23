# -*- coding: utf-8 -*-

import logging
from odoo import api, models, _, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


BUSINESS_LINE = [
    ('wood', 'Savia Wood'),
    ('play', 'Savia Play'),
    ('acuat', 'Savia Acuatic'),
    ('lic', 'Licitación'),
    ('project', 'Obra/Proyecto'),
    ('maint', 'Mantenimiento'),
]

CLIENT_TYPE = [
    ('hotel', 'Hoteles/Camping'),
    ('institution', 'Instituciones'),
    ('private', 'Privado'),    
]


class BimBudget(models.Model):
    _inherit = 'bim.budget'

    business_line = fields.Selection(
            selection=BUSINESS_LINE
    )

    client_type = fields.Selection(
            selection=CLIENT_TYPE
    )

    @api.model
    def create(self, vals):
        project = vals.get('project_id')
        if project:
            project_id = self.env['bim.project'].browse(project)
            partner_id = project_id.customer_id
            if partner_id and partner_id.potencial_client:
                raise ValidationError(
                    _(
                        "Partner is potencial customer, please, uncheck field in customer form."
                    )
                )
        return super(BimBudget, self).create(vals)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    business_line = fields.Selection(
            selection=BUSINESS_LINE
    )

    client_type = fields.Selection(
            selection=CLIENT_TYPE
    )
    project_code = fields.Char()
    contact_person = fields.Many2one(
        'res.partner',       
    )
    start_date = fields.Date()
    finish_date = fields.Date()
    access_states = fields.Char()
    others = fields.Char()

    @api.model
    def default_get(self, default_fields):
        rec = super(SaleOrder, self).default_get(default_fields)
        if 'opportunity_id' in default_fields:
            lead = self.env['crm.lead'].browse(rec.get('opportunity_id'))
            rec['business_line'] = lead.business_line or None
            rec['client_type'] = lead.client_type or None
        return rec

    def action_confirm(self):
        self.ensure_one()
        if self.partner_id.potencial_client:
            raise ValidationError(
                _(
                    "Partner is potencial customer, please, uncheck field in customer form."
                )
            )
        super(SaleOrder, self).action_confirm()

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update(
            {
                'business_line': self.business_line,
                'client_type': self.client_type,
            }
        )
        return res
    