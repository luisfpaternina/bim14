from odoo import models, fields, api, _

class BimProject(models.Model):
    _inherit = 'bim.project'

    has_analytic_account = fields.Boolean(
        string="Has analytic account",
        compute="compute_has_analytic_account")
    
    @api.depends('name','customer_id','analytic_id')
    def compute_has_analytic_account(self):
        if self.analytic_id:
            self.has_analytic_account = True
        else:
            self.has_analytic_account = False
    