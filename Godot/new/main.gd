extends Node3D

# Référence au véhicule


func _ready() -> void:
	var Cybertruck: Node3D
	# Charger le véhicule dans la scène
	Cybertruck = $Cybertruck
	var Ligne: Node3D
	Ligne = $NodeLigne
	# Charger le véhicule dans la scène
	Cybertruck = $Cybertruck
	# Vérifier si le véhicule est bien référencé
	if Cybertruck:
		print("Véhicule initialisé correctement.")
	else:
		print("Erreur : le véhicule n'est pas trouvé dans la scène.")
	if Ligne:
		print("obstcale initialisé correctement.")
	else:
		print("Erreur : le obstcale n'est pas trouvé dans la scène.")
