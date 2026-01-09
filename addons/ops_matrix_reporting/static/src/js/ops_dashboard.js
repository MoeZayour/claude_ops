/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class OpsDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            dashboardData: {},
            loading: true,
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        const dashboardId = this.props.action.context.dashboard_id || this.props.action.params.dashboard_id;
        if (dashboardId) {
            this.state.dashboardData = await this.rpc("/web/dataset/call_kw/ops.dashboard/get_dashboard_data", {
                model: "ops.dashboard",
                method: "get_dashboard_data",
                args: [dashboardId],
                kwargs: {},
            });
            this.state.loading = false;
        }
    }

    onWidgetClick(widget) {
        if (widget.config && widget.config.action) {
            this.action.doAction(widget.config.action);
        }
    }
}

OpsDashboard.template = "ops_matrix_reporting.OpsDashboard";

registry.category("actions").add("ops_dashboard_tag", OpsDashboard);
