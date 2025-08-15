import tkinter as tk
from tkinter import filedialog, messagebox
import pandas
import math
from modele import valeurs_acceptables, convertir_donnees, ArbreBinaire, RandomForest

# Variables globales
donnees = []
valeurs_valides = []
parametres = []
modele = None  # Pour stocker le modèle (CART ou Random Forest)
algo_choisi = None  # Type d'algorithme choisi

def charger_csv():
    """Charge un fichier CSV et initialise les paramètres globaux."""
    global donnees, valeurs_valides, parametres

    chemin = filedialog.askopenfilename(filetypes=[("Fichiers CSV", "*.csv")])
    if not chemin:
        messagebox.showwarning("Avertissement", "Aucun fichier sélectionné.")
        return

    try:
        donnees_brutes = pandas.read_csv(chemin).values.tolist()
        parametres = pandas.read_csv(chemin).columns.tolist()
        del parametres[-1]
        valeurs_valides = valeurs_acceptables(donnees_brutes)
        donnees = convertir_donnees(donnees_brutes, valeurs_valides)
        messagebox.showinfo("Succès", "Fichier CSV chargé avec succès.")
    except Exception as e:
        messagebox.showerror("Erreur", "Erreur lors du chargement : " + str(e))

def valider_algo():
    """Valide l'algorithme choisi, entraîne le modèle et affiche la précision."""
    global modele, algo_choisi

    if algo_choisi.get() == "CART":
        modele = ArbreBinaire()
        modele.entrainer(donnees, profondeur_max=5, t_min=5)
    elif algo_choisi.get() == "Random Forest":
        modele = RandomForest(nb_arbres=10, profondeur_max=5, t_min=5, nb_caracteristiques=round(math.sqrt(len(parametres))))
        modele.entrainer(donnees)
    else:
        messagebox.showwarning("Avertissement", "Veuillez sélectionner un algorithme.")
        return
    # Calculer et afficher la précision
    precision.config(text=calculer_precision())  # Met à jour le label pour afficher la précision
    afficher_formulaire()


def calculer_precision():
    """Calcule et affiche la précision du modèle."""
    global donnees, modele
    cpt = 0
    if algo_choisi.get() == "CART":
        for l in donnees:
            prediction = modele.predire_ligne(l[:-1]) 
            if prediction != l[-1]: 
                cpt += 1
    else :
        for l in donnees:
            prediction = modele.predire(l)
            if prediction!=l[-1] :
                cpt+=1
    return "Précision : "+str((1-cpt/len(donnees))*100)+ "%"


def afficher_formulaire():
    """Affiche le formulaire pour entrer les valeurs."""
    for widget in form_frame.winfo_children():
        widget.destroy()

    global entries
    entries = {}
    i=0
    for param in parametres:
        label = tk.Label(form_frame, text=param+ " :")
        label.grid(row=i, column=0, padx=5, pady=5)
        entry = tk.Entry(form_frame, width=30)
        entry.grid(row=i, column=1, padx=5, pady=5)
        entries[param] = entry
        i+=1

    btn_predict = tk.Button(form_frame, text="Prédire", command=valider_et_predire)
    btn_predict.grid(row=len(parametres), columnspan=2, pady=10)

def valider_et_predire():
    """Vérifie les valeurs entrées et effectue une prédiction."""
    ligne = []
    erreurs = False
    erreurs_details = []  # Liste pour stocker les erreurs détaillées
    i=0
    for (param, entry) in entries.items():
        valeur = entry.get()
        try:
            # Vérification des valeurs numériques
            if type(valeurs_valides[i]) == tuple:  # Plage numérique
                valeur = float(valeur)
                if not (valeurs_valides[i][0] <= valeur <= valeurs_valides[i][1]):
                    raise ValueError(param+" doit être entre "+ str(valeurs_valides[i][0])+ " et "+ str(valeurs_valides[i][1]))
            else:  # Vérification des valeurs 
                if valeur not in valeurs_valides[i]:
                    erreur=str(param)+ " doit être l'une des valeurs : "
                    for val in valeurs_valides[i]:
                        erreur+=str(val)+', '
                    erreur=erreur[:-2]
                    raise ValueError(erreur)
            
            # Si la valeur est valide, ajouter à la ligne
            ligne.append(valeur)
            entry.config(bg="white")  # Remettre la couleur normale si le champ est corrigé

        except ValueError as e:
            entry.config(bg="red")  # Mettre en rouge le champ incorrect
            erreurs = True
            erreurs_details.append(str(e))  # Ajouter le message d'erreur détaillé
        i+=1
    
    if erreurs:
        txt="Certaines valeurs sont incorrectes :\n \n"
        for erreur in erreurs_details:
            txt+= "- "+erreur+"\n"
        messagebox.showerror("Erreur", txt)
        return

    # Convertir les valeurs catégoriques en indices numériques
    ligne_convertie = []
    i=0
    for valeur in ligne:
        if type(valeurs_valides[i]) == tuple:
            ligne_convertie.append(valeur)
        else:
            ligne_convertie.append(valeurs_valides[i].index(valeur))
        i+=1

    # Prédiction
    if algo_choisi.get() == "CART":
        prediction = modele.predire_ligne(ligne_convertie)  # Utilisation de predire_ligne
    else:
        prediction = modele.predire(ligne_convertie)  # RandomForest n'a pas besoin de modification

    messagebox.showinfo("Résultat","Prédiction : " +prediction)


# Interface Tkinter
root = tk.Tk()
root.title("SAE classification")

# Cadre pour le choix de l'algorithme
frame_top = tk.Frame(root, padx=10, pady=10)
frame_top.pack(fill="x")

algo_choisi = tk.StringVar()
tk.Label(frame_top, text="Choisir un algorithme :").grid(row=0, column=0, padx=5, pady=5)
tk.Radiobutton(frame_top, text="CART", variable=algo_choisi, value="CART").grid(row=0, column=1, padx=5, pady=5)
tk.Radiobutton(frame_top, text="Random Forest", variable=algo_choisi, value="Random Forest").grid(row=0, column=2, padx=5, pady=5)

chargement = tk.Button(frame_top, text="Charger un fichier CSV", command=charger_csv)
chargement.grid(row=1, column=0, padx=5, columnspan=3, pady=10)

valider = tk.Button(frame_top, text="Continuer", command=valider_algo)
valider.grid(row=2, column=0, columnspan=3, pady=10)

precision = tk.Label(frame_top, text="")
precision.grid(row=3, column=0, columnspan=3, pady=10)

# Cadre pour le formulaire
form_frame = tk.Frame(root, padx=10, pady=10)
form_frame.pack(fill="both", expand=True)

root.mainloop()
