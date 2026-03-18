# Schema de la base de donnees

Le projet utilise une base PostgreSQL avec deux tables principales.

## Table `employees`

Cette table contient les donnees des employes utilisees pour faire la prediction.

Colonnes principales :
- `id_employee` : cle primaire
- `age`
- `genre`
- `revenu_mensuel`
- `statut_marital`
- `departement`
- `poste`
- `nombre_experiences_precedentes`
- `nombre_heures_travailless`
- `annee_experience_totale`
- `annees_dans_l_entreprise`
- `annees_dans_le_poste_actuel`
- `satisfaction_employee_environnement`
- `note_evaluation_precedente`
- `niveau_hierarchique_poste`
- `satisfaction_employee_nature_travail`
- `satisfaction_employee_equipe`
- `satisfaction_employee_equilibre_pro_perso`
- `note_evaluation_actuelle`
- `heure_supplementaires`
- `augementation_salaire_precedente`
- `a_quitte_l_entreprise`
- `nombre_participation_pee`
- `nb_formations_suivies`
- `nombre_employee_sous_responsabilite`
- `distance_domicile_travail`
- `niveau_education`
- `domaine_etude`
- `ayant_enfants`
- `frequence_deplacement`
- `annees_depuis_la_derniere_promotion`
- `annes_sous_responsable_actuel`

## Table `prediction_logs`

Cette table contient les logs des appels a l'API.

Colonnes :
- `id` : cle primaire
- `created_at` : date du log
- `employee_id` : identifiant de l'employe
- `endpoint` : `predict` ou `predict_proba`
- `input_payload` : JSON envoye
- `output_payload` : JSON retourne
- `model_version` : version du modele

## Relation entre les tables

- `prediction_logs.employee_id` pointe vers `employees.id_employee`

Donc :
- un employe peut avoir plusieurs logs de prediction
- un log appartient a un seul employe

## Contraintes importantes

- `id_employee` est unique
- `employee_id` dans `prediction_logs` est obligatoire
- la cle etrangere garantit la coherence entre les logs et les employes

## Utilisation dans le projet

1. l'API recoit un `employee_id`
2. elle lit l'employe dans `employees`
3. elle envoie les donnees au modele ML
4. elle sauvegarde la reponse dans `prediction_logs`
