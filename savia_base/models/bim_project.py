# -*- coding: utf-8 -*-
# Part of Ynext. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class BimProject(models.Model):
    _inherit = 'bim.project'

    client_type = fields.Selection([('hotel', 'Hoteles/Camping'),('institution', 'Instituciones'),
                                    ('private', 'Privado')], string='Client Type')
    business_line = fields.Selection([('wood', 'Savia Wood'),('play', 'Savia Play'),
                                      ('acuat', 'Savia Acuatic'),('lic', 'Licitación'),
                                      ('project', 'Obra/Proyecto'),('maint', 'Mantenimiento')], string='Business Line')

    def action_view_budgets(self):
        budgets = self.mapped('budget_ids')
        action = self.env.ref('base_bim_2.action_bim_budget').sudo().read()[0]
        if len(budgets) > 0:
            action['domain'] = [('id', 'in', budgets.ids)]
            action['context'] = {'default_project_id': self.id,
                                 'default_def_client_type': self.client_type,
                                 'default_def_business_line': self.business_line,
                                 'default_currency_id': self.currency_id.id}
            return action
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': 'New Budget',
                'res_model': 'bim.budget',
                'view_mode': 'form',
                'target': 'current',
                'context': {'default_project_id': self.id,
                            'default_def_client_type': self.client_type,
                            'default_def_business_line': self.business_line,
                            'default_currency_id': self.currency_id.id}
            }
