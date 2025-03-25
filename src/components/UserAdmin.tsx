import React, { useState, useEffect } from 'react';
import { UserPlus, Trash2, Edit, X, Check, Search } from 'lucide-react';

interface User {
  id: number;
  username: string;
  email: string;
  role: 'USER' | 'TRAINER' | 'ADMIN';
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string;
}

interface UserFormData {
  username: string;
  email: string;
  password: string;
  role: 'USER' | 'TRAINER' | 'ADMIN';
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_superuser: boolean;
}

export function UserAdmin() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<UserFormData>({
    username: '',
    email: '',
    password: '',
    role: 'USER',
    first_name: '',
    last_name: '',
    is_active: true,
    is_superuser: false
  });

  // Cargar usuarios
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/users/admin/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Para enviar cookies de sesión
      });

      if (!response.ok) {
        throw new Error('No tienes permisos para acceder a esta sección');
      }

      const data = await response.json();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al cargar usuarios');
    } finally {
      setLoading(false);
    }
  };

  // Filtrar usuarios
  const filteredUsers = users.filter(user => {
    return user.username.toLowerCase().includes(searchQuery.toLowerCase()) ||
           user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
           user.role.toLowerCase().includes(searchQuery.toLowerCase());
  });

  // Iniciar creación de usuario
  const handleAddUser = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      role: 'USER',
      first_name: '',
      last_name: '',
      is_active: true,
      is_superuser: false
    });
    setEditingUser(null);
    setShowForm(true);
  };

  // Iniciar edición de usuario
  const handleEditUser = (user: User) => {
    setFormData({
      username: user.username,
      email: user.email,
      password: '',
      role: user.role,
      first_name: user.first_name,
      last_name: user.last_name,
      is_active: user.is_active,
      is_superuser: user.is_superuser
    });
    setEditingUser(user);
    setShowForm(true);
  };

  // Enviar formulario (crear o actualizar)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      
      const url = editingUser 
        ? `/api/users/admin/${editingUser.id}/`
        : '/api/users/admin/';
      
      const method = editingUser ? 'PUT' : 'POST';
      
      // Solo incluir password si se proporcionó
      const dataToSend = {...formData};
      if (!dataToSend.password) {
        delete dataToSend.password;
      }
      
      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(dataToSend)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error en la operación');
      }

      // Recargar la lista de usuarios
      await fetchUsers();
      setShowForm(false);
      setEditingUser(null);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar usuario');
    } finally {
      setLoading(false);
    }
  };

  // Eliminar usuario
  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
      return;
    }
    
    try {
      setLoading(true);
      
      const response = await fetch(`/api/users/admin/${userId}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al eliminar usuario');
      }

      // Recargar la lista de usuarios
      await fetchUsers();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar usuario');
    } finally {
      setLoading(false);
    }
  };

  // Cancelar formulario
  const handleCancel = () => {
    setShowForm(false);
    setEditingUser(null);
    setError(null);
  };

  if (loading && users.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Administración de Usuarios</h1>
      
      {error && (
        <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
          <span className="block sm:inline">{error}</span>
          <button
            onClick={() => setError(null)}
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
          >
            <X className="h-5 w-5" />
          </button>
        </div>
      )}
      
      {/* Controles superiores */}
      <div className="flex flex-wrap gap-4 items-center justify-between mb-6">
        <div className="relative w-full md:w-1/3">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Buscar usuarios..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          />
        </div>
        
        <button
          onClick={handleAddUser}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
        >
          <UserPlus className="h-5 w-5" />
          <span>Agregar Usuario</span>
        </button>
      </div>
      
      {/* Formulario de creación/edición */}
      {showForm && (
        <div className="mb-8 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">
            {editingUser ? 'Editar Usuario' : 'Crear Nuevo Usuario'}
          </h2>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de Usuario*
                </label>
                <input
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email*
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {editingUser ? 'Contraseña (dejar en blanco para mantener)' : 'Contraseña*'}
                </label>
                <input
                  type="password"
                  required={!editingUser}
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rol*
                </label>
                <select
                  required
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value as 'USER' | 'TRAINER' | 'ADMIN'})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="USER">Usuario</option>
                  <option value="TRAINER">Entrenador</option>
                  <option value="ADMIN">Administrador</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre
                </label>
                <input
                  type="text"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Apellido
                </label>
                <input
                  type="text"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                />
                <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                  Usuario activo
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_superuser"
                  checked={formData.is_superuser}
                  onChange={(e) => setFormData({...formData, is_superuser: e.target.checked})}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                />
                <label htmlFor="is_superuser" className="ml-2 block text-sm text-gray-700">
                  Superusuario (acceso completo)
                </label>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                onClick={handleCancel}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Cancelar
              </button>
              
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white"></div>
                ) : (
                  <Check className="h-5 w-5" />
                )}
                <span>Guardar</span>
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Tabla de usuarios */}
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Usuario
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Correo
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rol
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Fecha Registro
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredUsers.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                  No se encontraron usuarios
                </td>
              </tr>
            ) : (
              filteredUsers.map(user => (
                <tr key={user.id} className={!user.is_active ? 'bg-gray-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">
                          {user.username}
                          {user.is_superuser && (
                            <span className="ml-1 text-xs font-medium text-red-600">(Super)</span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500">
                          {user.first_name} {user.last_name}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{user.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${user.role === 'ADMIN' ? 'bg-purple-100 text-purple-800' : 
                        user.role === 'TRAINER' ? 'bg-blue-100 text-blue-800' : 
                                               'bg-green-100 text-green-800'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.date_joined).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex items-center space-x-3">
                      <button
                        onClick={() => handleEditUser(user)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Edit className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
} 