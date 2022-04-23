odoo.define('folder_view.renderer', function (require) {
    "use strict";

    var ListRenderer = require('web.ListRenderer');

    var FolderRenderer = ListRenderer.extend({
        init: function (parent, state, params) {
            state.fieldsInfo.list = state.fieldsInfo.folder;
            this._super.apply(this, arguments);
            this.parent_field = params.arch.attrs.parent_field || 'parent_id';
        },
        _getNumberOfCols: function () {
            return this._super.apply(this, arguments) + 1;
        },
        _renderHeader: function () {
            var $thead = this._super.apply(this, arguments);
            if (this.hasSelectors) {
                $thead.find('.o_list_record_selector').after('<th/>');
            } else {
                $thead.find('tr').prepend('<th class="o_folder_open_record"/>');
            }
            return $thead;
        },
        _renderFooter: function () {
            var $tfoot = this._super.apply(this, arguments);
            $tfoot.find('tr').prepend('<th/>');
            return $tfoot;
        },
        _renderRow: function (record) {
            var $row = this._super.apply(this, arguments);
            var el = '<td class="o_folder_open_record"><button class="btn"><i class="fa fa-external-link"/></button></td>';
            if (this.hasSelectors) {
                $row.find('.o_list_record_selector').after(el);
            } else {
                $row.prepend(el);
            }
            return $row;
        },
        _onRowClicked: function (ev) {
            var id = $(ev.currentTarget).data('id');
            var record = this._getRecord(id);
            if (ev.target.closest('.o_folder_open_record')) {
                if (id) {
                    this.trigger_up('open_record', { id: id, target: ev.target });
                }
            } else if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click') && record) {
                var context = {};
                var default_field = 'default_' + this.parent_field;
                context[default_field] = record.res_id;
                const folder_view = this.__parentedParent.actionViews.find(a => a.type === 'folder');
                this.do_action({
                    type: 'ir.actions.act_window',
                    name: record.data.display_name || record.data.name,
                    view_mode: this.__parentedParent.actionViews.map(a => a.type).join(','),
                    views: [[folder_view ? folder_view.viewID : false, 'folder']].concat(this.__parentedParent.actionViews.filter(a => a.type != 'folder').map(a => [a.viewID, a.type])),
                    res_model: this.state.model,
                    domain: [[this.parent_field, '=', record.res_id]],
                    context: context,
                });
            }
        },
    });

    return FolderRenderer;
});