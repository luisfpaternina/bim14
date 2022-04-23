# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, SUPERUSER_ID

_logger = logging.getLogger(__name__)

PROYEC_TYPE = [
    ('standard', 'Standart Product'),
    ('project', 'Project'),
]

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


class Lead(models.Model):
    _inherit = "crm.lead"

    # Description
    family_id = fields.Many2one(
        "res.partner.family", index=True, tracking=10
    )
    
    

    project_type = fields.Selection(
        selection=PROYEC_TYPE
    )

    business_line = fields.Selection(
            selection=BUSINESS_LINE
    )

    client_type = fields.Selection(
            selection=CLIENT_TYPE
    )

    tender_date = fields.Datetime()

    users_ids = fields.Many2many(
        'res.users',
        compute='_compute_users_ids'
    )

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super(Lead, self)._prepare_customer_values(partner_name, is_company=is_company, parent_id=parent_id)
        res['family_id'] = self.family_id.id or None        
        return res
    
    def handle_salesmen_assignment(self, user_ids=None, team_id=False):
        """ Assign salesmen and salesteam to a batch of leads.  If there are more
        leads than salesmen, these salesmen will be assigned in round-robin. E.g.
        4 salesmen (S1, S2, S3, S4) for 6 leads (L1, L2, ... L6) will assigned as
        following: L1 - S1, L2 - S2, L3 - S3, L4 - S4, L5 - S1, L6 - S2.

        :param list user_ids: salesmen to assign
        :param int team_id: salesteam to assign
        """
        user = self.user_id
        super(Lead, self).handle_salesmen_assignment(user_ids=user_ids, team_id=team_id)
        self.user_id = user

    @api.depends('tag_ids')
    def _compute_users_ids(self):
        for lead in self:
            if lead.tag_ids:
                lead.users_ids = self.env['res.users'].search(
                    [('tag_id', 'in', lead.tag_ids.ids)]
                )
            else:
                lead.users_ids = self.env['res.users'].search(
                    []
                )
       
    @api.onchange('partner_id')
    def _change_partner_id(self):
        if self.partner_id:
            self.family_id = self.partner_id.family_id
        else:
            self.family_id = None
    
    @api.onchange('family_id')
    def _change_family_id(self):
        if self.family_id:
            comercial = self.env['res.users'].search(
                [
                    ('partner_id.family_id', '=', self.family_id.id)
                ], limit=1
            )
            if comercial:
                self.user_id = comercial
    
    # @api.onchange('tag_ids')
    # def change_tag_ids(self):
    #     if self.tag_ids:
    #         user_ids = self.env['res.users'].search(
    #             [('tag_id', 'in', self.tag_ids.ids)]
    #         )
    #         self.user_id = user_ids and user_ids[0] or False
    #         return {'domain':{'user_id':[('id','in', user_ids.ids)]}}
    #     else:
    #         self.user_id = False
    #         return {'domain':{'user_id':[('id','!=', -1)]}}
    
    def action_sale_quotations_new(self):
        action = super(Lead, self).action_sale_quotations_new()
        ctx = action['context']
        ctx.update(
            {
                'default_business_line': self.business_line,
                'default_client_type': self.client_type,
            }
        )
        action['context'] = ctx
        return action
    
    def action_view_sale_quotation(self):
        action = super(Lead, self).action_view_sale_quotation()
        return action