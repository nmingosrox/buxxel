$(document).ready(function() {
    const ordersTableBody = $('#my-orders-table-body');
    const loadingSpinner = $('#loading-spinner');
    const noOrdersMessage = $('#no-orders-message');

    async function fetchMyOrders() {
        loadingSpinner.show();
        ordersTableBody.empty();
        noOrdersMessage.hide();

        try {
            const { data: sessionData, error: sessionError } = await window.supabaseClient.auth.getSession();
            if (sessionError || !sessionData.session) {
                throw new Error("Authentication error. Please log in again.");
            }
            const token = sessionData.session.access_token;

            const response = await fetch('/api/me/orders', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Failed to fetch your orders. Status: ${response.status}`);
            }

            const orders = await response.json();

            if (orders.length === 0) {
                noOrdersMessage.show();
            } else {
                orders.forEach(order => {
                    const orderDate = new Date(order.created_at).toLocaleDateString();
                    const orderRow = `
                        <tr>
                            <td><small>${order.id}</small></td>
                            <td>${orderDate}</td>
                            <td>N$${order.total_price.toFixed(2)}</td>
                            <td><span class="badge bg-info text-dark">${order.status}</span></td>
                        </tr>
                    `;
                    ordersTableBody.append(orderRow);
                });
            }
        } catch (error) {
            console.error("Error fetching my orders:", error);
            ordersTableBody.html(`<tr><td colspan="4" class="text-center text-danger">Could not load your orders. ${error.message}</td></tr>`);
        } finally {
            loadingSpinner.hide();
        }
    }

    // Initial load
    fetchMyOrders();
});