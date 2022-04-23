# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from random import randint


class ResPartner(models.Model):
    _inherit = 'res.partner'

    family_id = fields.Many2one(
        "res.partner.family"
    )
    potencial_client = fields.Boolean(default=True)

    @api.constrains("potencial_client", "vat", "street")
    def _constraint_potencial_client(self):
        for partner in self:
            if not partner.potencial_client and (not partner.vat or not partner.street):
                raise ValidationError("Si no es cliente potencial debe tener ingresado los datos fiscales")


class PartnerFamily(models.Model):
    _name = 'res.partner.family'
    _description = 'Partner Family'
    _order = 'name'
    _parent_store = True

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string='Family Name', required=True, translate=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    parent_id = fields.Many2one('res.partner.family', string='Parent Family', index=True, ondelete='cascade')
    child_ids = fields.One2many('res.partner.family', 'parent_id', string='Child Family')
    active = fields.Boolean(default=True, help="The active field allows you to hide the family without removing it.")
    parent_path = fields.Char(index=True)
    
    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('You can not create recursive family.'))

    def name_get(self):
        """ Return the categories' display name, including their direct
            parent by default.

            If ``context['partner_family_display']`` is ``'short'``, the short
            version of the family name (without the direct parent) is used.
            The default is the long version.
        """
        if self._context.get('partner_family_display') == 'short':
            return super(PartnerFamily, self).name_get()

        res = []
        for family in self:
            names = []
            current = family
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((family.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
