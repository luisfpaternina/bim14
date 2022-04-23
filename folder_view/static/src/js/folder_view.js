odoo.define('folder_view.view', function (require) {
    "use strict";

    var core = require('web.core');
    var viewRegistry = require('web.view_registry');
    var ListView = require('web.ListView');
    var FolderRenderer = require('folder_view.renderer');

    var _lt = core._lt;

    var FolderView = ListView.extend({
        accesskey: 'f',
        display_name: _lt('Folder'),
        icon: 'fa-folder-open',
        viewType: 'folder',
        config: _.extend({}, ListView.prototype.config, {
            Renderer: FolderRenderer,
        }),
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            var found = false;
            if (this.loadParams.domain && this.loadParams.domain.length) {
                for (var i = 0; i < this.loadParams.domain.length; i++) {
                    var dom = this.loadParams.domain[i];
                    if (Array.isArray(dom) && dom.length === 3 && dom[0] === 'parent_id') {
                        found = true;
                        break;
                    }
                }

            }
            if (!found) {
                (this.loadParams.domain || []).push(['parent_id', '=', false]);
            }
        },
    });

    viewRegistry.add('folder', FolderView);
    return FolderView;
});