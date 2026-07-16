'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

function WorkflowColumn() {
  const workflows = [
    {
      icon: '📊',
      title: 'Dashboard',
      desc: 'Visualisez en temps réel la santé de votre réseau GNL.',
    },
    {
      icon: '🚨',
      title: 'Incidents',
      desc: 'Diagnostiquez les pannes et suivez leur résolution.',
    },
    {
      icon: '🗺️',
      title: 'Logistique',
      desc: "Optimisez vos routes grâce à l'IA.",
    },
    {
      icon: '🧠',
      title: 'Maintenance',
      desc: 'Maintenance prédictive basée sur les données.',
    },
    {
      icon: '🤖',
      title: 'Assistant IA',
      desc: 'Interrogez votre Knowledge Graph.',
    },
    {
      icon: '📈',
      title: 'Analyses',
      desc: 'Graphiques et indicateurs avancés.',
    },
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
          <div key={item.title} className="rounded-xl bg-white/10 border border-white/10 p-5">
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

export default function RegisterPage() {
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  // États pour gérer le succès de l'inscription
  const [isRegistered, setIsRegistered] = useState(false);
  const [registeredEmail, setRegisteredEmail] = useState('');

  // URL du backend via variable d'environnement
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://gnl-knowledge-graph-production.up.railway.app';

  async function handleSubmit(e) {
    e.preventDefault();

    // 1. Vérification de la confirmation du mot de passe
    if (password !== confirmPassword) {
      toast.error('Les mots de passe ne correspondent pas');
      return;
    }

    setLoading(true);

    try {
      // 2. Appel au backend avec fetch standard
      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      // Lire la réponse du backend
      const data = await response.json();

      // 3. Gérer les erreurs renvoyées par le backend
      if (!response.ok) {
        const errorMsg = data.detail || "Erreur lors de l'inscription.";
        toast.error(errorMsg);
        throw new Error(errorMsg);
      }

      // 4. Succès de l'inscription
      setRegisteredEmail(email);
      setIsRegistered(true);
      toast.success(data.message || "Compte créé ! En attente d'approbation.");

    } catch (error) {
      console.error('Register error:', error);
    } finally {
      setLoading(false);
    }
  }

  // --- AFFICHAGE DE L'ÉCRAN DE SUCCÈS APRÈS INSCRIPTION ---
  if (isRegistered) {
    return (
      <div className="flex min-h-screen w-full bg-gray-100">
        <WorkflowColumn />
        <section className="flex flex-1 items-center justify-center p-8">
          <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl p-8 text-center">
            <div className="text-6xl mb-4">✅</div>
            <h2 className="text-2xl font-bold mb-2">Inscription terminée !</h2>
            <p className="text-gray-600 mb-4">
              Un email de confirmation a été envoyé à <strong>{registeredEmail}</strong>.<br />
              Votre compte est en attente d'approbation par l'administrateur.
            </p>
            <Link
              href="/auth/login"
              className="inline-block w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Retour à la connexion
            </Link>
          </div>
        </section>
      </div>
    );
  }

  // --- FORMULAIRE D'INSCRIPTION ---
  return (
    <div className="flex min-h-screen w-full bg-gray-100">
      <WorkflowColumn />
      <section className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-md rounded-2xl bg-white shadow-2xl p-8">
          <div className="text-center mb-8">
            <div className="text-5xl mb-3">⛽</div>
            <h2 className="text-3xl font-bold">Créer un compte</h2>
            <p className="text-gray-500 mt-2">Rejoignez la plateforme GNL Knowledge Graph</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block mb-2 font-medium">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@gnl.com"
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-green-500 outline-none"
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
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-green-500 outline-none"
              />
            </div>
            <div>
              <label className="block mb-2 font-medium">Confirmation du mot de passe</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="********"
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-green-500 outline-none"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-green-600 py-3 text-white hover:bg-green-700 disabled:opacity-60 flex justify-center items-center gap-2"
            >
              {loading && <LoadingSpinner size="small" color="white" />}
              {loading ? "Création..." : "S'inscrire"}
            </button>
          </form>

          <div className="mt-8 text-center">
            <span className="text-gray-500">Déjà un compte ?</span>
            <Link href="/auth/login" className="ml-2 text-green-600 font-semibold hover:underline">
              Se connecter
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
