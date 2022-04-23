# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools

_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    code = fields.Char()
    