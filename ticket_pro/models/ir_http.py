# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools.safe_eval import safe_eval


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(IrHttp, self).session_info()
        try:
            raise_ticket = safe_eval(self.env['ir.config_parameter'].sudo().get_param('ticket_pro.raise_ticket'))
        except:
            raise_ticket = False
        result['raise_ticket'] = raise_ticket and self.env.user.raise_ticket
        return result
