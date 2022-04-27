# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from datetime import datetime

class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_payroll_account = fields.Boolean(
        string="Is payroll account")
