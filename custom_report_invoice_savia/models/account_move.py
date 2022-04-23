from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    paidtate_ids = fields.One2many(
        comodel_name='bim.paidstate',
        inverse_name='invoice_id',
        string='Estados de Pago'
    )
    paidstate_by_bim_project_ids = fields.Many2many(
        comodel_name='bim.paidstate',
        compute='_compute_paidstate_by_bim_project_ids',
        string='Estado de Pago por Obra',
    )
    bim_masive_certification_ids = fields.Many2many(
        'bim.massive.certification.by.line',
        string='Certificación masiva',
    )
    bim_masive_chapter_ids = fields.Many2many(
        'bim.massive.chapter.certification',
        string='Certificación capítulo',
    )

    @api.depends('paidtate_ids')
    def _compute_paidstate_by_bim_project_ids(self):
        for move in self:
            move.paidstate_by_bim_project_ids = move.paidtate_ids.filtered(
                lambda x: x.project_id == move.project_id
                and x.state == 'invoiced'
            )

    @api.onchange('project_id')
    def domain_bim_masive_chapter_ids(self):
        for record in self:
            if record.project_id:
                return {'domain': {'bim_masive_chapter_ids': [('project_id', '=', record.project_id.id)]}}
            else:
                return {'domain': {'bim_masive_chapter_ids': []}}

    @api.onchange('project_id')
    def domain_bim_masive_certification_ids(self):
        for record in self:
            if record.project_id:
                return {'domain': {'bim_masive_certification_ids': [('project_id', '=', record.project_id.id)]}}
            else:
                return {'domain': {'bim_masive_certification_ids': []}}
