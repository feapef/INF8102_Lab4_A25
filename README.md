# INF8102 - Sécurité Informatique -- Automne 2025
### TP4 : Infrastructure as Code Security

Repertoire git pour le lab 4 sur l'IaC avec python

----------
#### Utilisation

- Créer le fichier **aws_credentials** avec vos identifiants. 
- Importer ses templates dans le dossier **templates** 
- Modifier les paramètres dans **iac_boto3.py**. 
- Executer la commande : `python3 iac_boto3.py`

----------
#### Structure du répertoire
```
.
├── aws_credentials         [caché pour des questions de sécurité]
├── iac_boto3.py            [code pour lancer une pile sur cloudformation]
├── README.md
└── templates
    ├── ec2.json
    ├── s3.json
    └── vpc.yaml
```
