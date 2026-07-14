import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Charger le fichier .env
load_dotenv()

# Lire les identifiants
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER")
password = os.getenv("NEO4J_PASSWORD")

print(f"🔍 Diagnostic de connexion Neo4j...")
print(f"📡 URI : {uri}")
print(f"👤 User : {user}")
print(f"🔑 Password : {password[:5]}... (Masqué)")

try:
    # Tenter la connexion
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 1 as result")
        value = result.single()["result"]
        if value == 1:
            print("✅ SUCCÈS : La connexion à Neo4j est parfaite !")
        else:
            print("❌ ÉCHEC : La base a répondu mais avec une valeur inattendue.")
    driver.close()
except Exception as e:
    print(f"❌ ERREUR DÉTAILLÉE : {e}")