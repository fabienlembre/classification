import pandas
import random
import math

#Transformer str en float
def convertir_donnees(donnees, valeurs_acceptables):
    nouvelles_donnees = []
    for ligne in donnees:
        nouvelle_ligne = []
        for col in range(len(ligne)-1):
            try:
                nouvelle_ligne.append(float(ligne[col]))
            except ValueError:
                # Si la conversion échoue, on la transforme en numérique selon sa position dans valeurs_acceptables
                nouvelle_ligne.append(valeurs_acceptables[col].index(ligne[col]))
        nouvelle_ligne.append(ligne[-1])
        nouvelles_donnees.append(nouvelle_ligne)
    return nouvelles_donnees

#Retourne un tableau de tuple représentant les intervalles de valeurs acceptables pour chaque catégorie sans prendre le résultat en dernière colonne
def min_max(donnees, col):
  min=float('+inf')
  max=float('-inf')
  for l in donnees:
    if(l[col]>max):
      max=l[col]
    if(l[col]<min):
      min=l[col]
  return (min,max)

def valeurs_acceptables(donnees):
  l=[]
  for col in range(len(donnees[0])-1):
    try:
      float(donnees[0][col])
      l.append(min_max(donnees,col))
    except ValueError:
      sl=[]
      for lig in range(len(donnees)):
        if(donnees[lig][col] not in sl):
          sl.append(donnees[lig][col])
      l.append(sl)
  return l
  

class Noeud:
    """Classe représentant un nœud """
    def __init__(self, indice=None, valeur=None, gauche=None, droite=None, terminal=None):
        self.indice = indice  # Indice de la caractéristique pour la division
        self.valeur = valeur  # Valeur seuil pour la division
        self.gauche = gauche  # Sous-arbre gauche
        self.droite = droite  # Sous-arbre droit
        self.terminal = terminal  # Valeur du nœud terminal (si c'est une feuille)

    def est_terminal(self):
        return self.terminal is not None
    
#--------------------------------------------------------------------- CART ----------------------------------------------------------------------------- #


class ArbreBinaire:
    """Classe pour représenter un arbre binaire en utilisant l'algorithme CART."""
    def __init__(self):
        self.__racine = None

    def indice_gini(self, groupes):
        """Calcule l'indice de Gini pour chaque groupe."""
        total_exemples = 0
        for groupe in groupes:
            total_exemples+= len(groupe)
        gini = 0
        for groupe in groupes:
            if len(groupe) != 0:
                # Calcul des occurrences pour chaque classe
                classes = {}
                for ligne in groupe:
                    classe = ligne[-1]
                    if classe not in classes:
                        classes[classe] = 0
                    classes[classe] += 1
                # Calcul des proportions et du Gini pour ce groupe
                proportion_groupe = 0
                for classe, compteur in classes.items():
                    proportion = compteur / len(groupe)
                    proportion_groupe += proportion**2
                gini += (1 - proportion_groupe) * (len(groupe) / total_exemples)
        return gini

    def diviser_donnees(self, indice, valeur, donnees):
        """Divise les données en deux groupes selon une caractéristique et une valeur seuil."""
        gauche = []
        droite = []
        for ligne in donnees:
            if ligne[indice] < valeur:
                gauche.append(ligne)
            else:
                droite.append(ligne)
        return gauche, droite

    def trouver_meilleure_division(self, donnees):
        """Trouve la meilleure division des données en fonction de l'indice de Gini."""
        meilleur_score = float('inf')
        meilleure_division = None
        for indice in range(len(donnees[0]) - 1):  # Exclure la colonne des classes
            for valeur in set(ligne[indice] for ligne in donnees):
                groupes = self.diviser_donnees(indice, valeur, donnees)
                score = self.indice_gini(groupes)
                if score < meilleur_score:
                    meilleur_score = score
                    meilleure_division = {"indice": indice, "valeur": valeur, "groupes": groupes}
        return meilleure_division

    def construire(self, division, profondeur_max, t_min, profondeur):
        """Construit récursivement les nœuds de l'arbre."""
        gauche, droite = division["groupes"]
        
        # Si un des groupes est vide ou si la profondeur maximale est atteinte
        if not gauche or not droite or profondeur >= profondeur_max:
            # Calcul de la classe majoritaire directement
            classes = [ligne[-1] for ligne in gauche + droite]
            frequence = {}
            for classe in classes:
                # Vérifie si la classe existe déjà dans le dictionnaire
                if classe in frequence:
                    frequence[classe] += 1
                else:
                    frequence[classe] = 1
            classe_majoritaire = None
            frequence_max = -1
            for classe, freq in frequence.items():
                if freq > frequence_max:
                    frequence_max = freq
                    classe_majoritaire = classe
            return Noeud(terminal=classe_majoritaire)
        
        # Construire le sous-arbre gauche
        if len(gauche) <= t_min:
            # Créer un nœud terminal avec la classe majoritaire pour le groupe gauche
            classes_gauche = [ligne[-1] for ligne in gauche]
            frequence_gauche = {}
            for classe in classes_gauche:
                if classe in frequence_gauche:
                    frequence_gauche[classe] += 1
                else:
                    frequence_gauche[classe] = 1
            classe_majoritaire_gauche = None
            frequence_max_gauche = -1
            for classe, freq in frequence_gauche.items():
                if freq > frequence_max_gauche:
                    frequence_max_gauche = freq
                    classe_majoritaire_gauche = classe
            noeud_gauche = Noeud(terminal=classe_majoritaire_gauche)
        else:
            division_gauche = self.trouver_meilleure_division(gauche)
            noeud_gauche = self.construire(division_gauche, profondeur_max, t_min, profondeur + 1)
        
        # Construire le sous-arbre droit
        if len(droite) <= t_min:
            # Créer un nœud terminal avec la classe majoritaire pour le groupe droit
            classes_droite = [ligne[-1] for ligne in droite]
            frequence_droite = {}
            for classe in classes_droite:
                if classe in frequence_droite:
                    frequence_droite[classe] += 1
                else:
                    frequence_droite[classe] = 1
            classe_majoritaire_droite = None
            frequence_max_droite = -1
            for classe, freq in frequence_droite.items():
                if freq > frequence_max_droite:
                    frequence_max_droite = freq
                    classe_majoritaire_droite = classe
            noeud_droite = Noeud(terminal=classe_majoritaire_droite)
        else:
            division_droite = self.trouver_meilleure_division(droite)
            noeud_droite = self.construire(division_droite, profondeur_max, t_min, profondeur + 1)
        
        return Noeud(indice=division["indice"], valeur=division["valeur"], gauche=noeud_gauche, droite=noeud_droite)

    def entrainer(self, donnees, profondeur_max, t_min):
        """Construit l'arbre à partir des données d'entraînement."""
        division_initiale = self.trouver_meilleure_division(donnees)
        self.__racine = self.construire(division_initiale, profondeur_max, t_min, profondeur=1)

    def predire(self, noeud, ligne):
        """Prédit la classe pour une ligne donnée."""
        if noeud.est_terminal():
            return noeud.terminal
        if ligne[noeud.indice] < noeud.valeur:
            if noeud.gauche is not None:
                return self.predire(noeud.gauche, ligne)
        else:
            if noeud.droite is not None:
                return self.predire(noeud.droite, ligne)

    def predire_ligne(self, ligne):
        """Prédit la classe pour une ligne donnée (point d'entrée)."""
        return self.predire(self.__racine, ligne)


