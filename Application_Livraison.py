import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
import sys

# Classe abstraite Vehicule
class Vehicule(ABC):
    def __init__(self, marque, modele, immatriculation):
        self._marque = marque
        self._modele = modele
        self._immatriculation = immatriculation
    
    @abstractmethod
    def livrer(self, commande):
        pass
    
    def __str__(self):
        return f"{self._marque} {self._modele} ({self._immatriculation})"

# Classes dérivées
class Camion(Vehicule):
    def __init__(self, marque, modele, immatriculation, capacite):
        super().__init__(marque, modele, immatriculation)
        self.capacite_tonnes = capacite
    
    def livrer(self, commande):
        if commande.poids <= self.capacite_tonnes:
            commande.marquer_livree()
            return f"Camion livre {commande.id} ({commande.poids}t)"
        return f"Erreur: Capacité dépassée ({commande.poids}t > {self.capacite_tonnes}t)"

class Moto(Vehicule):
    def __init__(self, marque, modele, immatriculation, vitesse):
        super().__init__(marque, modele, immatriculation)
        self.vitesse_max = vitesse
    
    def livrer(self, commande):
        commande.marquer_livree()
        return f"Moto livre {commande.id} à {self.vitesse_max}km/h"

# Classe Commande
class Commande:
    def __init__(self, id, destination, poids):
        self.id = id
        self.destination = destination
        self.poids = poids
        self.statut = "en attente"
    
    def marquer_livree(self):
        self.statut = "livrée"
    
    @staticmethod
    def valider_poids(poids):
        return 0 < poids <= 100

# Classe Livreur
class Livreur:
    def __init__(self, nom, vehicule=None):
        self.nom = nom
        self.vehicule = vehicule
        self.commandes_en_cours = []
    
    def ajouter_commande(self, commande):
        if self.vehicule and Commande.valider_poids(commande.poids):
            self.commandes_en_cours.append(commande)
            return True
        return False
    
    def effectuer_livraison(self):
        resultats = []
        for commande in self.commandes_en_cours[:]:
            if self.vehicule:
                resultat = self.vehicule.livrer(commande)
                resultats.append(resultat)
                self.commandes_en_cours.remove(commande)
        return "\n".join(resultats) if resultats else "Aucune commande à livrer"
    
    @staticmethod
    def verifier_nom(nom):
        return nom.replace(' ', '').isalpha()
    
    @classmethod
    def depuis_dictionnaire(cls, data):
        return cls(data['nom'], data.get('vehicule'))
    
    def __str__(self):
        vehicule_info = str(self.vehicule) if self.vehicule else "Sans véhicule"
        commandes_info = f" ({len(self.commandes_en_cours)} commandes)" if self.commandes_en_cours else ""
        return f"{self.nom} - {vehicule_info}{commandes_info}"

# Classe Depot
class Depot:
    def __init__(self):
        self.vehicules_disponibles = []
        self.livreurs_disponibles = []
        self.commandes = []
    
    def ajouter_vehicule(self, vehicule):
        self.vehicules_disponibles.append(vehicule)
    
    def ajouter_livreur(self, livreur):
        self.livreurs_disponibles.append(livreur)
    
    def ajouter_commande(self, commande):
        self.commandes.append(commande)
    
    def attribuer_vehicule(self, livreur, vehicule):
        livreur.vehicule = vehicule
    
    def afficher_etat(self):
        etat = "=== État du dépôt ===\n"
        etat += "\nVéhicules disponibles:\n"
        etat += "\n".join(str(v) for v in self.vehicules_disponibles)
        etat += "\n\nLivreurs disponibles:\n"
        etat += "\n".join(str(l) for l in self.livreurs_disponibles)
        etat += "\n\nCommandes en attente:\n"
        etat += "\n".join(f"{c.id} - {c.destination} ({c.poids}kg)" for c in self.commandes if c.statut == "en attente")
        return etat

