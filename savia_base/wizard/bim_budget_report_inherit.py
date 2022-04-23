from odoo import models, fields, api, _
import xlwt
from io import BytesIO
import base64
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class BimBudgetReportWizard(models.TransientModel):
    _inherit = "bim.budget.report.wizard"

    def check_report_xls(self):
        budget = self.budget_id
        workbook = xlwt.Workbook(encoding="utf-8")
        worksheet = workbook.add_sheet('Budget')
        file_name = 'Budget'
        style_title = xlwt.easyxf('font: name Times New Roman 180, color-index black, bold on; align: wrap yes, horiz center;')
        style_filter_title = xlwt.easyxf('font: color-index black, bold on; align: wrap yes, horiz center;')
        style_filter_title2 = xlwt.easyxf('align: wrap yes, horiz center;')
        style_summary = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin;')
        style_border_table_top = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: bold on; align: wrap yes, horiz center;')
        style_border_table_bottom = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin; font: bold on;')
        style_border_table_details_chapters = xlwt.easyxf('borders: bottom thin;')
        style_border_table_details_departed = xlwt.easyxf('borders: bottom thin;')
        style_border_table_details = xlwt.easyxf('borders: bottom thin;')

        if self.display_type == 'summary':
            worksheet.write_merge(0, 0, 0, 11, _("SUMMARY BUDGET REPORT"), style_title)
            worksheet.write_merge(1,1,0,3, _("Project"),style_filter_title)
            worksheet.write_merge(2,2,0,3, budget.project_id.nombre,style_filter_title2)
            worksheet.write_merge(1,1,4,8, _("Budget Number"),style_filter_title)
            worksheet.write_merge(2,2,4,8, budget.code,style_filter_title2)
            worksheet.write_merge(1,1,9,11, _("Date of Issue"),style_filter_title)
            worksheet.write_merge(2,2,9,11, budget.create_date.strftime('%d/%m/%Y'),style_filter_title2)

            row = 4
            row_to = row + 1

            if self.total_type == 'normal':
                mt = round(self.get_total('material'),2)
                mo = round(self.get_total('labor'),2)
                eq = round(self.get_total('equip'),2)
                tot = mt + mo + eq
                others = round((budget.balance - tot),2)
                total = round(budget.balance,2)

                worksheet.write_merge(row,row_to,0,3, _("Total Materials"), style_summary)
                worksheet.write_merge(row,row_to,4,5, mt, style_summary)
                row += 2
                row_to = row + 1
                worksheet.write_merge(row,row_to,0,3, _("Total Labor"), style_summary)
                worksheet.write_merge(row,row_to,4,5, mo, style_summary)
                row += 2
                row_to = row + 1
                worksheet.write_merge(row,row_to,0,3, _("Total Equipment"), style_summary)
                worksheet.write_merge(row,row_to,4,5, eq, style_summary)
                row += 2
                row_to = row + 1
                worksheet.write_merge(row,row_to,0,3, _("Other"), style_summary)
                worksheet.write_merge(row,row_to,4,5, others, style_summary)
                row += 2
                row_to = row + 1
                worksheet.write_merge(row,row_to,0,3, "TOTAL", style_summary)
                worksheet.write_merge(row,row_to,4,5, total, style_summary)
                row += 1

            else:
                for asset in budget.asset_ids:
                    if asset.asset_id.show_on_report:
                        worksheet.write_merge(row,row,0,3, asset.asset_id.desc, style_summary)
                        worksheet.write_merge(row,row,4,5, round(asset.total,2), style_summary)
                        row += 1


        elif self.display_type == 'compare':
            worksheet.write_merge(0, 0, 0, 13, _("REAL EXECUTION REPORT"), style_title)
            worksheet.write_merge(1,1,0,2, _("Project"),style_filter_title)
            worksheet.write_merge(1,1,3,5, _("Budget Number"),style_filter_title)
            worksheet.write_merge(1,1,6,8, _("Date of Issue"),style_filter_title)
            if self.filter_ok:
                worksheet.write_merge(1,1,9,13, _("Added Filter"),style_filter_title)
            worksheet.write_merge(2,2,0,2, budget.project_id.nombre,style_filter_title2)
            worksheet.write_merge(2,2,3,5, budget.code,style_filter_title2)
            worksheet.write_merge(2,2,6,8, budget.create_date.strftime('%d/%m/%Y'),style_filter_title2)
            if self.filter_ok:
                worksheet.write_merge(2,2,9,13, self.get_filter_glosa(),style_filter_title2)

            row = 4
            # Header table
            worksheet.write_merge(row,row,8,9, _("BUDGET"), style_border_table_top)
            worksheet.write_merge(row,row,10,11, _("REAL EXECUTED"), style_border_table_top)
            row_to = row + 1
            worksheet.write_merge(row,row_to,12,13, _("DIFFERENCE"), style_border_table_top)
            row += 1
            worksheet.write_merge(row,row,0,1, _("CODE"), style_border_table_top)
            worksheet.write_merge(row,row,2,7, _("CONCEPT"), style_border_table_top)
            worksheet.write_merge(row,row,8,8, _("QUANTITY"), style_border_table_top)
            worksheet.write_merge(row,row,9,9, _("BUDGET"), style_border_table_top)
            worksheet.write_merge(row,row,10,10, _("QUANTITY"), style_border_table_top)
            worksheet.write_merge(row,row,11,11, _("REAL"), style_border_table_top)
            chapters = budget.concept_ids.filtered(lambda c: not c.parent_id)
            total = 0
            row += 1
            for chapter in chapters:
                balance = 0
                execute = 0
                difference = 0
                if self.filter_ok:
                    if self.get_execute_filter(chapter) > 0:
                        balance = round(chapter.balance,2)
                        execute = round(self.get_execute(chapter),2)
                        difference = balance - execute
                        worksheet.write_merge(row,row,0,1, chapter.code, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,2,7, chapter.name, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,8,8, "-", style_border_table_details_chapters)
                        worksheet.write_merge(row,row,9,9, balance, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,10,10, "-", style_border_table_details_chapters)
                        worksheet.write_merge(row,row,11,11, execute, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,12,13, difference, style_border_table_details_chapters)
                        row += 1

                        for child in chapter.child_ids:
                            if self.get_execute_filter(child) > 0:
                                child_balance = round(child.balance, 2)
                                child_execute = round(self.get_execute(child), 2)
                                child_difference = child_balance - child_execute

                                worksheet.write_merge(row,row,0,1, child.code, style_border_table_details_departed)
                                worksheet.write_merge(row,row,2,7, child.name, style_border_table_details_departed)
                                worksheet.write_merge(row,row,8,8, child.quantity, style_border_table_details_departed)
                                worksheet.write_merge(row,row,9,9, child_balance, style_border_table_details_departed)
                                worksheet.write_merge(row,row,10,10, "-", style_border_table_details_departed)
                                worksheet.write_merge(row,row,11,11, child_execute, style_border_table_details_departed)
                                worksheet.write_merge(row,row,12,13, child_difference, style_border_table_details_departed)
                                row += 1
                else:
                    balance = round(chapter.balance, 2)
                    execute = round(self.get_execute(chapter), 2)
                    difference = balance - execute

                    worksheet.write_merge(row,row,0,1, chapter.code, style_border_table_details_chapters)
                    worksheet.write_merge(row,row,2,7, chapter.name, style_border_table_details_chapters)
                    worksheet.write_merge(row,row,8,8, "-", style_border_table_details_chapters)
                    worksheet.write_merge(row, row, 9, 9, balance,style_border_table_details_chapters)
                    worksheet.write_merge(row, row, 10, 10, "-",style_border_table_details_chapters)
                    worksheet.write_merge(row, row, 11, 11, execute,style_border_table_details_chapters)
                    worksheet.write_merge(row, row, 12, 13, difference,style_border_table_details_chapters)
                    row += 1

                    for child in chapter.child_ids:
                        child_balance = round(child.balance, 2)
                        child_execute = round(self.get_execute(child), 2)
                        child_difference = child_balance - child_execute

                        worksheet.write_merge(row,row,0,1, child.code, style_border_table_details_departed)
                        worksheet.write_merge(row,row,2,7, child.name, style_border_table_details_departed)
                        worksheet.write_merge(row,row,8,8, child.quantity, style_border_table_details_departed)
                        worksheet.write_merge(row,row,9,9, child_balance, style_border_table_details_departed)
                        worksheet.write_merge(row,row,10,10, "-", style_border_table_details_departed)
                        worksheet.write_merge(row,row,11,11, child_execute, style_border_table_details_departed)
                        worksheet.write_merge(row,row,12,13, child_difference, style_border_table_details_departed)
                        row += 1

        else:# (DETALLADO - COMPLETO)
            if self.show_amount_and_price:
                worksheet.write_merge(0, 0, 0, 11, _("BUDGET REPORT"), style_title)
            else:
                worksheet.write_merge(0, 0, 0, 9, _("BUDGET REPORT"), style_title)
            worksheet.write_merge(1,1,0,2, _("Project"),style_filter_title)
            worksheet.write_merge(1,1,3,5, _("Budget Number"),style_filter_title)
            worksheet.write_merge(1,1,6,8, _("Date of Issue"),style_filter_title)
            if self.filter_ok:
                worksheet.write_merge(1,1,9,9, _("Added Filter"),style_filter_title)
            worksheet.write_merge(2,2,0,2, budget.project_id.nombre,style_filter_title2)
            worksheet.write_merge(2,2,3,5, budget.code,style_filter_title2)
            worksheet.write_merge(2,2,6,8, budget.create_date.strftime('%d/%m/%Y'),style_filter_title2)
            if self.filter_ok:
                worksheet.write_merge(2,2,9,9, self.get_filter_glosa(),style_filter_title2)

            row = 5
            # Header table
            worksheet.write_merge(row,row,0,1, _("CODE"), style_border_table_top)
            worksheet.write_merge(row,row,2,7, _("CRITERION"), style_border_table_top)
            worksheet.write_merge(row,row,8,8, _("UNIT"), style_border_table_top)
            if self.show_amount_and_price:
                worksheet.write_merge(row,row,9,9, _("QUANTITY"), style_border_table_top)
                worksheet.write_merge(row,row,10,10, _("PRICE"), style_border_table_top)
                worksheet.write_merge(row,row,11,11, _("AMOUNT"), style_border_table_top)
            else:
                worksheet.write_merge(row,row,9,9, _("AMOUNT"), style_border_table_top)
            row += 1
            parents = budget.concept_ids.filtered(lambda c: not c.parent_id)
            for parent in parents:
                if self.filter_ok:
                    filter_val = self.get_quantity_filter(parent)
                    if filter_val['qty'] > 0:
                        worksheet.write_merge(row,row,0,1, parent.code, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,2,7, parent.name, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,8,8, parent.uom_id and parent.uom_id.name or '', style_border_table_details_chapters)
                        if self.show_amount_and_price:
                            worksheet.write_merge(row,row,9,9, parent.quantity, style_border_table_details_chapters)
                            worksheet.write_merge(row,row,10,10, filter_val['price'], style_border_table_details_chapters)
                            worksheet.write_merge(row,row,11,11, filter_val['price'], style_border_table_details_chapters)
                        else:
                            worksheet.write_merge(row,row,9,9, filter_val['price'], style_border_table_details_chapters)
                        row += 1
                        if self.text and parent.note and self.display_type == 'full':
                            worksheet.write_merge(row,row,0,9, parent.note, style_border_table_details)
                            row += 1
                        if self.summary_type in ['departure','resource']:
                            for child in parent.child_ids:
                                filter_child = self.get_quantity_filter(child)
                                style_child = child.type == 'departure' and style_border_table_details_departed or style_border_table_details_chapters

                                if filter_child['qty'] > 0:
                                    worksheet.write_merge(row,row,0,1, child.code, style_child)
                                    worksheet.write_merge(row,row,2,7, child.name, style_child)
                                    worksheet.write_merge(row,row,8,8, child.uom_id and child.uom_id.name or '', style_child)
                                    if self.show_amount_and_price:
                                        worksheet.write_merge(row,row,9,9, filter_child['qty'], style_child)
                                        worksheet.write_merge(row,row,10,10, filter_child['price'], style_child)
                                        worksheet.write_merge(row,row,11,11, filter_child['qty'] * filter_child['price'], style_child)
                                    else:
                                        worksheet.write_merge(row,row,9,9, filter_child['qty'] * filter_child['price'], style_child)
                                    row += 1

                                    # EXTRA: Si hay un hijo partida o capitulo
                                    if any(ext.type in ['departure','chapter'] for ext in child.child_ids) and self.summary_type in ['departure']:
                                        for extra in child.child_ids:
                                            filter_ext = self.get_quantity_filter(extra)
                                            style_ext = extra.type == 'departure' and style_border_table_details_departed or style_border_table_details_chapters
                                            if filter_ext['qty'] > 0:
                                                worksheet.write_merge(row,row,0,1, extra.code, style_ext)
                                                worksheet.write_merge(row,row,2,7, extra.name, style_ext)
                                                worksheet.write_merge(row,row,8,8, extra.uom_id and extra.uom_id.name or '', style_ext)
                                                if self.show_amount_and_price:
                                                    worksheet.write_merge(row,row,9,9, filter_ext['qty'], style_ext)
                                                    worksheet.write_merge(row,row,10,10, filter_ext['price'], style_ext)
                                                    worksheet.write_merge(row,row,11,11, filter_ext['price']*filter_ext['qty'], style_ext)
                                                else:
                                                    worksheet.write_merge(row,row,9,9, filter_ext['price']*filter_ext['qty'], style_ext)
                                                row += 1
                                                if self.measures and extra.measuring_ids and self.display_type == 'full':
                                                    worksheet.write_merge(row,row,1,1, _("Group"), style_border_table_bottom)
                                                    worksheet.write_merge(row,row,2,4, _("Description"), style_border_table_bottom)
                                                    worksheet.write_merge(row,row,5,5, _("Quant(N)"), style_border_table_bottom)
                                                    worksheet.write_merge(row,row,6,6, _("Length(X)"), style_border_table_bottom)
                                                    worksheet.write_merge(row,row,7,7, _("Width(Y)"), style_border_table_bottom)
                                                    worksheet.write_merge(row,row,8,8, _("Height(Z)"), style_border_table_bottom)
                                                    if self.show_amount_and_price:
                                                        worksheet.write_merge(row,row,9,9, _("Formula"), style_border_table_bottom)
                                                        worksheet.write_merge(row,row,10,10, "Subtotal", style_border_table_bottom)
                                                    else:
                                                        worksheet.write_merge(row,row,9,9, "Subtotal", style_border_table_bottom)
                                                    row += 1

                                                    if self.filter_type == 'space':
                                                        measures_filter = extra.measuring_ids.filtered(lambda m: m.space_id.id in self.space_ids.ids)
                                                    else:
                                                        measures_filter = extra.measuring_ids.filtered(lambda m: m.space_id.object_id.id in self.object_ids.ids)

                                                    for msr in measures_filter:
                                                        worksheet.write_merge(row,row,1,1, msr.space_id.display_name or '', style_border_table_details)
                                                        worksheet.write_merge(row,row,2,4, msr.name or '', style_border_table_details)
                                                        worksheet.write_merge(row,row,5,5, msr.qty, style_border_table_details)
                                                        worksheet.write_merge(row,row,6,6, msr.length, style_border_table_details)
                                                        worksheet.write_merge(row,row,7,7, msr.width, style_border_table_details)
                                                        worksheet.write_merge(row,row,8,8, msr.height, style_border_table_details)
                                                        if self.show_amount_and_price:
                                                            worksheet.write_merge(row,row,9,9, msr.formula.name or '', style_border_table_details)
                                                            worksheet.write_merge(row,row,10,10, round(msr.amount_subtotal,2), style_border_table_details)
                                                        else:
                                                            worksheet.write_merge(row,row,9,9, round(msr.amount_subtotal,2), style_border_table_details)
                                                        row += 1

                                    if self.text and child.note and self.display_type == 'full':
                                        worksheet.write_merge(row,row,0,9, child.note, style_border_table_details)
                                        row += 1
                                    if self.measures and child.measuring_ids and self.display_type == 'full':
                                        worksheet.write_merge(row,row,1,1, _("Group"), style_border_table_bottom)
                                        worksheet.write_merge(row,row,2,4, _("Description"), style_border_table_bottom)
                                        worksheet.write_merge(row,row,5,5, _("Quant(N)"), style_border_table_bottom)
                                        worksheet.write_merge(row,row,6,6, _("Length(X)"), style_border_table_bottom)
                                        worksheet.write_merge(row,row,7,7, _("Width(Y)"), style_border_table_bottom)
                                        worksheet.write_merge(row,row,8,8, _("Height(Z)"), style_border_table_bottom)
                                        if self.show_amount_and_price:
                                            worksheet.write_merge(row,row,9,9, _("Formula"), style_border_table_bottom)
                                            worksheet.write_merge(row,row,10,10, "Subtotal", style_border_table_bottom)
                                        else:
                                            worksheet.write_merge(row,row,9,9, "Subtotal", style_border_table_bottom)
                                        row += 1

                                        if self.filter_type == 'space':
                                            measures_filter = child.measuring_ids.filtered(lambda m: m.space_id.id in self.space_ids.ids)
                                        else:
                                            measures_filter = child.measuring_ids.filtered(lambda m: m.space_id.object_id.id in self.object_ids.ids)

                                        for msr in measures_filter:
                                            worksheet.write_merge(row,row,1,1, msr.space_id.display_name or '', style_border_table_details)
                                            worksheet.write_merge(row,row,2,4, msr.name or '', style_border_table_details)
                                            worksheet.write_merge(row,row,5,5, msr.qty, style_border_table_details)
                                            worksheet.write_merge(row,row,6,6, msr.length, style_border_table_details)
                                            worksheet.write_merge(row,row,7,7, msr.width, style_border_table_details)
                                            worksheet.write_merge(row,row,8,8, msr.height, style_border_table_details)
                                            if self.show_amount_and_price:
                                                worksheet.write_merge(row,row,9,9, msr.formula.name or '', style_border_table_details)
                                                worksheet.write_merge(row,row,10,10, round(msr.amount_subtotal,2), style_border_table_details)
                                            else:
                                                worksheet.write_merge(row,row,9,9, round(msr.amount_subtotal,2), style_border_table_details)
                                            row += 1
                                    if child.child_ids and self.summary_type in ['resource']:
                                        for resource in child.child_ids:
                                            worksheet.write_merge(row,row,0,1, resource.code, style_border_table_details)
                                            worksheet.write_merge(row,row,2,7, resource.name, style_border_table_details)
                                            worksheet.write_merge(row,row,8,8, resource.uom_id and resource.uom_id.name or '', style_border_table_details)
                                            if self.show_amount_and_price:
                                                worksheet.write_merge(row,row,9,9, resource.quantity, style_border_table_details)
                                                worksheet.write_merge(row,row,10,10, round(resource.amount_compute,2), style_border_table_details)
                                                worksheet.write_merge(row,row,11,11, round(resource.balance,2), style_border_table_details)
                                            else:
                                                worksheet.write_merge(row,row,9,9, round(resource.balance,2), style_border_table_details)
                                            row += 1
                                            if self.text and resource.note and self.display_type == 'full':
                                                worksheet.write_merge(row,row,0,9, resource.note, style_border_table_details)
                                                row += 1

                # (DETALLADO - COMPLETO SIN FILTRO)
                else:
                    worksheet.write_merge(row,row,0,1, parent.code, style_border_table_details_chapters)
                    worksheet.write_merge(row,row,2,7, parent.name, style_border_table_details_chapters)
                    worksheet.write_merge(row,row,8,8, parent.uom_id and parent.uom_id.name or '', style_border_table_details_chapters)
                    if self.show_amount_and_price:
                        worksheet.write_merge(row,row,9,9, parent.quantity, style_border_table_details_chapters)
                        worksheet.write_merge(row,row,10,10, round(parent.amount_compute,2), style_border_table_details_chapters)
                        worksheet.write_merge(row,row,11,11, round(parent.balance,2), style_border_table_details_chapters)
                    else:
                        worksheet.write_merge(row,row,9,9, round(parent.balance,2), style_border_table_details_chapters)
                    row += 1
                    if self.text and parent.note and self.display_type == 'full':
                        worksheet.write_merge(row,row,0,9, parent.note, style_border_table_details)
                        row += 1
                    if self.summary_type in ['departure','resource']:
                        for child in parent.child_ids:
                            if child.type == 'departure':
                                worksheet.write_merge(row,row,0,1, child.code, style_border_table_details_departed)
                                worksheet.write_merge(row,row,2,7, child.name, style_border_table_details_departed)
                                worksheet.write_merge(row,row,8,8, child.uom_id and child.uom_id.name or '', style_border_table_details_departed)
                                if self.show_amount_and_price:
                                    worksheet.write_merge(row,row,9,9, child.quantity, style_border_table_details_departed)
                                    worksheet.write_merge(row,row,10,10, round(child.amount_compute,2), style_border_table_details_departed)
                                    worksheet.write_merge(row,row,11,11, round(child.balance,2), style_border_table_details_departed)
                                else:
                                    worksheet.write_merge(row,row,9,9, round(child.balance,2), style_border_table_details_departed)
                                row += 1
                            else:
                                worksheet.write_merge(row,row,0,1, child.code, style_border_table_details)
                                worksheet.write_merge(row,row,2,7, child.name, style_border_table_details)
                                worksheet.write_merge(row,row,8,8, child.uom_id and child.uom_id.name or '', style_border_table_details)
                                if self.show_amount_and_price:
                                    worksheet.write_merge(row,row,9,9, child.quantity, style_border_table_details)
                                    worksheet.write_merge(row,row,10,10, round(child.amount_compute,2), style_border_table_details)
                                    worksheet.write_merge(row,row,11,11, round(child.balance,2), style_border_table_details)
                                else:
                                    worksheet.write_merge(row,row,9,9, round(child.balance,2), style_border_table_details)
                                row += 1
                            if self.text and child.note and self.display_type == 'full':
                                worksheet.write_merge(row,row,0,9, child.note, style_border_table_details)
                                row += 1
                            if self.measures and child.measuring_ids and self.display_type == 'full':
                                worksheet.write_merge(row,row,1,1, _("Group"), style_border_table_bottom)
                                worksheet.write_merge(row,row,2,4, _("Description"), style_border_table_bottom)
                                worksheet.write_merge(row,row,5,5, _("Quant(N)"), style_border_table_bottom)
                                worksheet.write_merge(row,row,6,6, _("Length(X)"), style_border_table_bottom)
                                worksheet.write_merge(row,row,7,7, _("Width(Y)"), style_border_table_bottom)
                                worksheet.write_merge(row,row,8,8, _("Height(Z)"), style_border_table_bottom)
                                if self.show_amount_and_price:
                                    worksheet.write_merge(row,row,9,9, _("Formula"), style_border_table_bottom)
                                    worksheet.write_merge(row,row,10,10, "Subtotal", style_border_table_bottom)
                                else:
                                    worksheet.write_merge(row,row,9,9, "Subtotal", style_border_table_bottom)
                                row += 1
                                for msr in child.measuring_ids:
                                    worksheet.write_merge(row,row,1,1, msr.space_id.display_name or '', style_border_table_details)
                                    worksheet.write_merge(row,row,2,4, msr.name or '', style_border_table_details)
                                    worksheet.write_merge(row,row,5,5, msr.qty, style_border_table_details)
                                    worksheet.write_merge(row,row,6,6, msr.length, style_border_table_details)
                                    worksheet.write_merge(row,row,7,7, msr.width, style_border_table_details)
                                    worksheet.write_merge(row,row,8,8, msr.height, style_border_table_details)
                                    if self.show_amount_and_price:
                                        worksheet.write_merge(row,row,9,9, msr.formula.name or '', style_border_table_details)
                                        worksheet.write_merge(row,row,10,10, round(msr.amount_subtotal,2), style_border_table_details)
                                    else:
                                        worksheet.write_merge(row,row,9,9, round(msr.amount_subtotal,2), style_border_table_details)
                                    row += 1
                            if child.child_ids and self.summary_type in ['resource']:
                                for resource in child.child_ids:
                                    worksheet.write_merge(row,row,0,1, resource.code, style_border_table_details)
                                    worksheet.write_merge(row,row,2,7, resource.name, style_border_table_details)
                                    worksheet.write_merge(row,row,8,8, resource.uom_id and resource.uom_id.name or '', style_border_table_details)

                                    if self.show_amount_and_price:
                                        worksheet.write_merge(row,row,9,9, resource.quantity, style_border_table_details)
                                        worksheet.write_merge(row,row,10,10, round(resource.amount_compute,2), style_border_table_details)
                                        worksheet.write_merge(row,row,11,11, round(resource.balance,2), style_border_table_details)
                                    else:
                                        worksheet.write_merge(row,row,9,9, round(resource.balance,2), style_border_table_details)
                                    row += 1
                                    if self.text and resource.note and self.display_type == 'full':
                                        worksheet.write_merge(row,row,0,9, resource.note, style_border_table_details)
                                        row += 1
            # TOTALES (CON FILTRO)
            if self.filter_ok:
                total_filter = self.get_total_filter()
                if self.show_amount_and_price:
                    if total_filter['MT'] > 0:
                        worksheet.write_merge(row,row,8,10, _("Total Materials"), style_summary)
                        worksheet.write_merge(row,row,11,11, total_filter['MT'], style_summary)
                        row += 1
                    if total_filter['MO'] > 0:
                        worksheet.write_merge(row,row,8,10, _("Total Labor"), style_summary)
                        worksheet.write_merge(row,row,11,11, total_filter['MO'], style_summary)
                        row += 1
                    if total_filter['EQ'] > 0:
                        worksheet.write_merge(row,row,8,10, _("Total Equipment"), style_summary)
                        worksheet.write_merge(row,row,11,11, total_filter['EQ'], style_summary)
                        row += 1
                    if total_filter['AX'] > 0:
                        worksheet.write_merge(row,row,8,10, _("Other"), style_summary)
                        worksheet.write_merge(row,row,11,11, total_filter['AX'], style_summary)
                        row += 1
                    worksheet.write_merge(row,row,8,10, "TOTAL", style_summary)
                    worksheet.write_merge(row,row,11,11, total_filter['MT']+total_filter['MO']+total_filter['EQ']+total_filter['AX'], style_summary)
                else:
                    if total_filter['MT'] > 0:
                        worksheet.write_merge(row,row,6,8, _("Total Materials"), style_summary)
                        worksheet.write_merge(row,row,9,9, total_filter['MT'], style_summary)
                        row += 1
                    if total_filter['MO'] > 0:
                        worksheet.write_merge(row,row,6,8, _("Total Labor"), style_summary)
                        worksheet.write_merge(row,row,9,9, total_filter['MO'], style_summary)
                        row += 1
                    if total_filter['EQ'] > 0:
                        worksheet.write_merge(row,row,6,8, _("Total Equipment"), style_summary)
                        worksheet.write_merge(row,row,9,9, total_filter['EQ'], style_summary)
                        row += 1
                    if total_filter['AX'] > 0:
                        worksheet.write_merge(row,row,6,8, _("Other"), style_summary)
                        worksheet.write_merge(row,row,9,9, total_filter['AX'], style_summary)
                        row += 1
                    worksheet.write_merge(row,row,6,8, "TOTAL", style_summary)
                    worksheet.write_merge(row,row,9,9, total_filter['MT']+total_filter['MO']+total_filter['EQ']+total_filter['AX'], style_summary)

            # TOTALES (SIN FILTRO)
            else:
                if self.show_amount_and_price:
                    if self.total_type == 'normal':
                        mt = round(self.get_total('material'),2)
                        mo = round(self.get_total('labor'),2)
                        eq = round(self.get_total('equip'),2)
                        tot = mt + mo + eq
                        others = round((budget.balance - tot),2)
                        total = round(budget.balance,2)
                        if mt > 0:
                            worksheet.write_merge(row,row,8,10, _("Total Materials"), style_summary)
                            worksheet.write_merge(row,row,11,11, mt, style_summary)
                            row += 1
                        if mo > 0:
                            worksheet.write_merge(row,row,8,10, _("Total Labor"), style_summary)
                            worksheet.write_merge(row,row,11,11, mo, style_summary)
                            row += 1
                        if eq > 0:
                            worksheet.write_merge(row,row,8,10, _("Total Equipment"), style_summary)
                            worksheet.write_merge(row,row,11,11, eq, style_summary)
                            row += 1
                        if others > 0:
                            worksheet.write_merge(row,row,8,10, _("Others"), style_summary)
                            worksheet.write_merge(row,row,11,11, others, style_summary)
                            row += 1
                        worksheet.write_merge(row,row,8,10, "TOTAL", style_summary)
                        worksheet.write_merge(row,row,11,11, total, style_summary)
                    else:
                        for asset in budget.asset_ids:
                            if asset.asset_id.show_on_report:
                                worksheet.write_merge(row,row,8,10, asset.asset_id.desc, style_summary)
                                worksheet.write_merge(row,row,11,11, round(asset.total,2), style_summary)
                                row += 1
                else:
                    if self.total_type == 'normal':
                        mt = round(self.get_total('material'),2)
                        mo = round(self.get_total('labor'),2)
                        eq = round(self.get_total('equip'),2)
                        tot = mt + mo + eq
                        others = round((budget.balance - tot),2)
                        total = round(budget.balance,2)
                        if mt > 0:
                            worksheet.write_merge(row,row,6,8, _("Total Materials"), style_summary)
                            worksheet.write_merge(row,row,9,9, mt, style_summary)
                            row += 1
                        if mo > 0:
                            worksheet.write_merge(row,row,6,8, _("Total Labor"), style_summary)
                            worksheet.write_merge(row,row,9,9, mo, style_summary)
                            row += 1
                        if eq > 0:
                            worksheet.write_merge(row,row,6,8, _("Total Equipment"), style_summary)
                            worksheet.write_merge(row,row,9,9, eq, style_summary)
                            row += 1
                        if others > 0:
                            worksheet.write_merge(row,row,8,10, _("Others"), style_summary)
                            worksheet.write_merge(row,row,11,11, others, style_summary)
                            row += 1
                        worksheet.write_merge(row,row,6,8, "TOTAL", style_summary)
                        worksheet.write_merge(row,row,9,9, total, style_summary)
                    else:
                        for asset in budget.asset_ids:
                            if asset.asset_id.show_on_report:
                                worksheet.write_merge(row,row,6,8, asset.asset_id.desc, style_summary)
                                worksheet.write_merge(row,row,9,9, round(asset.total,2), style_summary)
                                row += 1

        fp = BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        data_b64 = base64.encodebytes(data)
        doc = self.env['ir.attachment'].create({
            'name': '%s.xls' % (file_name),
            'datas': data_b64,
        })

        return {
            'type': "ir.actions.act_url",
            'url': "web/content/?model=ir.attachment&id=" + str(
                doc.id) + "&filename_field=name&field=datas&download=true&filename=" + str(doc.name),
            'target': "self",
            'no_destroy': False,
        }


