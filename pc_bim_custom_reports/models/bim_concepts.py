from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import ValidationError
import logging


class BimConcepts(models.Model):
    _inherit = 'bim.concepts'
    
    percentage_on_sale = fields.Float(
        string="Percentage on sale")
    percentage_sale_value = fields.Float(
        string="%",
        related="percentage_on_sale")
    cost_of_sale = fields.Float(
        string="Cost of sale",
        compute="calculated_cost_of_sale")
    percentage_value = fields.Float(
        string="Percentaje value",
        compute="calculated_cost_of_sale")
    

    @api.constrains('percentage_on_sale')
    def validate_percentage_on_sale(self):
    # FUNCIÓN PARA VALIDAR QUE EL PORCENTAJE SEA DE 0 A 100%
        for record in self:
            if record.percentage_on_sale > 100 or record.percentage_on_sale < 0:
                raise ValidationError(_('The percentage value must be between 0 and 100'))
    
    @api.depends('percentage_on_sale', 'amount_fixed')
    def calculated_cost_of_sale(self):
    # CALCULAR COSTO DE VENTA Y PORCENTAJE
        for record in self:
            if record.amount_fixed > 0:
                subtotal = (record.percentage_on_sale * record.amount_fixed) / 100
                record.percentage_value = subtotal
                total = subtotal + record.amount_fixed
                record.cost_of_sale = total
            else:
                record.cost_of_sale = 0
                record.percentage_value = 0