# Interface graphique
class Application(tk.Tk):
    def __init__(self, depot):
        super().__init__()
        self.depot = depot
        self.title("Gestion Livraisons")
        self.geometry("900x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
        self.update_listboxes()
    
    def on_close(self):
        self.destroy()
        sys.exit()
    
    def create_widgets(self):
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Listboxes avec scrollbars
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Véhicules
        ttk.Label(list_frame, text="Véhicules").grid(row=0, column=0, sticky="w")
        vehicule_frame = ttk.Frame(list_frame)
        vehicule_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.vehicules_listbox = tk.Listbox(vehicule_frame, width=40, height=15)
        self.vehicules_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v = ttk.Scrollbar(vehicule_frame, orient=tk.VERTICAL, command=self.vehicules_listbox.yview)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        self.vehicules_listbox.config(yscrollcommand=scrollbar_v.set)
        
        # Livreurs
        ttk.Label(list_frame, text="Livreurs").grid(row=0, column=1, sticky="w")
        livreur_frame = ttk.Frame(list_frame)
        livreur_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.livreurs_listbox = tk.Listbox(livreur_frame, width=40, height=15)
        self.livreurs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_l = ttk.Scrollbar(livreur_frame, orient=tk.VERTICAL, command=self.livreurs_listbox.yview)
        scrollbar_l.pack(side=tk.RIGHT, fill=tk.Y)
        self.livreurs_listbox.config(yscrollcommand=scrollbar_l.set)
        
        # Commandes
        ttk.Label(list_frame, text="Commandes").grid(row=0, column=2, sticky="w")
        commande_frame = ttk.Frame(list_frame)
        commande_frame.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
        self.commandes_listbox = tk.Listbox(commande_frame, width=40, height=15)
        self.commandes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_c = ttk.Scrollbar(commande_frame, orient=tk.VERTICAL, command=self.commandes_listbox.yview)
        scrollbar_c.pack(side=tk.RIGHT, fill=tk.Y)
        self.commandes_listbox.config(yscrollcommand=scrollbar_c.set)
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="Ajouter Véhicule", command=self.add_vehicule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Ajouter Livreur", command=self.add_livreur).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Créer Commande", command=self.add_commande).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Attribuer Véhicule", command=self.attribuer_vehicule).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Effectuer Livraison", command=self.effectuer_livraison).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Afficher État", command=self.afficher_etat).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Quitter", command=self.on_close).pack(side=tk.RIGHT, padx=5)
    
    def safe_update_listboxes(self):
        """Mise à jour sécurisée des listes"""
        if not self.winfo_exists():
            return
            
        try:
            self.update_listboxes()
        except tk.TclError as e:
            print(f"Erreur lors de la mise à jour des listes: {e}")
    
    def update_listboxes(self):
        """Mise à jour des listes de l'interface"""
        # Mise à jour des véhicules
        self.vehicules_listbox.delete(0, tk.END)
        for v in self.depot.vehicules_disponibles:
            self.vehicules_listbox.insert(tk.END, str(v))
        
        # Mise à jour des livreurs
        self.livreurs_listbox.delete(0, tk.END)
        for l in self.depot.livreurs_disponibles:
            self.livreurs_listbox.insert(tk.END, str(l))
        
        # Mise à jour des commandes
        self.commandes_listbox.delete(0, tk.END)
        for c in self.depot.commandes:
            status = "🟢" if c.statut == "livrée" else "🟠"
            self.commandes_listbox.insert(tk.END, f"{status} {c.id} - {c.destination} ({c.poids}kg)")
    
    def add_vehicule(self):
        dialog = AjoutVehiculeDialog(self)
        self.wait_window(dialog)
        self.safe_update_listboxes()
    
    def add_livreur(self):
        dialog = AjoutLivreurDialog(self)
        self.wait_window(dialog)
        self.safe_update_listboxes()
    
    def add_commande(self):
        dialog = AjoutCommandeDialog(self)
        self.wait_window(dialog)
        self.safe_update_listboxes()
    
    def attribuer_vehicule(self):
        livreur_idx = self.livreurs_listbox.curselection()
        vehicule_idx = self.vehicules_listbox.curselection()
        
        if not livreur_idx or not vehicule_idx:
            messagebox.showerror("Erreur", "Sélectionnez un livreur et un véhicule")
            return
        
        livreur = self.depot.livreurs_disponibles[livreur_idx[0]]
        vehicule = self.depot.vehicules_disponibles[vehicule_idx[0]]
        self.depot.attribuer_vehicule(livreur, vehicule)
        self.safe_update_listboxes()
        messagebox.showinfo("Succès", f"Véhicule attribué à {livreur.nom}")
    
    def effectuer_livraison(self):
        livreur_idx = self.livreurs_listbox.curselection()
        if not livreur_idx:
            messagebox.showerror("Erreur", "Sélectionnez un livreur")
            return
        
        livreur = self.depot.livreurs_disponibles[livreur_idx[0]]
        if not livreur.vehicule:
            messagebox.showerror("Erreur", "Le livreur n'a pas de véhicule attribué")
            return
        
        if not livreur.commandes_en_cours:
            messagebox.showinfo("Information", "Ce livreur n'a aucune commande à livrer")
            return
        
        result = livreur.effectuer_livraison()
        messagebox.showinfo("Résultat livraison", result)
        self.safe_update_listboxes()
    
    def afficher_etat(self):
        messagebox.showinfo("État du dépôt", self.depot.afficher_etat())

