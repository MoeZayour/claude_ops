/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { patch } from "@web/core/utils/patch";

patch(ListController.prototype, {
    /**
     * Override export action to launch secure export wizard
     * Exemptions: IT Admin and System Admin keep native export
     */
    async onExportData() {
        const user = this.env.services.user;
        
        // Check if user is IT Admin or System Admin - they get native export
        const isITAdmin = await user.hasGroup('ops_matrix_core.group_ops_it_admin');
        const isSysAdmin = await user.hasGroup('base.group_system');
        
        if (isITAdmin || isSysAdmin) {
            // Call original export for exempt users
            return super.onExportData(...arguments);
        }
        
        // For all other users, launch secure export wizard
        const model = this.props.resModel;
        const domain = this.model.root.domain;
        const fields = this.model.root.fields;
        
        // Get visible field names from current list view
        const visibleFields = this.model.root.columns
            .filter(col => col.type !== 'field_handle' && col.name !== 'selector')
            .map(col => col.name);
        
        // Get model ID from ir.model
        const modelRecord = await this.env.services.orm.searchRead(
            'ir.model',
            [['model', '=', model]],
            ['id'],
            { limit: 1 }
        );
        
        if (!modelRecord || modelRecord.length === 0) {
            this.env.services.notification.add(
                'Model not found. Please contact your administrator.',
                { type: 'danger' }
            );
            return;
        }
        
        const modelId = modelRecord[0].id;
        
        // Get field IDs for visible fields
        let fieldIds = [];
        if (visibleFields.length > 0) {
            const fieldRecords = await this.env.services.orm.searchRead(
                'ir.model.fields',
                [
                    ['model_id', '=', modelId],
                    ['name', 'in', visibleFields],
                    ['store', '=', true]
                ],
                ['id']
            );
            fieldIds = fieldRecords.map(f => f.id);
        }
        
        // Launch wizard with context
        this.env.services.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Secure Export',
            res_model: 'ops.secure.export.wizard',
            view_mode: 'form',
            views: [[false, 'form']],
            target: 'new',
            context: {
                default_model_id: modelId,
                default_domain: JSON.stringify(domain),
                default_field_ids: [[6, 0, fieldIds]],
                active_model: model,
                active_domain: domain,
            }
        });
    }
});
