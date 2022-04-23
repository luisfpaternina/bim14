# -*- coding: utf-8 -*-


from odoo import api, models, fields, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    total_cost = fields.Float(compute='compute_picking_total_cost', store=True)

    @api.depends('move_ids_without_package.product_cost','move_ids_without_package.quantity_done')
    def compute_picking_total_cost(self):
        for picking in self:
            total = 0
            for line in picking.move_ids_without_package:
                total += line.product_cost * line.quantity_done
            picking.total_cost = total

    def update_picking_total_cost(self):
        for picking in self:
            for line in picking.move_ids_without_package:
                if line.purchase_id:
                    line.product_cost = line._find_purchase_price(line.purchase_id)
                elif line.product_id:
                    line.product_cost = line.product_id.standard_price

class StockMove(models.Model):
    _inherit = 'stock.move'
    product_cost = fields.Float()
    purchase_id = fields.Many2one('purchase.order')

    @api.model
    def create(self, vals):
        move = super().create(vals)
        if move.product_id:
            move.product_cost = move.product_id.standard_price
        if move.purchase_id:
            price = move._find_purchase_price(move.purchase_id)
            if price > 0:
                move.product_cost = price
        elif move.product_id and move.picking_id and move.picking_id.purchase_id:
            price = move._find_purchase_price(move.picking_id.purchase_id)
            if price > 0:
                move.product_cost = price
        return move

    def _find_purchase_price(self, purchase_id):
        price = 0
        purchase_lines = purchase_id.order_line.filtered_domain([('product_id','=',self.product_id.id)])
        if purchase_lines:
            price = purchase_lines[0].price_unit
        return price