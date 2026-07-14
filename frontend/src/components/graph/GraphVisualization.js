/**
 * GraphVisualization - Visualisation du graphe (Version ultra-robuste)
 */

'use client';

import { useEffect, useRef, useState } from 'react';

export function GraphVisualization({ onNodeClick, selectedNode }) {
  const containerRef = useRef(null);
  const [status, setStatus] = useState('Chargement...');
  const [error, setError] = useState(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    let cyInstance = null;
    let destroyTimeout = null;

    const initGraph = async () => {
      try {
        // Vérifier que le conteneur existe et est visible
        if (!containerRef.current) {
          throw new Error('Conteneur non trouvé');
        }

        // Vérifier que le conteneur a une taille
        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) {
          // Attendre que le conteneur soit visible
          await new Promise(resolve => setTimeout(resolve, 100));
        }

        setStatus('Importation de Cytoscape...');

        // Importer Cytoscape
        const cytoscapeModule = await import('cytoscape');
        const cytoscape = cytoscapeModule.default || cytoscapeModule;

        if (!mountedRef.current) return;
        setStatus('Création du graphe...');

        // Données du graphe
        const elements = {
          nodes: [
            { data: { id: 'FOUR-001', label: 'Total Energies' }, classes: 'Fournisseur' },
            { data: { id: 'TERM-001', label: 'Fos-sur-Mer' }, classes: 'Terminal' },
            { data: { id: 'METH-001', label: 'GNL Explorer' }, classes: 'Méthanier' },
            { data: { id: 'PIPE-001', label: 'Nord-Sud' }, classes: 'Pipeline' },
            { data: { id: 'CLIENT-001', label: 'EDF' }, classes: 'Client' },
            { data: { id: 'STOCK-001', label: 'Stockage Souterrain' }, classes: 'Stockage' },
            { data: { id: 'COMP-001', label: 'Compresseur Nord' }, classes: 'Compresseur' },
            { data: { id: 'INC-001', label: 'INC-001' }, classes: 'Incident' },
          ],
          edges: [
            { data: { id: 'e1', source: 'FOUR-001', target: 'TERM-001', label: 'FOURNIT' } },
            { data: { id: 'e2', source: 'METH-001', target: 'TERM-001', label: 'LIVRE_A' } },
            { data: { id: 'e3', source: 'TERM-001', target: 'PIPE-001', label: 'ALIMENTE' } },
            { data: { id: 'e4', source: 'PIPE-001', target: 'CLIENT-001', label: 'DESSERT' } },
            { data: { id: 'e5', source: 'TERM-001', target: 'STOCK-001', label: 'STOCKE' } },
            { data: { id: 'e6', source: 'PIPE-001', target: 'COMP-001', label: 'DEPEND_DE' } },
            { data: { id: 'e7', source: 'INC-001', target: 'PIPE-001', label: 'AFFECTE' } },
          ]
        };

        // Créer l'instance avec un layout simple et immédiat
        cyInstance = cytoscape({
          container: containerRef.current,
          elements: elements,
          style: [
            {
              selector: 'node',
              style: {
                'background-color': (ele) => {
                  const colors = {
                    Fournisseur: '#3B82F6',
                    Terminal: '#10B981',
                    Méthanier: '#8B5CF6',
                    Pipeline: '#F59E0B',
                    Client: '#EF4444',
                    Stockage: '#6366F1',
                    Compresseur: '#EC4899',
                    Incident: '#DC2626',
                  };
                  return colors[ele.classes()[0]] || '#6B7280';
                },
                // --- DÉBUT DES MODIFICATIONS DE TEXTE ---
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#ffffff',
                'font-size': '9px',            // Taille réduite (était à 11px)
                'font-weight': 'bold',
                'text-wrap': 'wrap',           // Permet de passer à la ligne si le texte est long
                'text-max-width': '50px',      // Évite que le texte ne sorte du cadre
                // --- FIN DES MODIFICATIONS ---
                'width': '55px',
                'height': '55px',
                'shape': 'roundrectangle',
                'border-width': 2,
                'border-color': 'rgba(0,0,0,0.2)',
              }
            },
            {
              selector: 'node.Incident',
              style: {
                'shape': 'diamond',
                'width': '40px',
                'height': '40px',
                // Pour les incidents, on garde la même logique de texte mais adaptée à un losange
                'text-max-width': '35px',     
              }
            },
            {
              selector: 'edge',
              style: {
                'width': 2,
                'line-color': '#9CA3AF',
                'target-arrow-color': '#9CA3AF',
                'target-arrow-shape': 'triangle',
                'label': 'data(label)',
                'font-size': '8px',
                'text-rotation': 'autorotate',
                'color': '#6B7280',
                'curve-style': 'bezier',
              }
            }
          ],
          layout: {
            name: 'grid',  // Layout simple et rapide
            animate: false,
            padding: 30,
            rows: 3,
            cols: 3,
          },
        });

        if (!mountedRef.current) {
          if (cyInstance) cyInstance.destroy();
          return;
        }

        // Attendre que le layout soit terminé
        cyInstance.on('layoutstop', () => {
          if (!mountedRef.current || !cyInstance) return;
          try {
            cyInstance.resize();
            cyInstance.fit();
            cyInstance.center();
            console.log('✅ Graphe centré');
            if (mountedRef.current) {
              setStatus('Graphe affiché !');
            }
          } catch (e) {
            console.warn('⚠️ Erreur de centrage:', e.message);
          }
        });

        // Forcer un redimensionnement après un délai
        setTimeout(() => {
          if (mountedRef.current && cyInstance) {
            try {
              cyInstance.resize();
              cyInstance.fit();
              cyInstance.center();
              console.log('✅ Graphe redimensionné');
            } catch (e) {
              console.warn('⚠️ Erreur:', e.message);
            }
          }
        }, 300);

        // Événements
        cyInstance.on('click', 'node', (evt) => {
          const node = evt.target;
          if (onNodeClick) {
            onNodeClick({
              id: node.data('id'),
              label: node.data('label'),
              classes: node.classes(),
            });
          }
        });

        cyInstance.on('mouseover', 'node', (evt) => {
          evt.target.style('border-color', '#FFD700');
          evt.target.style('border-width', 3);
        });

        cyInstance.on('mouseout', 'node', (evt) => {
          evt.target.style('border-color', 'rgba(0,0,0,0.2)');
          evt.target.style('border-width', 2);
        });

        // Si le layout ne se déclenche pas, forcer
        setTimeout(() => {
          if (mountedRef.current && cyInstance && status === 'Création du graphe...') {
            try {
              cyInstance.layout({ name: 'grid', animate: false }).run();
            } catch (e) {
              console.warn('⚠️ Layout forcé:', e.message);
            }
          }
        }, 100);

      } catch (err) {
        console.error('❌ ERREUR:', err);
        if (mountedRef.current) {
          setError(err.message);
          setStatus('Erreur');
        }
      }
    };

    // Attendre que le DOM soit prêt
    const timer = setTimeout(() => {
      initGraph();
    }, 200);

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
      if (destroyTimeout) clearTimeout(destroyTimeout);
      if (cyInstance) {
        try {
          cyInstance.destroy();
        } catch (e) {
          // Ignorer
        }
        cyInstance = null;
      }
    };
  }, []);

  // Effet pour les changements de sélection
  useEffect(() => {
    // Le graphe est déjà géré par l'effet principal
  }, [selectedNode]);

  if (error) {
    return (
      <div className="w-full h-full flex flex-col items-center justify-center bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
        <div className="text-4xl mb-2">❌</div>
        <p className="text-red-600 dark:text-red-400 font-medium">Erreur de chargement</p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
        >
          Réessayer
        </button>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      <div className="text-xs text-gray-500 p-1 bg-gray-100 dark:bg-gray-800 rounded-t-lg text-center">
        {status}
      </div>
      <div 
        ref={containerRef} 
        className="flex-1 bg-gray-50 dark:bg-gray-700/30 rounded-b-lg"
        style={{ minHeight: '350px', width: '100%', position: 'relative' }}
      />
    </div>
  );
}