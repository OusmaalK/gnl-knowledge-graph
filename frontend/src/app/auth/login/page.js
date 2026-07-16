'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Cookies from 'js-cookie';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

function WorkflowColumn() {
  const workflows = [
    { icon: '📊', title: 'Dashboard', desc: 'Visualisez en temps réel la santé de votre réseau GNL.' },
    { icon: '🚨', title: 'Incidents', desc: 'Diagnostiquez les pannes et suivez leur résolution.' },
    { icon: '🗺️', title: 'Logistique', desc: 'Optimisez vos routes grâce à l’IA.' },
    { icon: '🧠', title: 'Maintenance', desc: 'Maintenance prédictive basée sur les données.' },
    { icon: '🤖', title: 'Assistant IA', desc: 'Interrogez votre Knowledge Graph.' },
    { icon: '📈', title: 'Analyses', desc: 'Graphiques et indicateurs avancés.' },
  ];

  return (
    <aside className="hidden lg:flex lg:w-1/3 xl:w-2/5 bg-gradient-to-br from-blue-900 to-indigo-900 text-white p-12 flex-col justify-center overflow-y-auto">
      <div className="mb-10">
        <div className="text-5xl mb-4">⛽</div>
        <h1 className="text-4xl font-bold mb-3">GNL Knowledge Graph</h1>
        <p className="text-blue-200">Plateforme intelligente pour le transport du Gaz Naturel Liquéfié.</p>
      </div>
      <div className="space-y-5">
        {workflows.map((item) => (
          <div key={item.title} className="rounded-xl bg-white/10 p-5 border border-white/10">
            <div className="flex gap-4">
              <div className="text-3xl">{item.icon}</div>
              <div>
                <h3 className="font-semibold text-lg">{item.title}</h3>
                <p className="text-blue-200 text-sm mt-1">{item.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </aside>
  );
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  // URL du backend via variable d'environnement ou fallback
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://gnl-knowledge-graph-production.up.railway.app';

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);

    try {
      // 1. Vérification et nettoyage des données
      const cleanEmail = email.trim();
      const cleanPassword = password.trim();

      // 2. Récupération robuste de l'URL
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://gnl-knowledge-graph-production.up.railway.app';
      console.log("🔗 Envoi vers:", `${API_URL}/api/auth/login`);

      // 3. Appel fetch avec gestion des erreurs réseau
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email: cleanEmail, 
          password: cleanPassword 
        }),
      });

      // 4. Lecture du corps de la réponse
      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        // Si le serveur ne répond pas avec du JSON valide
        throw new Error("Le serveur n'a pas renvoyé une réponse valide.");
      }

      // 5. Gestion des erreurs serveur
      if (!response.ok) {
        // Si le backend renvoie un message d'erreur, on l'affiche
        const errorMsg = data.detail || `Erreur serveur (${response.status})`;
        toast.error(errorMsg);
        throw new Error(errorMsg);
      }

      // --- SUCCÈS ---
      // Stockage du token et du rôle
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      Cookies.set('token', data.access_token, { expires: 7 });
      Cookies.set('role', data.role, { expires: 7 });

      toast.success('Connexion réussie');
      router.push('/');

    } catch (error) {
      // L'erreur est déjà gérée par le toast ci-dessus
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen w-full bg-gray-100">
      <WorkflowColumn />
      <section className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl p-8">
          <div className="text-center mb-8">
            <div className="text-5xl mb-3">⛽</div>
            <h2 className="text-3xl font-bold">Se connecter</h2>
            <p className="text-gray-500 mt-2">Accédez à votre plateforme GNL</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block mb-2 font-medium">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@gnl.com"
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <div>
              <label className="block mb-2 font-medium">Mot de passe</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="********"
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-blue-600 py-3 text-white hover:bg-blue-700 disabled:opacity-60 flex justify-center items-center gap-2"
            >
              {loading && <LoadingSpinner size="small" color="white" />}
              {loading ? 'Connexion...' : 'Se connecter'}
            </button>
          </form>

          <div className="mt-8 text-center">
            <span className="text-gray-500">Pas encore inscrit ?</span>
            <Link href="/auth/register" className="ml-2 text-blue-600 font-semibold hover:underline">
              Créer un compte
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
