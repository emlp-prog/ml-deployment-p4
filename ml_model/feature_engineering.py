import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class AttritionFeatureEngineer(BaseEstimator, TransformerMixin):

    def __init__(self):
        self.nominal_cols = ["statut_marital", "departement", "poste", "domaine_etude"]
        self.drop_early = [
            "nombre_heures_travailless",
            "nombre_employee_sous_responsabilite",
            "ayant_enfants",
        ]
        self.drop_final = ["id_employee", "niveau_hierarchique_poste"]
        self.feature_names_ = None

    def fit(self, X, y=None):
        Xt = self._transform(X)
        self.feature_names_ = Xt.columns.tolist()
        return self

    def transform(self, X):
        Xt = self._transform(X)

        if self.feature_names_ is not None:
            Xt = Xt.reindex(columns=self.feature_names_, fill_value=0)

        return Xt

    def _transform(self, X):

        X = X.copy()

        X = X.drop(columns=[c for c in self.drop_early if c in X.columns], errors="ignore")

        if "augementation_salaire_precedente" in X.columns:
            X["augementation_salaire_precedente"] = (
                X["augementation_salaire_precedente"]
                .astype(str)
                .str.replace(" %", "", regex=False)
                .astype(float)
            )

        if "genre" in X.columns:
            X["is_male"] = (X["genre"] == "M").astype(int)
            X = X.drop(columns=["genre"])

        if "heure_supplementaires" in X.columns:
            X["heure_supplementaires"] = (X["heure_supplementaires"] == "Oui").astype(int)

        if "frequence_deplacement" in X.columns:
            mapping = {"Aucun": 0, "Occasionnel": 1, "Frequent": 2}
            X["frequence_deplacement"] = X["frequence_deplacement"].map(mapping)

        if {"annees_dans_le_poste_actuel", "annees_dans_l_entreprise"}.issubset(X.columns):
            X["stagnation_poste"] = (
                X["annees_dans_le_poste_actuel"] /
                (X["annees_dans_l_entreprise"] + 1)
            )

        if {"annees_depuis_la_derniere_promotion", "annees_dans_l_entreprise"}.issubset(X.columns):
            X["stagnation_promotion"] = (
                X["annees_depuis_la_derniere_promotion"] /
                (X["annees_dans_l_entreprise"] + 1)
            )

        if {"nb_formations_suivies", "annees_dans_l_entreprise"}.issubset(X.columns):
            X["taux_formation"] = (
                X["nb_formations_suivies"] /
                (X["annees_dans_l_entreprise"] + 1)
            )

        if {"annees_dans_l_entreprise", "niveau_hierarchique_poste"}.issubset(X.columns):
            X["anciennete_x_niveau"] = (
                X["annees_dans_l_entreprise"] *
                X["niveau_hierarchique_poste"]
            )

        if {
            "revenu_mensuel",
            "annee_experience_totale",
            "annees_dans_l_entreprise",
        }.issubset(X.columns):

            X["salaire_par_experience"] = (
                X["revenu_mensuel"] /
                (X["annee_experience_totale"] + 1)
            )

            X["proportion_experience_entreprise"] = (
                X["annees_dans_l_entreprise"] /
                (X["annee_experience_totale"] + 1)
            )

        if {
            "note_evaluation_actuelle",
            "note_evaluation_precedente",
        }.issubset(X.columns):

            X["evolution_evaluation"] = (
                X["note_evaluation_actuelle"] -
                X["note_evaluation_precedente"]
            )

        sat_cols = [
            "satisfaction_employee_nature_travail",
            "satisfaction_employee_equipe",
            "satisfaction_employee_equilibre_pro_perso",
            "satisfaction_employee_environnement",
        ]

        if all(col in X.columns for col in sat_cols):
            X["satisfaction_moyenne"] = X[sat_cols].mean(axis=1)

        nominal_present = [c for c in self.nominal_cols if c in X.columns]

        X = pd.get_dummies(
            X,
            columns=nominal_present,
            drop_first=True
        )

        X = X.drop(
            columns=[c for c in self.drop_final if c in X.columns],
            errors="ignore"
        )

        return X