# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
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


class AccountMove(models.Model):
    _inherit = "account.move"

    revised = fields.Selection(
        [('si', 'Si'), ('no', 'No')],
        tracking=True
    )

    business_line = fields.Selection(
            selection=BUSINESS_LINE
    )

    client_type = fields.Selection(
            selection=CLIENT_TYPE
    )

    @api.constrains('partner_id')
    def _check_potential_partner(self):
        for move in self:
            if move.move_type not in ('in_invoice', 'in_refund', 'in_receipt', 'entry') and move.partner_id.potencial_client:
                raise ValidationError(
                    _(
                        "Partner is potencial customer, please, uncheck field in customer form."
                    )
                )
    
