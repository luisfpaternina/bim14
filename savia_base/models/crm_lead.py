# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models

class CrmLead(models.Model):
    _inherit = 'crm.lead'


    def action_view_bim_project(self):
        action = self.env.ref('base_bim_2.action_bim_proect').sudo().read()[0]
        action['context'] = {
            'search_default_state': 1,
            'search_default_partner_id': self.partner_id.id,
            'default_customer_id': self.partner_id.id,
            'default_nombre': self.name,
            'default_user_id': self.user_id.id,
            'default_opportunity_id': self.id,
            'default_client_type': self.client_type,
            'default_business_line': self.business_line,
        }
        action['domain'] = [('opportunity_id', '=', self.id)]
        quotations = self.mapped('bim_order_ids')
        if len(quotations) == 1:
            action['views'] = [(self.env.ref('base_bim_2.view_form_bim_project').id, 'form')]
            action['res_id'] = quotations.id
        return action