# Dialogs pour l'ajout d'éléments
class AjoutVehiculeDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Ajouter un véhicule")
        self.geometry("300x250")
        self.transient(parent)
        self.grab_set()
        
        # Configuration de la grille
        self.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self, text="Type:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.type_var = tk.StringVar(value="Camion")
        ttk.Combobox(self, textvariable=self.type_var, values=["Camion", "Moto"]).grid(
            row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(self, text="Marque:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.marque_entry = ttk.Entry(self)
        self.marque_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(self, text="Modèle:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.modele_entry = ttk.Entry(self)
        self.modele_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(self, text="Immatriculation:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.immat_entry = ttk.Entry(self)
        self.immat_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(self, text="Capacité (t) / Vitesse (km/h):").grid(
            row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.attribut_entry = ttk.Entry(self)
        self.attribut_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Ajouter", command=self.valider).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def valider(self):
        try:
            type_ = self.type_var.get()
            marque = self.marque_entry.get().strip()
            modele = self.modele_entry.get().strip()
            immat = self.immat_entry.get().strip()
            attribut = float(self.attribut_entry.get().strip())
            
            if not marque or not modele or not immat:
                messagebox.showerror("Erreur", "Tous les champs doivent être remplis")
                return
            
            if type_ == "Camion":
                vehicule = Camion(marque, modele, immat, attribut)
            else:
                vehicule = Moto(marque, modele, immat, attribut)
            
            self.parent.depot.ajouter_vehicule(vehicule)
            self.destroy()
        except ValueError:
            messagebox.showerror("Erreur", "Données invalides")

class AjoutLivreurDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Ajouter un livreur")
        self.geometry("300x150")
        self.transient(parent)
        self.grab_set()
        
        # Configuration de la grille
        self.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self, text="Nom:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.nom_entry = ttk.Entry(self)
        self.nom_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Ajouter", command=self.valider).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def valider(self):
        nom = self.nom_entry.get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide")
            return
            
        if Livreur.verifier_nom(nom):
            livreur = Livreur(nom)
            self.parent.depot.ajouter_livreur(livreur)
            self.destroy()
        else:
            messagebox.showerror("Erreur", "Nom invalide (caractères alphabétiques uniquement)")

class AjoutCommandeDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Créer une commande")
        self.geometry("300x200")
        self.transient(parent)
        self.grab_set()
        
        # Configuration de la grille
        self.grid_columnconfigure(1, weight=1)
        
        ttk.Label(self, text="ID:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.id_entry = ttk.Entry(self)
        self.id_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(self, text="Destination:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.dest_entry = ttk.Entry(self)
        self.dest_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(self, text="Poids (kg):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.poids_entry = ttk.Entry(self)
        self.poids_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Créer", command=self.valider).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def valider(self):
        try:
            id_ = self.id_entry.get().strip()
            destination = self.dest_entry.get().strip()
            poids = float(self.poids_entry.get().strip())
            
            if not id_ or not destination:
                messagebox.showerror("Erreur", "ID et destination sont obligatoires")
                return
                
            if Commande.valider_poids(poids):
                commande = Commande(id_, destination, poids)
                self.parent.depot.ajouter_commande(commande)
                self.destroy()
            else:
                messagebox.showerror("Erreur", "Poids invalide (0 < poids <= 100kg)")
        except ValueError:
            messagebox.showerror("Erreur", "Données invalides")

# Point d'entrée de l'application
if __name__ == "__main__":
    depot = Depot()
    
    # Exemple de données initiales
    depot.ajouter_vehicule(Camion("Renault", "Truck", "AB-123-CD", 10))
    depot.ajouter_vehicule(Moto("Yamaha", "MT-07", "XYZ-987", 120))
    depot.ajouter_livreur(Livreur("Jean Dupont"))
    depot.ajouter_commande(Commande("CMD001", "Paris", 5))
    depot.ajouter_commande(Commande("CMD002", "Lyon", 8))
    
    app = Application(depot)
    app.mainloop()