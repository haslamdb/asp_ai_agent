ADMIN_DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Dashboard - ASP AI Agent</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .stat-card { transition: transform 0.2s; }
        .stat-card:hover { transform: translateY(-2px); }
        .user-row:hover { background-color: #f9fafb; }
        .modal { display: none; }
        .modal.active { display: flex; }
    </style>
</head>
<body class="bg-gray-100 min-h-screen">
    <!-- Navigation -->
    <nav class="bg-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div class="flex justify-between items-center">
                <div>
                    <h1 class="text-2xl font-bold text-gray-900">ASP AI Agent - Admin Dashboard</h1>
                    <p class="text-sm text-gray-600">User Management & Analytics</p>
                </div>
                <div class="space-x-4">
                    <a href="/dashboard" class="text-indigo-600 hover:text-indigo-800">Dashboard</a>
                    <a href="/logout" class="text-red-600 hover:text-red-800">Logout</a>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Statistics Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6 stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Total Users</p>
                        <p class="text-3xl font-bold text-gray-900" id="stat-total-users">-</p>
                    </div>
                    <div class="bg-blue-100 rounded-full p-3">
                        <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6 stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Active Users</p>
                        <p class="text-3xl font-bold text-green-600" id="stat-active-users">-</p>
                    </div>
                    <div class="bg-green-100 rounded-full p-3">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6 stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">New This Week</p>
                        <p class="text-3xl font-bold text-purple-600" id="stat-new-users">-</p>
                    </div>
                    <div class="bg-purple-100 rounded-full p-3">
                        <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
                        </svg>
                    </div>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow p-6 stat-card">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-sm font-medium text-gray-600">Total Sessions</p>
                        <p class="text-3xl font-bold text-orange-600" id="stat-total-sessions">-</p>
                    </div>
                    <div class="bg-orange-100 rounded-full p-3">
                        <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                    </div>
                </div>
            </div>
        </div>

        <!-- Users Table -->
        <div class="bg-white rounded-lg shadow">
            <div class="px-6 py-4 border-b border-gray-200">
                <div class="flex justify-between items-center">
                    <h2 class="text-xl font-bold text-gray-900">User Management</h2>
                    <div class="flex space-x-4">
                        <input type="text" id="search-users" placeholder="Search users..."
                               class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent">
                        <button onclick="loadUsers()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700">
                            Refresh
                        </button>
                    </div>
                </div>
            </div>

            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Institution</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Activity</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Login</th>
                            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                    </thead>
                    <tbody id="users-table-body" class="bg-white divide-y divide-gray-200">
                        <!-- Users will be loaded here -->
                    </tbody>
                </table>
            </div>

            <div id="loading" class="text-center py-8">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
                <p class="mt-2 text-gray-600">Loading users...</p>
            </div>

            <div id="no-users" class="text-center py-8 hidden">
                <p class="text-gray-600">No users found</p>
            </div>
        </div>
    </div>

    <!-- User Detail Modal -->
    <div id="user-detail-modal" class="modal fixed inset-0 bg-gray-600 bg-opacity-50 items-center justify-center p-4 z-50">
        <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div class="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 class="text-xl font-bold text-gray-900">User Details</h3>
                <button onclick="closeModal()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div id="user-detail-content" class="px-6 py-4">
                <!-- User details will be loaded here -->
            </div>
        </div>
    </div>

    <script>
        let allUsers = [];

        // Load statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/admin/stats');
                const data = await response.json();

                document.getElementById('stat-total-users').textContent = data.total_users;
                document.getElementById('stat-active-users').textContent = data.active_users;
                document.getElementById('stat-new-users').textContent = data.new_users_this_week;
                document.getElementById('stat-total-sessions').textContent = data.total_sessions;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Load users
        async function loadUsers() {
            const tbody = document.getElementById('users-table-body');
            const loading = document.getElementById('loading');
            const noUsers = document.getElementById('no-users');

            loading.classList.remove('hidden');
            tbody.innerHTML = '';

            try {
                const response = await fetch('/api/admin/users');
                const data = await response.json();
                allUsers = data.users;

                loading.classList.add('hidden');

                if (allUsers.length === 0) {
                    noUsers.classList.remove('hidden');
                } else {
                    noUsers.classList.add('hidden');
                    renderUsers(allUsers);
                }
            } catch (error) {
                console.error('Error loading users:', error);
                loading.classList.add('hidden');
                tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-4 text-center text-red-600">Error loading users</td></tr>';
            }
        }

        // Render users in table
        function renderUsers(users) {
            const tbody = document.getElementById('users-table-body');
            tbody.innerHTML = '';

            users.forEach(user => {
                const row = document.createElement('tr');
                row.className = 'user-row';

                const statusBadge = user.is_active
                    ? '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Active</span>'
                    : '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Blocked</span>';

                const verifiedBadge = user.email_verified
                    ? '<span class="text-green-600">✓</span>'
                    : '<span class="text-gray-400">✗</span>';

                const adminBadge = user.is_admin
                    ? '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800 ml-2">Admin</span>'
                    : '';

                const lastLogin = user.last_login
                    ? new Date(user.last_login).toLocaleString()
                    : 'Never';

                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div>
                            <div class="text-sm font-medium text-gray-900">${user.full_name}</div>
                            <div class="text-sm text-gray-500">${user.email} ${verifiedBadge}</div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">${user.institution || 'N/A'}</div>
                        <div class="text-sm text-gray-500">${user.specialty || 'N/A'}</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="text-sm text-gray-900">${user.session_count} sessions</div>
                        <div class="text-sm text-gray-500">${user.modules_completed}/${user.modules_started} modules</div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        ${statusBadge}${adminBadge}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        ${lastLogin}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button onclick="viewUser(${user.id})" class="text-indigo-600 hover:text-indigo-900">View</button>
                        ${!user.is_admin ? `
                            <button onclick="toggleActive(${user.id}, ${user.is_active})"
                                    class="text-${user.is_active ? 'yellow' : 'green'}-600 hover:text-${user.is_active ? 'yellow' : 'green'}-900">
                                ${user.is_active ? 'Block' : 'Unblock'}
                            </button>
                            ${!user.is_admin ? `<button onclick="makeAdmin(${user.id})" class="text-purple-600 hover:text-purple-900">Make Admin</button>` : ''}
                            <button onclick="deleteUser(${user.id}, '${user.email}')" class="text-red-600 hover:text-red-900">Delete</button>
                        ` : '<span class="text-gray-400">Protected</span>'}
                    </td>
                `;

                tbody.appendChild(row);
            });
        }

        // Search users
        document.getElementById('search-users').addEventListener('input', (e) => {
            const search = e.target.value.toLowerCase();
            const filtered = allUsers.filter(user =>
                user.email.toLowerCase().includes(search) ||
                user.full_name.toLowerCase().includes(search) ||
                (user.institution && user.institution.toLowerCase().includes(search))
            );
            renderUsers(filtered);
        });

        // View user details
        async function viewUser(userId) {
            try {
                const response = await fetch(`/api/admin/users/${userId}`);
                const data = await response.json();

                const content = document.getElementById('user-detail-content');
                content.innerHTML = `
                    <div class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm font-medium text-gray-500">Email</p>
                                <p class="text-sm text-gray-900">${data.user.email}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">Full Name</p>
                                <p class="text-sm text-gray-900">${data.user.full_name}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">Institution</p>
                                <p class="text-sm text-gray-900">${data.user.institution || 'N/A'}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">Fellowship Year</p>
                                <p class="text-sm text-gray-900">${data.user.fellowship_year || 'N/A'}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">Specialty</p>
                                <p class="text-sm text-gray-900">${data.user.specialty || 'N/A'}</p>
                            </div>
                            <div>
                                <p class="text-sm font-medium text-gray-500">Created</p>
                                <p class="text-sm text-gray-900">${new Date(data.user.created_at).toLocaleString()}</p>
                            </div>
                        </div>

                        <div class="mt-6">
                            <h4 class="text-lg font-semibold mb-2">Recent Sessions (${data.recent_sessions.length})</h4>
                            ${data.recent_sessions.length > 0 ? `
                                <div class="space-y-2">
                                    ${data.recent_sessions.map(s => `
                                        <div class="border-l-4 border-indigo-500 pl-4 py-2">
                                            <p class="text-sm font-medium">${s.module_name || s.session_type}</p>
                                            <p class="text-xs text-gray-500">${new Date(s.started_at).toLocaleString()}</p>
                                            <p class="text-xs text-gray-500">Model: ${s.model_used}</p>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : '<p class="text-gray-500">No sessions yet</p>'}
                        </div>

                        <div class="mt-6">
                            <h4 class="text-lg font-semibold mb-2">Module Progress (${data.progress.length})</h4>
                            ${data.progress.length > 0 ? `
                                <div class="space-y-2">
                                    ${data.progress.map(p => `
                                        <div class="border-l-4 ${p.completed ? 'border-green-500' : 'border-yellow-500'} pl-4 py-2">
                                            <p class="text-sm font-medium">${p.module_name}</p>
                                            <p class="text-xs text-gray-500">
                                                ${p.completed ? '✓ Completed' : 'In Progress'}
                                                - Attempts: ${p.attempts}
                                                ${p.score ? ` - Score: ${p.score}` : ''}
                                            </p>
                                        </div>
                                    `).join('')}
                                </div>
                            ` : '<p class="text-gray-500">No progress yet</p>'}
                        </div>
                    </div>
                `;

                document.getElementById('user-detail-modal').classList.add('active');
            } catch (error) {
                console.error('Error loading user details:', error);
                alert('Error loading user details');
            }
        }

        // Close modal
        function closeModal() {
            document.getElementById('user-detail-modal').classList.remove('active');
        }

        // Toggle user active status
        async function toggleActive(userId, currentStatus) {
            const action = currentStatus ? 'block' : 'unblock';
            if (!confirm(`Are you sure you want to ${action} this user?`)) return;

            try {
                const response = await fetch(`/api/admin/users/${userId}/toggle-active`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    loadUsers();
                    loadStats();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error toggling user status:', error);
                alert('Error toggling user status');
            }
        }

        // Delete user
        async function deleteUser(userId, email) {
            if (!confirm(`Are you sure you want to permanently delete ${email}? This action cannot be undone.`)) return;
            if (!confirm(`Really delete ${email}? All their data will be lost.`)) return;

            try {
                const response = await fetch(`/api/admin/users/${userId}/delete`, {
                    method: 'DELETE'
                });
                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    loadUsers();
                    loadStats();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error deleting user:', error);
                alert('Error deleting user');
            }
        }

        // Make user admin
        async function makeAdmin(userId) {
            if (!confirm('Are you sure you want to make this user an admin?')) return;

            try {
                const response = await fetch(`/api/admin/users/${userId}/make-admin`, {
                    method: 'POST'
                });
                const data = await response.json();

                if (data.success) {
                    alert(data.message);
                    loadUsers();
                    loadStats();
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error making user admin:', error);
                alert('Error making user admin');
            }
        }

        // Initialize
        loadStats();
        loadUsers();
    </script>
</body>
</html>
'''
