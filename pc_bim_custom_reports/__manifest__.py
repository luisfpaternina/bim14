{
    'name': 'pc BIM custom reports',

    'version': '14.0.0.0',

    'author': "ProcessControl",

    'contributors': ['Luis Felipe Paternina'],

    'website': "www.processcontrol.es",

    'category': 'reports',

    'depends': [

        'base',
        'bim_project',
        'base_bim_2',
    ],

    'data': [
        
        'security/ir.model.access.csv',
        'wizard/bim_certification_report.xml',
        'views/bim_budget.xml',
        'reports/certification_report.xml',
        'reports/comparative_report.xml',
        'reports/origin_certification_report.xml',
               
    ],
    'installable': True
}
