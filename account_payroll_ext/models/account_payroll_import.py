# -*- coding: utf-8 -*-
from markupsafe import string
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
from datetime import datetime


class AccountPayrollImport(models.Model):
    _name = 'account.payroll.import'
    _inherit = 'mail.thread'
    _description = 'Account payroll import'

    name = fields.Char(
        string="Name")
    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee")
    employee_name = fields.Char(
        string="Employee name",
        related="employee_id.name")
    project_id = fields.Many2one(
        'bim.project',
        string="Project BIM")
    date = fields.Date(
        string="Date")
    import_line_ids = fields.One2many(
        'account.payroll.import.lines',
        'import_id',
        string="Import lines")
    state = fields.Selection([
        ('draft','Draft'),
        ('send','send')],string="State",default="draft")
    

    def send_records(self):
        for record in self:
            if record.employee_id:
                record.write({'state': 'send'})
                move_payroll_obj = record.env['account.move.payroll'].create({
                    'employee_id': record.employee_id.id,
                    'date': record.date,
                    })


class AccountPayrollImportLines(models.Model):
    _name = 'account.payroll.import.lines'
    _inherit = 'mail.thread'
    _description = 'Account payroll import lines'

    project_id = fields.Many2one(
        'bim.project',
        string="Project BIM")
    debit = fields.Float(
        string="Debit")
    credit = fields.Float(
        string="Credit")
    amount = fields.Float(
        string="Import")
    import_id = fields.Many2one(
        'account.payroll.import',
        string="Accont payroll import")
    account_id = fields.Many2one(
        'account.account',
        string="Account")
