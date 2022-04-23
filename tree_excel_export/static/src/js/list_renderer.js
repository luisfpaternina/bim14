odoo.define('tree_excel_export.ListRenderer', function (require) {
    "use strict";

    const { _t } = require('web.core');
    var ListRenderer = require('web.ListRenderer');
    var framework = require('web.framework');
    var session = require('web.session');

    ListRenderer.include({
        async _renderView() {
            await this._super.apply(this, arguments);
            if (this.arch.attrs.excel_export === '1' && !this.optionalColumns.length) {
                this.el.classList.add('o_list_optional_columns');
                this.$('table').append($('<i class="o_optional_columns_dropdown_toggle fa fa-ellipsis-v"/>'));
                this.$el.append(this._renderOptionalColumnsDropdown());
            }
        },
        _renderOptionalColumnsDropdown: function () {
            var $optionals = this._super.apply(this, arguments);
            if (this.arch.attrs.excel_export === '1') {
                const self = this;
                var $dropdown = $optionals.find('.o_optional_columns_dropdown');
                if ($dropdown.children().length) {
                    $dropdown.prepend($('<div class="dropdown-divider"/>'))
                }
                var $export_btn = $('<a>', {
                    class: 'dropdown-item',
                    text: _t('Export excel'),
                    href: '#'
                });
                $dropdown.prepend($export_btn.prepend($('<i>', { class: 'fa fa-file-excel-o mr-2' })));
                $export_btn.click(function (ev) {
                    ev.stopPropagation();
                    ev.preventDefault();
                    self._onToggleOptionalColumnDropdown(ev);
                    framework.blockUI();
                    const $table = self.$('.o_list_table');
                    const header = _.map($table.find('thead th'), th => $(th).text());
                    const body = _.map($table.find('tbody tr'), function (tr) {
                        const $tr = $(tr);
                        return _.map($tr.find('td'), td => $(td).text());
                    });
                    return new Promise(function (resolve, reject) {
                        var blocked = !session.get_file({
                            url: '/tree_excel_export/download',
                            data: {
                                header: JSON.stringify(header),
                                body: JSON.stringify(body),
                            },
                            success: resolve,
                            error: (error) => {
                                self.call('crash_manager', 'rpc_error', error);
                                reject();
                            },
                            complete: framework.unblockUI,
                        });
                        if (blocked) {
                            var message = _t('A popup window with your report was blocked. You ' +
                                'may need to change your browser settings to allow ' +
                                'popup windows for this page.');
                            self.do_warn(_t('Warning'), message, true);
                        }
                    });
                });
            }
            return $optionals;
        },
        _onToggleOptionalColumn: function (ev) {
            ev.stopPropagation();
            ev.preventDefault();
            var input = ev.currentTarget.querySelector('input');
            if (!input) return;
            this._super.apply(this, arguments);
        },
    });
});
