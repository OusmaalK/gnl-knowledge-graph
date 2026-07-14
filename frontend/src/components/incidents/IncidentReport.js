/**
 * IncidentReport - Composant de génération de rapport PDF
 * ============================================================================
 * Description: Exporte les incidents au format PDF
 * ============================================================================
 */

import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

export const generateIncidentReport = (incidents, filters) => {
  if (!incidents || incidents.length === 0) {
    alert('Aucun incident à exporter.');
    return;
  }

  const doc = new jsPDF();
  
  // Titre
  doc.setFontSize(18);
  doc.text('Rapport des Incidents - GNL Knowledge Graph', 14, 22);
  
  // Date du rapport
  doc.setFontSize(10);
  doc.text(`Généré le : ${new Date().toLocaleString('fr-FR')}`, 14, 30);
  
  // Filtres
  doc.setFontSize(9);
  doc.text(`Filtres : ${filters.severity !== 'all' ? 'Gravité: '+filters.severity : 'Toutes gravités'} | ${filters.status !== 'all' ? 'Statut: '+filters.status : 'Tous statuts'}`, 14, 36);

  // Tableau des incidents
  const tableData = incidents.map(inc => [
    inc.id || 'N/A',
    inc.description || 'N/A',
    inc.gravite || 'N/A',
    inc.statut || 'N/A',
    inc.date ? new Date(inc.date).toLocaleDateString('fr-FR') : 'N/A',
    inc.equipment_name || 'N/A'
  ]);

  autoTable(doc, {
    startY: 42,
    head: [['ID', 'Description', 'Gravité', 'Statut', 'Date', 'Équipement']],
    body: tableData,
    theme: 'striped',
    headStyles: { fillColor: [41, 128, 185] },
    styles: { fontSize: 8 },
    columnStyles: {
      0: { cellWidth: 25 },
      1: { cellWidth: 60 },
      2: { cellWidth: 20 },
      3: { cellWidth: 20 },
      4: { cellWidth: 25 },
      5: { cellWidth: 30 }
    }
  });

  // Sauvegarder le PDF
  doc.save(`rapport-incidents-${new Date().toISOString().slice(0, 10)}.pdf`);
};