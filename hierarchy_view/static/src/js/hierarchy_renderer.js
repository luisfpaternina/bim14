odoo.define('hierarchy_view.renderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var field_utils = require('web.field_utils');
    var viewUtils = require('web.viewUtils');
    var config = require('web.config');
    var dom = require('web.dom');
    var core = require('web.core');
    var dialogs = require('web.view_dialogs');

    var QWeb = core.qweb;
    var _t = core._t;

    var DECORATIONS = [
        'decoration-bf',
        'decoration-it',
        'decoration-danger',
        'decoration-info',
        'decoration-muted',
        'decoration-primary',
        'decoration-success',
        'decoration-warning'
    ];

    var FIELD_CLASSES = {
        char: 'o_list_char',
        float: 'o_list_number',
        integer: 'o_list_number',
        monetary: 'o_list_number',
        text: 'o_list_text',
        many2one: 'o_list_many2one',
    };

    $(document).click(function () {
        $('.oh_contextmenu').hide();
        $('.oh_title a').removeClass('text-muted font-weight-bold');
    });
    $(document).contextmenu(function (ev) {
        if ($(ev.target).closest('.o_hierarchy_sidebar_container').length == 0) {
            $('.oh_contextmenu').hide();
            $('.oh_title a').removeClass('text-muted font-weight-bold');
        }
    });

    var HierarchyRenderer = BasicRenderer.extend({
        template: 'HierarchyView',
        events: {
            'click .o_optional_columns_dropdown .dropdown-item': '_onToggleOptionalColumn',
            'click .o_optional_columns_dropdown_toggle': '_onToggleOptionalColumnDropdown',
            'contextmenu .o_hierarchy_sidebar_container': 'context_menu_parent',
            'click .o_hierarchy_sidebar_container a[data-childs="true"]': 'display_children',
            'contextmenu .o_hierarchy_sidebar_container a': 'context_menu_child',
            'click .oh_contextmenu [data-action="open"]': 'openRecord',
            'click .oh_contextmenu [data-action="create"]': 'openNewForm',
            'click .oh_contextmenu [data-action="copy"]': 'openNewForm',
            'click .oh_contextmenu [data-action="unlink"]': 'deleteRecord',
            'click tbody tr': '_onRowClicked',
        },
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this._preprocessColumns();
            this.columnInvisibleFields = params.columnInvisibleFields || {};
            this.rowDecorations = this._extractDecorationAttrs(this.arch);
            this.fieldDecorations = {};
            for (const field of this.arch.children.filter(c => c.tag === 'field')) {
                const decorations = this._extractDecorationAttrs(field);
                this.fieldDecorations[field.attrs.name] = decorations;
            }
            this.parent_field = params.arch.attrs.parent_field || 'parent_id';
            this.listData = this.state.data;
            this.$contextmenu = undefined;
            this.contextResId = undefined;
        },
        willStart: function () {
            this._processColumns(this.columnInvisibleFields);
            return this._super.apply(this, arguments);
        },
        updateState: function (state, params) {
            this._setState(state);
            this.columnInvisibleFields = params.columnInvisibleFields || {};
            this._processColumns(this.columnInvisibleFields);
            return this._super.apply(this, arguments);
        },
        renderSidebar: function () {
            var elements = QWeb.render('HierarchySidebarList', { records: this.state.data });
            this.$('.o_hierarchy_sidebar_container').html(elements).resizable({
                handles: 'e',
                maxWidth: 600,
                minWidth: 200,
            });
            this.$('ul').show();
        },
        context_menu_parent: function (ev) {
            ev.preventDefault();
            this.contextResId = undefined;
            this.contextParentId = undefined;
        },
        context_menu_child: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.$('.oh_title a').removeClass('text-primary font-weight-bold');
            var $a = $(ev.currentTarget);
            $a.addClass('text-muted font-weight-bold');
            this.contextResId = $a.get()[0].dataset.resId;
            this.contextParentId = $a.get()[0].dataset.parentId;
            if (this.$contextmenu.height() + ev.pageY >= window.innerHeight) {
                this.$contextmenu.css('top', '').css('bottom', window.innerHeight - ev.pageY).css('left', ev.pageX).show();
            } else {
                this.$contextmenu.css('top', ev.pageY).css('bottom', '').css('left', ev.pageX).show();
            }
            
        },
        openRecord: function (ev) {
            ev.preventDefault();
            this.trigger_up('open_record', { id: this.contextResId, target: ev.target });
        },
        openNewForm: function (ev) {
            ev.preventDefault();
            var self = this;
            var $a = this.$(`.oh_title [data-res-id="${this.contextResId}"]`);
            var $li = $a.closest('li');
            var parent_id = $(ev.target).data('action') === 'create' ? $a.data('id') : $a.data('parentId');
            var context = {};
            context['default_' + this.parent_field] = parent_id;
            new dialogs.FormViewDialog(this, {
                res_model: this.state.model,
                title: _t('Create ') + ' ' + (this.arch.attrs.string || ''),
                disable_multiple_selection: true,
                context: _.extend({}, this.state.context, context),
                on_saved: function () {
                    if (!parent_id) {
                        var controller = self.__parentedParent;
                        controller.__parentedParent.doAction({
                            type: 'ir.actions.act_window',
                            name: controller._title,
                            res_model: self.state.model,
                            views: controller.actionViews.map(act_view => [false, act_view.type]),
                            domain: controller.initialState.domain,
                        }, {
                            replace_last_action: true,
                            additional_context: controller.initialState.context,
                        });
                    }
                    else {
                        if ($(ev.target).data('action') === 'create') {
                            if (!$a.data('childs')) {
                                $a.get()[0].dataset.childs = true;
                                $li.find('.oh_title .fa.fa-angle-right').removeClass('fa-angle-right text-muted').addClass('fa-caret-right');
                            }
                            self.refresh_record($li);
                        } else {
                            self.refresh_record($li.parent().closest('li'));
                        }
                    }
                },
            }).open();
        },
        deleteRecord: function (ev) {
            ev.preventDefault();
            var self = this;
            var $a = this.$(`.oh_title [data-res-id="${this.contextResId}"]`);
            var $li = $a.closest('li');
            var $ul = $li.parent();
            if (confirm(_t("Are you sure you want to delete this record ?"))) {
                self.getParent().model.deleteRecords([self.contextResId], self.state.model).then(function () {
                    $li.hide(function () {
                        $li.remove();
                        if (!$ul.children().length) {
                            var $oh_title = $ul.siblings('.oh_title');
                            $oh_title.find('>.fa-caret-down').removeClass('fa-caret-down').addClass('fa-angle-right text-muted');
                            var $a2 = $oh_title.find('>a').get();
                            if ($a2.length) {
                                $a2[0].dataset.childs = false;
                            }
                            $ul.remove();
                        }
                    });
                });
            }
        },
        refresh_record: function ($li) {
            $li.find('>.oh_title i.fa-caret-down').removeClass('fa-caret-down').addClass('fa-caret-right');
            $li.find('>ul').remove();
            $li.find('a').trigger('click');
        },
        display_children: function (ev) {
            var model = this.getParent().model;
            var $a = $(ev.currentTarget);
            this.$('a').removeClass('unfolded');
            $a.addClass('unfolded');
            var $li = $a.closest('li');
            if ($li.find('>.oh_title i.fa-caret-down').length) {
                $li.find('>ul').slideUp();
                $li.find('>.oh_title i.fa-caret-down').removeClass('fa-caret-down').addClass('fa-caret-right');
                var res_id = $li.parent().parent().find('>.oh_title a').data('resId');
                var new_state = model.get(res_id);
                this.listData = new_state ? new_state.data : this.state.data;
                this.renderListData();
                return;
            } else if ($li.find('ul').length) {
                $li.find('>.oh_title i.fa-caret-right').removeClass('fa-caret-right').addClass('fa-caret-down');
                var res_id = $a.data('resId');
                var new_state = model.get(res_id);
                this.listData = new_state.data;
                this.renderListData();
                $li.find('>ul').slideDown();
                return;
            }
            $li.find('>.oh_title i.fa-caret-right').removeClass('fa-caret-right').addClass('fa-caret-down');
            var res_id = $a.data('id');
            var self = this;
            model.load({
                context: this.state.context,
                domain: [[this.parent_field, '=', res_id]],
                fields: this.state.fields,
                fieldsInfo: this.state.fieldsInfo,
                viewType: 'hierarchy',
                modelName: this.state.model,
                type: 'list',
            }).then(function (res_id) {
                var new_state = model.get(res_id);
                self.listData = new_state.data;
                self.renderListData();
                $a.data('resId', res_id);
                if (self.listData.length) {
                    var elements = QWeb.render('HierarchySidebarList', { records: self.listData });
                    $li.append(elements);
                }
                $li.find('>ul').slideDown();
            });
        },
        renderListData: function () {
            this._computeAggregates();
            var $table = $('<table>').addClass('o_list_table table table-sm table-hover table-striped');
            $table.append(this._renderHeader());
            $table.append(this._renderBody());
            $table.append(this._renderFooter());
            if (this.optionalColumns.length) {
                $table.addClass('o_list_optional_columns');
                $table.append($('<i class="o_optional_columns_dropdown_toggle fa fa-ellipsis-v"/>'));
                $table.append(this._renderOptionalColumnsDropdown());
            }
            this.$('.o_hierarchy_widget').html($table);
        },
        _renderView: function () {
            var defs = [];
            this.defs = defs;
            this._computeAggregates();
            this.renderSidebar();
            this.renderListData();
            delete this.defs;
            var contextmenu = QWeb.render('HierarchyContextMenu');
            this.$el.append(contextmenu);
            this.$contextmenu = this.$('.oh_contextmenu');
            return this._super.apply(this, arguments);
        },
        // ---------- List methods -------------
        _computeAggregates: function () {
            _.each(this.columns, this._computeColumnAggregates.bind(this, this.listData));
        },
        _computeColumnAggregates: function (data, column) {
            var attrs = column.attrs;
            var field = this.state.fields[attrs.name];
            if (!field) {
                return;
            }
            var type = field.type;
            if (type !== 'integer' && type !== 'float' && type !== 'monetary') {
                return;
            }
            var func = (attrs.sum && 'sum') || (attrs.avg && 'avg') ||
                (attrs.max && 'max') || (attrs.min && 'min');
            if (func) {
                var count = 0;
                var aggregateValue = 0;
                if (func === 'max') {
                    aggregateValue = -Infinity;
                } else if (func === 'min') {
                    aggregateValue = Infinity;
                }
                _.each(data, function (d) {
                    count += 1;
                    var value = (d.type === 'record') ? d.data[attrs.name] : d.aggregateValues[attrs.name];
                    if (func === 'avg') {
                        aggregateValue += value;
                    } else if (func === 'sum') {
                        aggregateValue += value;
                    } else if (func === 'max') {
                        aggregateValue = Math.max(aggregateValue, value);
                    } else if (func === 'min') {
                        aggregateValue = Math.min(aggregateValue, value);
                    }
                });
                if (func === 'avg') {
                    aggregateValue = count ? aggregateValue / count : aggregateValue;
                }
                column.aggregate = {
                    help: attrs[func],
                    value: aggregateValue,
                };
            }
        },
        _processColumns: function (columnInvisibleFields) {
            var self = this;
            this.handleField = null;
            this.columns = [];
            this.optionalColumns = [];
            this.optionalColumnsEnabled = [];
            var storedOptionalColumns;
            this.trigger_up('load_optional_fields', {
                keyParts: this._getOptionalColumnsStorageKeyParts(),
                callback: function (res) {
                    storedOptionalColumns = res;
                },
            });
            _.each(this.arch.children, function (c) {
                if (c.tag !== 'control' && c.tag !== 'groupby' && c.tag !== 'header') {
                    var reject = c.attrs.modifiers.invisible;
                    if (c.tag === "button_group") {
                        reject = c.children.every(child => columnInvisibleFields[child.attrs.name]);
                    } else if (c.attrs.name in columnInvisibleFields) {
                        reject = columnInvisibleFields[c.attrs.name];
                    }
                    if (!reject && c.attrs.widget === 'handle') {
                        self.handleField = c.attrs.name;
                        if (self.isGrouped) {
                            reject = true;
                        }
                    }
    
                    if (!reject && c.attrs.optional) {
                        self.optionalColumns.push(c);
                        var enabled;
                        if (storedOptionalColumns === undefined) {
                            enabled = c.attrs.optional === 'show';
                        } else {
                            enabled = _.contains(storedOptionalColumns, c.attrs.name);
                        }
                        if (enabled) {
                            self.optionalColumnsEnabled.push(c.attrs.name);
                        }
                        reject = !enabled;
                    }
    
                    if (!reject) {
                        self.columns.push(c);
                    }
                }
            });
        },
        _getOptionalColumnsStorageKeyParts: function () {
            var self = this;
            return {
                fields: _.map(this.state.fieldsInfo[this.viewType], function (_, fieldName) {
                    return {name: fieldName, type: self.state.fields[fieldName].type};
                }),
            };
        },
        _onToggleOptionalColumn: function (ev) {
            var self = this;
            ev.stopPropagation();
            // when the input's label is clicked, the click event is also raised on the
            // input itself (https://developer.mozilla.org/en-US/docs/Web/HTML/Element/label),
            // so this handler is executed twice (except if the rendering is quick enough,
            // as when we render, we empty the HTML)
            ev.preventDefault();
            var input = ev.currentTarget.querySelector('input');
            var fieldIndex = this.optionalColumnsEnabled.indexOf(input.name);
            if (fieldIndex >= 0) {
                this.optionalColumnsEnabled.splice(fieldIndex, 1);
            } else {
                this.optionalColumnsEnabled.push(input.name);
            }
            this.trigger_up('save_optional_fields', {
                keyParts: this._getOptionalColumnsStorageKeyParts(),
                optionalColumnsEnabled: this.optionalColumnsEnabled,
            });
            this._processColumns(this.columnInvisibleFields);
            this._render().then(function () {
                self._onToggleOptionalColumnDropdown(ev);
            });
        },
        _onToggleOptionalColumnDropdown: function (ev) {
            // The dropdown toggle is inside the overflow hidden container because
            // the ellipsis is always in the last column, but we want the actual
            // dropdown to be outside of the overflow hidden container since it
            // could easily have a higher height than the table. However, separating
            // the toggle and the dropdown itself is not supported by popper.js by
            // default, which is why we need to toggle the dropdown manually.
            ev.stopPropagation();
            this.$('.o_optional_columns .dropdown-toggle').dropdown('toggle');
        },
        _renderOptionalColumnsDropdown: function () {
            var self = this;
            var $optionalColumnsDropdown = $('<div>', {
                class: 'o_optional_columns text-center dropdown',
            });
            var $a = $("<a>", {
                'class': "dropdown-toggle text-dark o-no-caret",
                'href': "#",
                'role': "button",
                'data-toggle': "dropdown",
                'data-display': "static",
                'aria-expanded': false,
            });
            $a.appendTo($optionalColumnsDropdown);
    
            var direction = _t.database.parameters.direction;
            var dropdownMenuClass = direction === 'rtl' ? 'dropdown-menu-left' : 'dropdown-menu-right';
            var $dropdown = $("<div>", {
                class: 'dropdown-menu o_optional_columns_dropdown ' + dropdownMenuClass,
                role: 'menu',
            });
            this.optionalColumns.forEach(function (col) {
                var txt = (col.attrs.string || self.state.fields[col.attrs.name].string) +
                (config.isDebug() ? (' (' + col.attrs.name + ')') : '');
                var $checkbox = dom.renderCheckbox({
                    text: txt,
                    prop: {
                        name: col.attrs.name,
                        checked: _.contains(self.optionalColumnsEnabled, col.attrs.name),
                    }
                });
                $dropdown.append($("<div>", {
                    class: "dropdown-item",
                }).append($checkbox));
            });
            $dropdown.appendTo($optionalColumnsDropdown);
            return $optionalColumnsDropdown;
        },
        _renderHeader: function () {
            var $tr = $('<tr>').append(_.map(this.columns, this._renderHeaderCell.bind(this)));
            return $('<thead>').append($tr);
        },
        _renderHeaderCell: function (node) {
            const { icon, name, string } = node.attrs;
            var order = this.state.orderedBy;
            var isNodeSorted = order[0] && order[0].name === name;
            var field = this.state.fields[name];
            var $th = $('<th>');
            if (name) {
                $th.attr('data-name', name);
            } else if (string) {
                $th.attr('data-string', string);
            } else if (icon) {
                $th.attr('data-icon', icon);
            }
            if (node.attrs.editOnly) {
                $th.addClass('oe_edit_only');
            }
            if (node.attrs.readOnly) {
                $th.addClass('oe_read_only');
            }
            if (node.tag === 'button_group') {
                $th.addClass('o_list_button');
            }
            if (!field || node.attrs.nolabel === '1') {
                return $th;
            }
            var description = string || field.string;
            if (node.attrs.widget) {
                $th.addClass(' o_' + node.attrs.widget + '_cell');
                const FieldWidget = this.state.fieldsInfo.hierarchy[name].Widget;
                if (FieldWidget.prototype.noLabel) {
                    description = '';
                } else if (FieldWidget.prototype.label) {
                    description = FieldWidget.prototype.label;
                }
            }
            $th.text(description)
                .attr('tabindex', -1)
                .toggleClass('o-sort-down', isNodeSorted ? !order[0].asc : false)
                .toggleClass('o-sort-up', isNodeSorted ? order[0].asc : false)
                .addClass((field.sortable || this.state.fieldsInfo.hierarchy[name].options.allow_order || false) && 'o_column_sortable');
    
            if (isNodeSorted) {
                $th.attr('aria-sort', order[0].asc ? 'ascending' : 'descending');
            }

            if (field.type === 'float' || field.type === 'integer' || field.type === 'monetary') {
                $th.addClass('o_list_number_th');
            }

            if (config.isDebug()) {
                var fieldDescr = {
                    field: field,
                    name: name,
                    string: description || name,
                    record: this.state,
                    attrs: _.extend({}, node.attrs, this.state.fieldsInfo.hierarchy[name]),
                };
                this._addFieldTooltip(fieldDescr, $th);
            } else {
                $th.attr('title', description);
            }
            return $th;
        },
        _renderBody: function () {
            var self = this;
            var $rows = this._renderRows();
            while ($rows.length < 4) {
                $rows.push(self._renderEmptyRow());
            }
            return $('<tbody>').append($rows);
        },
        _renderRows: function () {
            return this.listData.map(this._renderRow.bind(this));
        },
        _renderRow: function (record) {
            var self = this;
            var $cells = this.columns.map(function (node, index) {
                return self._renderBodyCell(record, node, index, { mode: 'readonly' });
            });

            var $tr = $('<tr/>', { class: 'o_data_row' }).attr('data-id', record.id).append($cells);
            this._setDecorationClasses($tr, this.rowDecorations, record);
            return $tr;
        },
        _renderEmptyRow: function () {
            var $td = $('<td>&nbsp;</td>').attr('colspan', this.columns.length);
            return $('<tr>').append($td);
        },
        _renderBodyCell: function (record, node, colIndex, options) {
            var tdClassName = 'o_data_cell';
            if (node.tag === 'button_group') {
                tdClassName += ' o_list_button';
            } else if (node.tag === 'field') {
                tdClassName += ' o_field_cell';
                var typeClass = FIELD_CLASSES[this.state.fields[node.attrs.name].type];
                if (typeClass) {
                    tdClassName += (' ' + typeClass);
                }
                if (node.attrs.widget) {
                    tdClassName += (' o_' + node.attrs.widget + '_cell');
                }
            }
            if (node.attrs.editOnly) {
                tdClassName += ' oe_edit_only';
            }
            if (node.attrs.readOnly) {
                tdClassName += ' oe_read_only';
            }
            var $td = $('<td>', { class: tdClassName, tabindex: -1 });

            var modifiers = this._registerModifiers(node, record, $td, _.pick(options, 'mode'));
            if (modifiers.invisible && !(options && options.renderInvisible)) {
                return $td;
            }

            if (node.tag === 'button_group') {
                for (const buttonNode of node.children) {
                    if (!this.columnInvisibleFields[buttonNode.attrs.name]) {
                        $td.append(this._renderButton(record, buttonNode));
                    }
                }
                return $td;
            } else if (node.tag === 'widget') {
                return $td.append(this._renderWidget(record, node));
            }
            if (node.attrs.widget || (options && options.renderWidgets)) {
                var $el = this._renderFieldWidget(node, record, _.pick(options, 'mode'));
                return $td.append($el);
            }
            this._handleAttributes($td, node);
            this._setDecorationClasses($td, this.fieldDecorations[node.attrs.name], record);

            var name = node.attrs.name;
            var field = this.state.fields[name];
            var value = record.data[name];
            var formatter = field_utils.format[field.type];
            var formatOptions = {
                escape: true,
                data: record.data,
                isPassword: 'password' in node.attrs,
                digits: node.attrs.digits && JSON.parse(node.attrs.digits),
            };
            var formattedValue = formatter(value, field, formatOptions);
            var title = '';
            if (field.type !== 'boolean') {
                title = formatter(value, field, _.extend(formatOptions, {escape: false}));
            }
            return $td.html(formattedValue).attr('title', title);
        },
        _extractDecorationAttrs: function (node) {
            const decorations = {};
            for (const [key, expr] of Object.entries(node.attrs)) {
                if (DECORATIONS.includes(key)) {
                    const cssClass = key.replace('decoration', 'text');
                    decorations[cssClass] = py.parse(py.tokenize(expr));
                }
            }
            return decorations;
        },
        _setDecorationClasses: function ($el, decorations, record) {
            for (const [cssClass, expr] of Object.entries(decorations)) {
                $el.toggleClass(cssClass, py.PY_isTrue(py.evaluate(expr, record.evalContext)));
            }
        },
        _renderFooter: function () {
            var aggregates = {};
            _.each(this.columns, function (column) {
                if ('aggregate' in column) {
                    aggregates[column.attrs.name] = column.aggregate;
                }
            });
            var $cells = this._renderAggregateCells(aggregates);
            return $('<tfoot>').append($('<tr>').append($cells));
        },
        _renderAggregateCells: function (aggregateValues) {
            var self = this;

            return _.map(this.columns, function (column) {
                var $cell = $('<td>');
                if (config.isDebug()) {
                    $cell.addClass(column.attrs.name);
                }
                if (column.attrs.editOnly) {
                    $cell.addClass('oe_edit_only');
                }
                if (column.attrs.readOnly) {
                    $cell.addClass('oe_read_only');
                }
                if (column.attrs.name in aggregateValues) {
                    var field = self.state.fields[column.attrs.name];
                    var value = aggregateValues[column.attrs.name].value;
                    var help = aggregateValues[column.attrs.name].help;
                    var formatFunc = field_utils.format[column.attrs.widget];
                    if (!formatFunc) {
                        formatFunc = field_utils.format[field.type];
                    }
                    var formattedValue = formatFunc(value, field, {
                        escape: true,
                        digits: column.attrs.digits ? JSON.parse(column.attrs.digits) : undefined,
                    });
                    $cell.addClass('o_list_number').attr('title', help).html(formattedValue);
                }
                return $cell;
            });
        },
        _renderButton: function (record, node) {
            var self = this;
            var nodeWithoutWidth = Object.assign({}, node);
            delete nodeWithoutWidth.attrs.width;
            let extraClass = '';
            if (node.attrs.icon) {
                const btnStyleRegex = /\bbtn-[a-z]+\b/;
                if (!btnStyleRegex.test(nodeWithoutWidth.attrs.class)) {
                    extraClass = 'btn-link o_icon_button';
                }
            }
            var $button = viewUtils.renderButtonFromNode(nodeWithoutWidth, {
                extraClass: extraClass,
            });
            this._handleAttributes($button, node);
            this._registerModifiers(node, record, $button);

            if (record.res_id) {
                $button.on("click", function (e) {
                    e.stopPropagation();
                    self.trigger_up('button_clicked', {
                        attrs: node.attrs,
                        record: record,
                    });
                });
            } else {
                if (node.attrs.options.warn) {
                    $button.on("click", function (e) {
                        e.stopPropagation();
                        self.do_warn(_t("Warning"), _t('Please click on the "save" button first.'));
                    });
                } else {
                    $button.prop('disabled', true);
                }
            }
            return $button;
        },
        _updateFooter: function () {
            this._computeAggregates();
            this.$('tfoot').replaceWith(this._renderFooter());
        },
        _onRowClicked: function (ev) {
            if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click')) {
                var id = $(ev.currentTarget).data('id');
                if (id) {
                    this.trigger_up('open_record', { id: id, target: ev.target });
                }
            }
        },
        _processModeClassNames: function () {
            this.arch.children.forEach(c => {
                if (c.attrs.class) {
                    c.attrs.editOnly = /\boe_edit_only\b/.test(c.attrs.class);
                    c.attrs.readOnly = /\boe_read_only\b/.test(c.attrs.class);
                }
            });
        },
        _groupAdjacentButtons: function () {
            const children = [];
            let groupId = 0;
            let buttonGroupNode = null;
            for (const c of this.arch.children) {
                if (c.tag === 'button') {
                    if (!buttonGroupNode) {
                        buttonGroupNode = {
                            tag: 'button_group',
                            children: [c],
                            attrs: {
                                name: `button_group_${groupId++}`,
                                modifiers: {},
                            },
                        };
                        children.push(buttonGroupNode);
                    } else {
                        buttonGroupNode.children.push(c);
                    }
                } else {
                    buttonGroupNode = null;
                    children.push(c);
                }
            }
            this.arch.children = children;
        },
        _preprocessColumns: function () {
            this._processModeClassNames();
            this._groupAdjacentButtons();
    
            // set as readOnly (resp. editOnly) button groups containing only
            // readOnly (resp. editOnly) buttons, s.t. no column is rendered
            this.arch.children.filter(c => c.tag === 'button_group').forEach(c => {
                c.attrs.editOnly = c.children.every(n => n.attrs.editOnly);
                c.attrs.readOnly = c.children.every(n => n.attrs.readOnly);
            });
        },
    });

    return HierarchyRenderer;
});