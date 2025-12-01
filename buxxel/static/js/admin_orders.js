$(document).ready(function() {
    const ordersTableBody = $('#orders-table-body');
    const loadingSpinner = $('#loading-spinner');
    const noOrdersMessage = $('#no-orders-message');

    async function fetchOrders() {
        loadingSpinner.show();
        ordersTableBody.empty();
        noOrdersMessage.hide();

        try {
            const { data: sessionData, error: sessionError } = await window.supabaseClient.auth.getSession();
            if (sessionError || !sessionData.session) {
                throw new Error("Authentication error. Please log in again.");
            }
            const token = sessionData.session.access_token;

            const response = await fetch('/api/admin/orders', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch orders. Status: ${response.status}`);
            }

            const orders = await response.json();

            if (orders.length === 0) {
                noOrdersMessage.show();
            } else {
                orders.forEach(order => {
                    const customerName = order.profiles ? (order.profiles.username || order.profiles.email) : 'N/A';
                    const orderDate = new Date(order.created_at).toLocaleDateString();
                    const orderRow = `
                        <tr data-order-id="${order.id}">
                            <td><small>${order.id}</small></td>
                            <td>${customerName}</td>
                            <td>${orderDate}</td>
                            <td>N$${order.total_price.toFixed(2)}</td>
                            <td><span class="badge bg-info text-dark">${order.status}</span></td>
                            <td>
                                <select class="form-select form-select-sm status-select" data-order-id="${order.id}">
                                    <option value="${order.status}" selected>${order.status}</option>
                                    <option value="Pending">Pending</option>
                                    <option value="Shipped">Shipped</option>
                                    <option value="Delivered">Delivered</option>
                                    <option value="Cancelled">Cancelled</option>
                                </select>
                                <button class="btn btn-sm btn-primary mt-1 update-status-btn" data-order-id="${order.id}" style="display: none;">
                                    Update
                                </button>
                            </td>
                        </tr>
                    `;
                    ordersTableBody.append(orderRow);
                });
            }
        } catch (error) {
            console.error("Error fetching orders:", error);
            ordersTableBody.html(`<tr><td colspan="6" class="text-center text-danger">Could not load orders. ${error.message}</td></tr>`);
        } finally {
            loadingSpinner.hide();
        }
    }

    // Show the "Update" button when a new status is selected
    ordersTableBody.on('change', '.status-select', function() {
        const updateBtn = $(this).siblings('.update-status-btn');
        updateBtn.show();
    });

    // Handle the click on the "Update" button
    ordersTableBody.on('click', '.update-status-btn', async function() {
        const orderId = $(this).data('order-id');
        const updateBtn = $(this);
        const selectElement = updateBtn.siblings('.status-select');
        const newStatus = selectElement.val();

        if (!newStatus) return;

        updateBtn.prop('disabled', true).html('<span class="spinner-border spinner-border-sm"></span>');

        try {
            const { data: sessionData, error: sessionError } = await window.supabaseClient.auth.getSession();
            if (sessionError || !sessionData.session) throw new Error("Authentication error.");
            const token = sessionData.session.access_token;

            const response = await fetch(`/api/admin/orders/${orderId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ status: newStatus })
            });

            if (!response.ok) throw new Error('Failed to update status.');

            const updatedOrder = await response.json();
            // Update the badge in the UI
            const statusBadge = selectElement.closest('tr').find('.badge');
            statusBadge.text(updatedOrder.status).removeClass('bg-info bg-success').addClass('bg-success'); // Change color for feedback
            updateBtn.hide(); // Hide the button after successful update

        } catch (error) {
            console.error("Error updating status:", error);
            alert(`Failed to update status for order ${orderId}.`);
        } finally {
            updateBtn.prop('disabled', false).html('Update');
        }
    });

    // Initial load
    fetchOrders();
});