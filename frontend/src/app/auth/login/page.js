'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import Cookies from 'js-cookie'; // <-- NOUVEAU : Import pour gérer les cookies
import { useApi } from '@/hooks/useApi';
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
      desc: 'Optimisez vos routes grâce à l’IA.',
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

        <h1 className="text-4xl font-bold mb-3">
          GNL Knowledge Graph
        </h1>

        <p className="text-blue-200">
          Plateforme intelligente pour le transport du Gaz Naturel Liquéfié.
        </p>
      </div>

      <div className="space-y-5">
        {workflows.map((item) => (
          <div
            key={item.title}
            className="rounded-xl bg-white/10 p-5 border border-white/10"
          >
            <div className="flex gap-4">

              <div className="text-3xl">
                {item.icon}
              </div>

              <div>

                <h3 className="font-semibold text-lg">
                  {item.title}
                </h3>

                <p className="text-blue-200 text-sm mt-1">
                  {item.desc}
                </p>

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
  const { post } = useApi();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();

    setLoading(true);

    try {

      const response = await post('/api/auth/login', {
        email,
        password,
      });

      // --- STOCKAGE DU TOKEN ET DU RÔLE ---
      // 1. Stockage local pour le Frontend
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('role', response.role);

      // 2. Stockage dans les cookies pour le Middleware (7 jours)
      Cookies.set('token', response.access_token, { expires: 7 });
      Cookies.set('role', response.role, { expires: 7 });
      // ---------------------------------------

      toast.success('Connexion réussie');

      router.push('/');

    } catch {

      toast.error('Email ou mot de passe incorrect');

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

            <div className="text-5xl mb-3">
              ⛽
            </div>

            <h2 className="text-3xl font-bold">
              Se connecter
            </h2>

            <p className="text-gray-500 mt-2">
              Accédez à votre plateforme GNL
            </p>

          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            <div>

              <label className="block mb-2 font-medium">
                Email
              </label>

              <input
                type="email"
                required
                value={email}
                onChange={(e)=>setEmail(e.target.value)}
                placeholder="admin@gnl.com"
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
              />

            </div>

            <div>

              <label className="block mb-2 font-medium">
                Mot de passe
              </label>

              <input
                type="password"
                required
                value={password}
                onChange={(e)=>setPassword(e.target.value)}
                placeholder="********"
                className="w-full rounded-lg border px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
              />

            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-blue-600 py-3 text-white hover:bg-blue-700 disabled:opacity-60 flex justify-center items-center gap-2"
            >

              {loading && (
                <LoadingSpinner
                  size="small"
                  color="white"
                />
              )}

              {loading ? 'Connexion...' : 'Se connecter'}

            </button>

          </form>

          <div className="mt-8 text-center">

            <span className="text-gray-500">
              Pas encore inscrit ?
            </span>

            <Link
              href="/auth/register"
              className="ml-2 text-blue-600 font-semibold hover:underline"
            >
              Créer un compte
            </Link>

          </div>

        </div>

      </section>

    </div>

  );
}