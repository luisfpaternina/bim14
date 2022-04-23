# -*- coding: utf-8 -*-
{
    'name': "Unoobi | Savia personalization",
    'summary': """
        Savia Personalization.
    """,
    'description': """
        Savia Personalization
    """,
    'sequence': 50,
    'author': "UNOOBI",
    'category': 'Contact',
    'version': '1.0',
    'depends': ['base', 'contacts', 'crm', 'account', 'stock', 'sale', 'purchase', 'base_bim_2'],
    'data': [
        # ==== SECURITY
        'security/ir.model.access.csv',
        'security/sale_security.xml',
        'security/security_groups_savia.xml',
        # === VIEWS
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/crm_lead.xml',
        'views/inherit_sale_views.xml',
        'views/account_move_views.xml',
        'views/bim_budget_view.xml',
    ],
    'demo': [],
}
