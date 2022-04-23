# -*- coding: utf-8 -*-

import logging
from odoo import api, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.constrains('partner_id')
    def _check_potential_partner(self):
        for move in self:
            if move.picking_type_code != 'incoming' and move.partner_id.potencial_client:
                raise ValidationError(
                    _(
                        "Partner is potencial customer, please, uncheck field in customer form."
                    )
                )
    