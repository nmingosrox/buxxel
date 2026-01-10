document.addEventListener('DOMContentLoaded', function () {
    const tableBody = document.getElementById('users-table-body');
    const loadingSpinner = document.getElementById('loading-spinner');
    const noUsersMessage = document.getElementById('no-users-message');

    async function fetchAndRenderUsers() {
        try {
            const response = await fetch('/admin/api/users');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const users = await response.json();

            // Hide spinner once data is loaded
            loadingSpinner.style.display = 'none';
            tableBody.innerHTML = ''; // Clear existing rows
            noUsersMessage.style.display = 'none';

            if (users.length === 0) {
                noUsersMessage.style.display = 'block';
            } else {
                users.forEach(user => {
                    const row = createUserRow(user);
                    tableBody.appendChild(row);
                });
            }
        } catch (error) {
            // Hide spinner and show error in table
            loadingSpinner.style.display = 'none';
            tableBody.innerHTML = `<tr>
                <td colspan="5" class="text-center text-danger">
                    Failed to load users.<br>
                    <strong>Error:</strong> ${error.message}
                </td>
            </tr>`;
        }
    }

    function createUserRow(user) {
        const row = document.createElement('tr');

        const roleBadge = user.user_role === 'admin'
            ? `<span class="badge bg-danger">Admin</span>`
            : `<span class="badge bg-secondary">User</span>`;

        const joinedDate = new Date(user.created_at).toLocaleDateString();

        // ID cell (shortened UUID)
        const idCell = row.insertCell();
        idCell.textContent = `${user.id.substring(0, 8)}...`;

        // Username cell
        const usernameCell = row.insertCell();
        usernameCell.textContent = user.username;

        // Role cell
        const roleCell = row.insertCell();
        roleCell.innerHTML = roleBadge;

        // Joined date cell
        const joinedCell = row.insertCell();
        joinedCell.textContent = joinedDate;

        // Actions cell
        const actionsCell = row.insertCell();
        actionsCell.innerHTML = `
            <button class="btn btn-sm btn-outline-primary" title="Edit Role">
                <i class="bi bi-person-badge"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger" title="Delete User">
                <i class="bi bi-trash-fill"></i>
            </button>
        `;

        return row;
    }

    // Initial fetch
    fetchAndRenderUsers();
});
