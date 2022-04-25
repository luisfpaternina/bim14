# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date
import logging


class BimBudget(models.Model):
    _inherit = 'bim.budget'