# Exemple d'utilisation
def cart(fichier):    
    # Créer et entraîner l'arbre
    arbre = ArbreBinaire()
    arbre.entrainer(donnees, profondeur_max=5, t_min=10)
    
    # Prédire avec de nouvelles données
    cpt=0
    for l in donnees:
        prediction = arbre.predire_ligne(l)
        
        if prediction!=l[-1] :
            cpt+=1
        print("Prediction : "+str(prediction)+", Reel : "+ str(l[-1]))
    print("fautes = ", str(cpt),"/",str(len(donnees)))
    print("precision = ",str((1-cpt/len(donnees))*100), "%")
    print("Prediction : "+str(arbre.predire_ligne([5,2.5,6.5,1])))

# ------------------------------------------------------ Random Forest ---------------------------------------------------------

import random

class RandomForest:
    """Classe pour représenter une forêt aléatoire."""
    def __init__(self, nb_arbres, profondeur_max, t_min, nb_caracteristiques):
        self.__nb_arbres = nb_arbres
        self.__profondeur_max = profondeur_max
        self.__t_min = t_min
        self.__nb_caracteristiques = nb_caracteristiques
        self.__arbres = []

    def indice_gini(self, groupes):
        """Calcule l'indice de Gini pour chaque groupe."""
        total_exemples = 0
        for groupe in groupes:
            total_exemples += len(groupe)
        gini = 0
        for groupe in groupes:
            if len(groupe) != 0:
                # Calcul des occurrences pour chaque classe
                classes = {}
                for ligne in groupe:
                    classe = ligne[-1]
                    if classe not in classes:
                        classes[classe] = 0
                    classes[classe] += 1
                # Calcul des proportions et du Gini pour ce groupe
                proportion_groupe = 0
                for classe, compteur in classes.items():
                    proportion = compteur / len(groupe)
                    proportion_groupe += proportion ** 2
                gini += (1 - proportion_groupe) * (len(groupe) / total_exemples)
        return gini

    def diviser_donnees(self, indice, valeur, donnees):
        """Divise les données en deux groupes selon une caractéristique et une valeur seuil."""
        gauche = []
        droite = []
        for ligne in donnees:
            if ligne[indice] < valeur:
                gauche.append(ligne)
            else:
                droite.append(ligne)
        return gauche, droite

    def trouver_meilleure_division(self, donnees, indices_caracteristiques):
        """Trouve la meilleure division en utilisant un sous-ensemble de caractéristiques."""
        meilleur_score = float('inf')
        meilleure_division = None
        for indice in indices_caracteristiques:
            for valeur in set(ligne[indice] for ligne in donnees):
                groupes = self.diviser_donnees(indice, valeur, donnees)
                score = self.indice_gini(groupes)
                if score < meilleur_score:
                    meilleur_score = score
                    meilleure_division = {"indice": indice, "valeur": valeur, "groupes": groupes}
        return meilleure_division

    def construire_arbre(self, donnees, profondeur):
        """Construit l'arbre récursivement"""
        indices_caracteristiques = random.sample(range(len(donnees[0]) - 1), self.__nb_caracteristiques)
        division = self.trouver_meilleure_division(donnees, indices_caracteristiques)

        # Si on atteint les critères d'arrêt
        if not division or profondeur >= self.__profondeur_max or len(donnees) <= self.__t_min:
            # Calcul de la classe majoritaire (nœud terminal)
            classes = [ligne[-1] for ligne in donnees]
            frequence = {}
            for classe in classes:
                if classe in frequence:
                    frequence[classe] += 1
                else:
                    frequence[classe] = 1
            classe_majoritaire = None
            frequence_max = -1
            for classe, freq in frequence.items():
                if freq > frequence_max:
                    frequence_max = freq
                    classe_majoritaire = classe
            return Noeud(terminal=classe_majoritaire)

        gauche, droite = division["groupes"]
        # Si un des groupes est vide, créer un nœud terminal
        if not gauche or not droite:
            # Calcul de la classe majoritaire (nœud terminal)
            classes = [ligne[-1] for ligne in gauche + droite]
            frequence = {}
            for classe in classes:
                if classe in frequence:
                    frequence[classe] += 1
                else:
                    frequence[classe] = 1
            classe_majoritaire = None
            frequence_max = -1
            for classe, freq in frequence.items():
                if freq > frequence_max:
                    frequence_max = freq
                    classe_majoritaire = classe
            return Noeud(terminal=classe_majoritaire)

        # Créer le nœud courant avec des sous-arbres
        noeud_g = self.construire_arbre(gauche, profondeur + 1)
        noeud_d = self.construire_arbre(droite, profondeur + 1)
        return Noeud(indice=division["indice"], valeur=division["valeur"], gauche=noeud_g, droite=noeud_d)

    def creer_echantillon(self, donnees):
        """Crée un échantillon (tirage avec remplacement)"""
        return [random.choice(donnees) for _ in range(len(donnees))]

    def entrainer(self, donnees):
        """Construit plusieurs arbres et les stocke dans la forêt."""
        self.__arbres = []
        for _ in range(self.__nb_arbres):
            echantillon = self.creer_echantillon(donnees)
            arbre = self.construire_arbre(echantillon, profondeur=0)
            self.__arbres.append(arbre)

    def predire_arbre(self, noeud, ligne):
        """Fait une prédiction avec un arbre (récursivement)."""
        if noeud.est_terminal():
            return noeud.terminal
        if ligne[noeud.indice] < noeud.valeur:
            return self.predire_arbre(noeud.gauche, ligne)
        else:
            return self.predire_arbre(noeud.droite, ligne)

    def predire(self, ligne):
        """Retourne la prédiction de la majorité des arbres"""
        predictions = [self.predire_arbre(arbre, ligne) for arbre in self.__arbres]
        # Calculer la fréquence des prédictions
        frequence = {}
        for prediction in predictions:
            if prediction in frequence:
                frequence[prediction] += 1
            else:
                frequence[prediction] = 1
        # Trouver la classe avec la fréquence maximale
        classe_majoritaire = None
        frequence_max = -1
        for prediction, freq in frequence.items():
            if freq > frequence_max:
                frequence_max = freq
                classe_majoritaire = prediction
        return classe_majoritaire


