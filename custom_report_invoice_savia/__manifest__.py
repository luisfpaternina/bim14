# Copyright 2021 Process Control (http://www.processcontrol.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    'name': 'Custom Report Invoice Savia',
    'summary': 'Custom module for Savia\'s invoices.',
    'version': '14.0.1.0.0',
    'category': 'Invoice',
    'author': 'Óscar Soto, Process Control',
    'license': 'AGPL-3',
    'depends': [
        'account',
        'base_bim_2',
    ],
    'data': [
        'data/paperformat.xml',
        'views/account_move.xml',
        'reports/report_invoice_document.xml',
    ],
}
