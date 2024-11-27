from SunFounder_Ultrasonic_Avoidance import Ultrasonic_Avoidance
import csv
import time

UA = Ultrasonic_Avoidance.Ultrasonic_Avoidance(20)
threshold = 10


def main():
    # Nom du fichier CSV
    distance = UA.get_distance()
    nom_fichier = 'donnees_10cm.csv'
    status = UA.less_than(threshold)
    while(True):
        if distance != -1:
            print('distance', distance, 'cm')
            """ with open(nom_fichier, mode='a', newline='', encoding='utf-8') as fichier:  # Mode 'a' pour ajouter les données
                writer = csv.writer(fichier)
                
                # Écrire la distance sous la colonne "Donner a 10cm"
                writer.writerow([distance])  # Ajouter la distance à une nouvelle ligne  """
            #time.sleep(0.2)  # Petite pause pour éviter trop de lectures rapides
        else:
            print(False)
        if status == 1:
            print("Less than %d" % threshold)
        elif status == 0:
            print("Over %d" % threshold)
        else:
            print("Read distance error.")


if __name__=='__main__':
    main()