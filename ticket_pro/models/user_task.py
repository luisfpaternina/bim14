# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

class UserTask(models.Model):
    _description = "User Task"
    _name = 'user.task'
    name = fields.Char(string='Nombre')