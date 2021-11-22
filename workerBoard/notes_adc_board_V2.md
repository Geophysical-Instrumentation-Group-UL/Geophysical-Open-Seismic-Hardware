# Amélioration à faire au board de l'ADC

-----

## Général

- Switch vraiment plus petite
- Composantes sur les 2 côtés
- 4 layers ?
- Un 5V clean pour les accel
- Mount pour le Teensy directement
- Alimentation 3.3 pour le board teensy
- Interface pour les câbles armés du treuil

## Analogique

- Relier les pins de entrées avec des résistance de 1.5 MOhms
- Enlever les headers permettant d'isoler certains channels
- Vref - : refaire le decoupling vers le ground.
- Source de 4.096 : Trouver la meilleur source possible

## Source de tension

- Revoir les valeurs des capaciteurs de découplage





## Plan des modifications à faire

- Remplacer le 8 channel par un 4 channel -- OK
- delete les drivers pour les channel 4-8 -- OK
-  Decoupling capacitor Vref- --- OK
- Conception d'un circuit d'alimentation pour drop le voltage de la ligne
- Switch plus petite (bouton seulement) -- OK
- Choix des résistances pour les entrées analogiques. Peut être demander à Analog device pourquoi il faut ces résistances -- En attente de la réponse de AD -- JEVAIS JUSTE  LES METTRES... --OK
- Changer le footprint des capacitors pour du 0603 -- OK
- REgarder pour les microphonicics capacitors
- REgarder pour des tantalu

## Notes sur les pins du Teensy

- Les pins 2,3,4 et 5 sont réservé pour les sorties de l'ADC
- La pin 9 sur le slave est pour le MODE de la chip RS485
- ChipSelectPIN = 10
- CLCK de l'ADC = 6
- DRDY de l'ADC = 18 -- est-ce qu'il faut plus qu'une PIN DRDY? NON seulement 1 PIN
- le SERIAL pour le RS485 est le SERIAL3 aux pin RX=15 et TX=14
- LE 3.3 et le GND au bout du board vont faire al chip RS485
- Le SPI utilise les pin standars du teensy, soit CS=10, MOSI=SDI=11,MISO=SDO=12



## Notes sur le circuit du THVD8000

- pense pas que j'ai besoin d'avoir un pull up ou pull down resistor sur le R et D car ces pins sont relié aux pins du port serial du TEENSY. Sinon pour la pin mode je peux toujours la déclaré dans le code avec la condition input_pull_down

 ## Questions pour Christian

- Est-ce que les différentes sources (combinaisons capaciteurs/sources 5V) dans le schematic des drivers sont nécessaire? Est-ce que je pourrai utiliser seulement 1 pour tous les drivers?
- LEs résistances pour les entrées analogiques : est-ce que la précision doit être élevé et aussi le drift en temps? Pour l'instant j'ai 0.5% et 25ppm/°C

## Conception du voltage regulator

- Besoins de drop 250V à 5V avec au moins 1A de courant...