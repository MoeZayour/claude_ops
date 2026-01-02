/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";
import { formatFloat } from "@web/core/utils/formatters";

export class MatrixAvailabilityTab extends Component {
    static template = "ops_matrix_core.MatrixAvailabilityTab";
    static props = {
        record: Object,
        resModel: String,
        resId: Number,
    };

    setup() {
        // Component state for availability data
        this.state = useState({
            availabilityData: [],
            isLoading: true,
            error: null,
            userBranch: null,
            userBusinessUnit: null,
        });

        onWillStart(async () => {
            await this._loadAvailabilityData();
        });
    }

    /**
     * Load availability data from the server via RPC.
     *
     * Calls a controller method to get:
     * 1. Product availability per line
     * 2. Stock levels (masked if user lacks permission)
     * 3. User's effective matrix access (branch/BU)
     */
    async _loadAvailabilityData() {
        try {
            this.state.isLoading = true;
            this.state.error = null;

            // Call server to get availability data
            // This replaces the PDF download approach with JSON data
            const response = await rpc({
                route: "/web/dataset/call_kw/sale.order/get_availability_data_json",
                params: {
                    args: [this.props.resId],
                    kwargs: {},
                },
            });

            // Update state with returned data
            this.state.availabilityData = response.availability_data || [];
            this.state.userBranch = response.user_branch || null;
            this.state.userBusinessUnit = response.user_business_unit || null;
            this.state.isLoading = false;
        } catch (error) {
            this.state.isLoading = false;
            this.state.error = error.message || "Failed to load availability data";
            console.error("MatrixAvailabilityTab Error:", error);
        }
    }

    /**
     * Format quantity value with proper masking.
     *
     * If the value is "***", it means the user doesn't have permission
     * to see the actual stock level (masked).
     */
    formatQuantity(value) {
        if (value === "***") {
            return "***";
        }
        return formatFloat(value, { digits: [false, 2] });
    }

    /**
     * Get CSS class for availability status indicator.
     *
     * Returns "success" for in-stock, "danger" for low stock.
     */
    getStatusClass(item) {
        if (item.stock_on_hand === "***") {
            return "secondary"; // Unknown due to masking
        }
        return item.is_insufficient ? "danger" : "success";
    }

    /**
     * Get availability status badge text.
     */
    getStatusText(item) {
        if (item.stock_on_hand === "***") {
            return "Restricted";
        }
        return item.is_insufficient ? "Low Stock" : "In Stock";
    }

    /**
     * Refresh availability data.
     *
     * Called when user clicks the refresh button.
     */
    async refreshData() {
        await this._loadAvailabilityData();
    }

    /**
     * Download availability data as CSV.
     *
     * Exports the current availability view as a CSV file for external analysis.
     */
    downloadAsCSV() {
        if (!this.state.availabilityData || this.state.availabilityData.length === 0) {
            return;
        }

        // Prepare CSV headers
        const headers = ["SKU", "Product Name", "Ordered Qty", "Stock On Hand", "Available", "Status"];
        const rows = [headers];

        // Add data rows
        for (const item of this.state.availabilityData) {
            rows.push([
                item.sku || "",
                item.product_name || "",
                item.ordered_qty || "",
                this.formatQuantity(item.stock_on_hand),
                this.formatQuantity(item.display_qty),
                this.getStatusText(item),
            ]);
        }

        // Convert to CSV string
        const csvContent = rows.map((row) => row.map((cell) => `"${cell}"`).join(",")).join("\n");

        // Create download link
        const blob = new Blob([csvContent], { type: "text/csv" });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `Availability_${this.props.record.name || "Report"}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    /**
     * Generate PDF from current data.
     *
     * Alternative to CSV download - creates a printable PDF.
     */
    async generatePDF() {
        // This would call a server-side method to generate PDF
        try {
            const response = await rpc({
                route: "/web/dataset/call_kw/sale.order/generate_availability_pdf",
                params: {
                    args: [this.props.resId],
                    kwargs: {},
                },
            });

            // Trigger download
            if (response.pdf_url) {
                window.location.href = response.pdf_url;
            }
        } catch (error) {
            console.error("PDF Generation Error:", error);
        }
    }
}
