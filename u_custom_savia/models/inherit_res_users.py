# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from random import randint


class Users(models.Model):
    _inherit = 'res.users'

    tag_id = fields.Many2one(
        'crm.tag'
    )