def random_forest(donnees, parametres):
    # Créer et entraîner l'arbre
    foret = RandomForest(nb_arbres=5, profondeur_max=4, t_min=5, nb_caracteristiques=round(math.sqrt(len(parametres))))
    foret.entrainer(donnees)
    
    # Prédire avec de nouvelles données
    cpt=0
    for l in donnees:
        prediction = foret.predire(l)
        
        if prediction!=l[-1] :
            cpt+=1
        print("Prediction : "+str(prediction)+", Reel : "+ str(l[-1]))
    print("fautes = ", str(cpt),"/",str(len(donnees)))
    print("precision = ",str((1-cpt/len(donnees))*100), "%")
    print("Prediction : "+str(foret.predire([5,2.5,6.5,1])))


#--------------------------------------------------------------------- TESTS ----------------------------------------------------------------------------- #

 
if __name__ == "__main__":
    donnees = pandas.read_csv('iris.csv').values.tolist()
    parametres= pandas.read_csv('iris.csv').columns.tolist()
    del(parametres[-1])
    valeurs_valides = valeurs_acceptables(donnees)
    donnees = convertir_donnees(donnees, valeurs_valides)
    print(valeurs_valides)
    print("------------------------  Algorithme Cart ------------------------------- \n")
    cart(donnees) #toujours le même résultat
    print("\n ------------------------ Algorithme Random Forest ------------------------------- \n")
    random_forest(donnees, parametres) #pas toujours le même résultat