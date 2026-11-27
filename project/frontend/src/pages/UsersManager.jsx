import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserPlus, 
  ShieldCheck, 
  ShieldAlert, 
  Eye, 
  Trash2, 
  CheckCircle2, 
  XCircle,
  KeyRound
} from 'lucide-react';
import { api } from '../api/client';
import Modal from '../components/Modal';
import { useLanguage } from '../i18n/LanguageContext';

export default function UsersManager({ currentUser }) {
  const { t } = useLanguage();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  // Form states
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('admin');

  // Modal states
  const [modalConfig, setModalConfig] = useState({
    isOpen: false,
    title: '',
    message: '',
    type: 'info',
    onConfirm: null,
    confirmText: 'Confirmer',
  });

  const closeModal = () => {
    setModalConfig(prev => ({ ...prev, isOpen: false }));
  };

  const showInfoModal = (title, message, type = 'info') => {
    setModalConfig({
      isOpen: true,
      title,
      message,
      type,
      onConfirm: null,
    });
  };

  const showConfirmModal = (title, message, onConfirm, type = 'danger', confirmText = 'Confirmer') => {
    setModalConfig({
      isOpen: true,
      title,
      message,
      type,
      onConfirm: () => {
        closeModal();
        onConfirm();
      },
      confirmText,
    });
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await api.getUsers();
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      showInfoModal('Erreur', err.message || "Impossible de charger les utilisateurs", 'danger');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreateUser = async (e) => {
    e.preventDefault();
    if (!username.trim() || !password) return;
    setSubmitting(true);
    try {
      await api.createUser({
        username: username.trim(),
        password,
        role,
      });
      setUsername('');
      setPassword('');
      setRole('admin');
      await loadUsers();
      showInfoModal('Succès', `L'administrateur ${username} a été créé avec le rôle ${role}.`, 'success');
    } catch (err) {
      showInfoModal('Erreur de création', err.message || "Impossible de créer le compte", 'danger');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = (user) => {
    const nextStatus = !user.is_active;
    const actionLabel = nextStatus ? 'réactiver' : 'désactiver';
    showConfirmModal(
      'Modification du compte',
      `Voulez-vous vraiment ${actionLabel} le compte "${user.username}" ?`,
      async () => {
        try {
          await api.updateUser(user.id, { is_active: nextStatus });
          await loadUsers();
          showInfoModal('Succès', `Le compte ${user.username} a été mis à jour.`, 'success');
        } catch (err) {
          showInfoModal('Erreur', err.message, 'danger');
        }
      },
      nextStatus ? 'info' : 'danger',
      nextStatus ? 'Réactiver' : 'Désactiver'
    );
  };

  const handleRoleChange = async (user, newRole) => {
    if (user.role === newRole) return;
    try {
      await api.updateUser(user.id, { role: newRole });
      await loadUsers();
      showInfoModal('Rôle mis à jour', `Le compte ${user.username} a désormais le rôle ${newRole}.`, 'success');
    } catch (err) {
      showInfoModal('Erreur', err.message, 'danger');
    }
  };

  const isSuperadmin = currentUser?.role === 'superadmin';

  if (!isSuperadmin) {
    return (
      <div className="p-6 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-200 text-xs">
        Seuls les comptes <strong>Superadmin</strong> peuvent administrer les accès et gérer les administrateurs de la plateforme.
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      <Modal
        isOpen={modalConfig.isOpen}
        onClose={closeModal}
        onConfirm={modalConfig.onConfirm}
        title={modalConfig.title}
        message={modalConfig.message}
        type={modalConfig.type}
        confirmText={modalConfig.confirmText}
      />

      {/* Header */}
      <div>
        <div className="flex items-center space-x-2 text-indigo-600 dark:text-indigo-400 text-xs font-mono uppercase tracking-wider">
          <Users className="h-4 w-4" />
          <span>Contrôle d'Accès & Multi-Admins</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
          Gestion des Administrateurs
        </h1>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Créez de nouveaux comptes d'accès, attribuez des rôles (Superadmin, Admin, Viewer) et gérez les autorisations.
        </p>
      </div>

      {/* Create User Form */}
      <div className="p-6 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
        <h2 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2 mb-4">
          <UserPlus className="h-4 w-4 text-indigo-500" />
          Créer un nouvel administrateur
        </h2>
        <form onSubmit={handleCreateUser} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Identifiant / Email
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="ex: marie.dupont"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Mot de passe initial
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min. 6 caractères"
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
              Niveau d'accès / Rôle
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="admin">Admin (Opérations & Datasets)</option>
              <option value="superadmin">Superadmin (Gestion complète + Comptes)</option>
              <option value="viewer">Viewer (Lecture seule & Rapports)</option>
            </select>
          </div>
          <div>
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-semibold transition-colors disabled:opacity-50"
            >
              {submitting ? 'Création en cours...' : 'Ajouter le compte'}
            </button>
          </div>
        </form>
      </div>

      {/* Users List Table */}
      <div className="rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center">
          <span className="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Comptes Actifs ({users.length})
          </span>
          {loading && <span className="text-xs text-slate-400">Chargement...</span>}
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-300">
            <thead className="bg-slate-50 dark:bg-slate-950/50 text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-6 py-3">Utilisateur</th>
                <th className="px-6 py-3">Rôle actuel</th>
                <th className="px-6 py-3">Statut</th>
                <th className="px-6 py-3">Créé le</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 font-sans">
              {users.map((u) => {
                const isCurrent = currentUser?.id === u.id;
                return (
                  <tr key={u.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/30 transition-colors">
                    <td className="px-6 py-4 font-semibold text-slate-900 dark:text-white flex items-center gap-2">
                      <div className="h-7 w-7 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-700 dark:text-slate-300">
                        {u.username.slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <span>{u.username}</span>
                        {isCurrent && (
                          <span className="ml-2 px-1.5 py-0.5 rounded text-[10px] bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 font-semibold">
                            Vous
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={u.role}
                        disabled={isCurrent}
                        onChange={(e) => handleRoleChange(u, e.target.value)}
                        className="px-2 py-1 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium focus:outline-none disabled:opacity-60"
                      >
                        <option value="superadmin">Superadmin</option>
                        <option value="admin">Admin</option>
                        <option value="viewer">Viewer</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      {u.is_active ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                          <CheckCircle2 className="h-3 w-3" /> Actif
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800">
                          <XCircle className="h-3 w-3" /> Désactivé
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-slate-400 text-[11px]">
                      {new Date(u.created_at).toLocaleDateString('fr-FR', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleToggleActive(u)}
                        disabled={isCurrent}
                        className={`px-3 py-1 rounded-lg text-[11px] font-semibold transition-colors disabled:opacity-40 ${
                          u.is_active 
                            ? 'text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60'
                            : 'text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900/60'
                        }`}
                      >
                        {u.is_active ? 'Désactiver' : 'Réactiver'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
