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

- Besoins de drop 250V à 12V avec au moins 1A de courant...
- Du 12v on veux avoir 
  - une 5V crass pour power les ADC et les teensy. Ce 5V doit pouvoir tiré jusqu'a 0.3 A mettons
  - un 5V vraiment clean pour alimenter les accels



## Avancement actuel -- 19 novembre

- LE board du power supply est mis de côté pour l'instant en attendant d'Avoir plus de détails sur la puissance requise par le système de couplage
- Le THVD8000 est ok et les drivers aussi et les ADC aussi, mais il faudrait check les electrical rules
- Le prochain schematic à faire est celui pour les accels

## Next - 25 novembre

- Conception du circuit pour les accels
  - Creation de la pièce pour accel

## 29 Novembre

Circuit accels ok, peut etre rajouté un condensateur pour réduire le bruit venant du 5V de référence

Fouille pour des connecteurs, trouvé les omnetics ou les harwins 

finalement va y aller avec les harwins a moins d'Avis contraire mais il faut que je demande à Christian

Pour la suite du routing:

- essayer de laccer les decoupling capacitor sur le bottom layer (autant pour less Vref que pour l'ADC)
- Signaux digitaux de l'ADC vers le teensy sur el bottom plane et du teensy vers le RS485 sur le top plane 

## 9 décembre

-  Ne pas oublier d'acheter des résistance pour le diviseur de tension du 12V vers le 5V qui peut soutenir 6W environ (12V et 0.5A)
- Notes pour Vref :

  - MAnque les connections au 12V pour le ref et le 5V no clean
-  Est-ce que la puce V3 ref est capable de pousser pour le thvd8000?
- DRC à tous les endroit ou j'ai un via qui se connecte au ground ou au 5V FIXED : set the split plane to the good net (see github psush comment)

  - Les connections qui emploi un via entre le top et le bottom layer eux n'ont pas d'erreur. 
  - Les erreurs sont donc liées au plan ground et 5V


## 13 décembre

Choix des connecteurs :

- Modification du schématic (retrait des plugs)

  - pin map : 
    - channel 3 16-15-8-7 -u9    p14-p16
    - channel 2 14-13-6-5 -u8    p13-p11
    - channel 1 12-11 4-3  p12-p5
    - channel 0 10-9  2-1 p17-p15

- Réarrangement des drivers pour laisser la place aux connecteurs

- placer le modèle 3D

  

## 14 décembre

- RAjouter des vis sur le board d'Accel pour le fixer au accel holder -- DONE
- FAire une liste de révision complète:
  - Vérifier les pins de l'ADC si cest les même connections que pour l'ancien board et la datasheet -- OK
  - Vérifivier la limite de Puissance pour les résistances -- OK, mais plusieurs quesitons, voir plus bas
  - Vérifier la capacité des Vrf en courant -> faire un tableau de la demande et de la capacité -- OK et changé le 3.3V
  - Vérifier les connections du THVD8000 - vérifier la vitesse max de transfert sur le cable du treuil
  - Vérifier les connections du teensy -- OK
  - Vérifier les connections des amplis -- OK
  - REgarder pour la grosseur des traces requise pour le 12V 0.4 AMp (plus gros que 0.254 mils?)
  - Générer les BOM et vérifier que tout est dispo chez les fournisseurs
- Passer les commandes de pièces et de PCB
  - Rajouter de la pate à souder
- Passer la commandes pour les accels



> Questions pour Christian:
>
> - Est-ce que le V4ref est équivalent ou jai besoins de dupliquer? -- OK si les impédance de ref1 et ref2 sont pareils -- pas trouvé d'info la dessu...
> - Pin DIN doit être maintenu à GND avec une pull-down resistor est ce que la config est ok? -- OK au pire no short
> - Vérifier les résistance du voltage régulator pour le 5V no clean : est-ce que les résistances sont ok avec 1/10W et est-ce que je suis obliger de faire le voltage divider selon la datasheet? OK je crois quon va envoyer le 12V direct dans le ENABLE donc meme pas de diviseur de tension
> - Résistance d'entre GND et entrées analogue est ce que cest ok 1/10W? Avec précision de 0.5% -- Oui C'est ok
> - Résistance dans le module THVD8000 cest 120omhs 1/10W et 0.1%, pas assez résistant? Il n'y aura plus de DC à ce moment -- OK pas bp de courant qui va passé là.
>
> changer les vis pour des m3 -- OK
> changer le connecteurs 12V pour des vis -- OK
> Bord THVD8000 à révisier

## 17 décembre

- révision des circruits thvd8000
  - retrait des bobines du baord principales : celles-ci seront sur le power supply
- Le retrait des bobines laisse plus de place : il faut donc réarranger le board dans ce coin
- NEXT : générer le BOM et faire la commande pour lundi
