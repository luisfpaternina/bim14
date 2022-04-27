{
    'name': 'account payroll ext',

    'version': '14.0.0.0',

    'author': "ProcessControl",

    'contributors': ['Luis Felipe Paternina'],

    'website': "www.processcontrol.es",

    'category': 'Account',

    'depends': [

        'account_accountant',
        'hr',
        'hr_attendance',
        'bim_project',
        'base_bim_2',
        'l10n_es',
    ],

    'data': [
        
        'data/sequences.xml',
        'data/ir_actions_server.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/account_move_payroll.xml',
        'views/account_payroll_import.xml',
        'views/account_account.xml',
               
    ],
    'installable': True
}
