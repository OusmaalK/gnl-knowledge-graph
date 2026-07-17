"""
Application FastAPI principale
"""

from fastapi import Depends, FastAPI, Request, APIRouter, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import os
from typing import Dict, Any, Optional
from jose import jwt
from pydantic import BaseModel

# Import pour la connexion Neo4j
from neo4j import GraphDatabase

# Import pour le JWT
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from .routers import graph, agents, queries, health
from .middleware import logging as logging_middleware
from .middleware import metrics as metrics_middleware
from .routers import websocket

# --- SOLUTION FINALE POUR LES IMPORTS SUR RAILWAY ---
import sys
import os
# Ajoute le dossier 'backend' au path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.config import settings
from src.core.exceptions import GNLException
from src.core.security import verify_password, get_password_hash, create_access_token
# ---------------------------------------------------

logger = logging.getLogger(__name__)

# --- CONFIGURATION DE SECURITE AJOUTEE ---
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

SECRET_KEY = "votre_cle_secrete_tres_longue_et_compliquee_ici" # Changez ceci par une vraie clé
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
# --- FIN DE LA CONFIGURATION AJOUTEE ---

# ========================================================
# MODÈLES DE DONNÉES
# ========================================================
class AgentRequest(BaseModel):
    query: str
    params: Optional[Dict[str, Any]] = None

class RouteSearchRequest(BaseModel):
    start_id: str
    end_id: str
    exclude_id: Optional[str] = None

class IoTSettingsRequest(BaseModel):
    mqtt_broker: str
    mqtt_port: int
    mqtt_topic: str
    neo4j_label: str
    alert_threshold_temperature: int
    alert_threshold_pression: int

class AutoIncidentRequest(BaseModel):
    id: str
    description: str
    gravite: str
    date: str
    cause: str
    duree_min: int
    equipment_id: str

# --- NOUVEAUX MODÈLES AUTH ---
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
# ========================================================

def create_app() -> FastAPI:
    """
    Crée l'application FastAPI
    """
    app = FastAPI(
        title="GNL Knowledge Graph API",
        description="API pour l'interrogation du graphe de connaissances GNL",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware personnalisés
    app.add_middleware(
        logging_middleware.LoggingMiddleware,
        logger_name="api.access"
    )
    app.add_middleware(
        metrics_middleware.MetricsMiddleware
    )

    # Gestionnaire d'exceptions global
    @app.exception_handler(GNLException)
    async def gnl_exception_handler(request: Request, exc: GNLException):
        logger.error(f"GNLException: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "code": exc.code,
                "details": exc.details
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Exception non gérée: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erreur interne du serveur",
                "detail": str(exc) if settings.DEBUG else None
            }
        )

    # ========================================================
    # ROUTES ADMIN
    # ========================================================
    admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

    @admin_router.get("/status")
    async def get_system_status():
        services = [
            {"name": "Neo4j", "status": "up"},
            {"name": "Qdrant", "status": "up"},
            {"name": "Redis", "status": "up"},
            {"name": "Kafka", "status": "up"},
            {"name": "Backend API", "status": "up"},
        ]
        up_count = sum(1 for s in services if s['status'] == 'up')
        return {
            "services_up": up_count,
            "services_total": len(services),
            "users": 0,
            "services": services
        }

    @admin_router.get("/database/stats")
    async def get_database_stats():
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                nodes_result = session.run("MATCH (n) RETURN count(n) as count")
                nodes_count = nodes_result.single()["count"]
                rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
                rels_count = rels_result.single()["count"]
            driver.close()
            return {"nodes": nodes_count, "relationships": rels_count}
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les stats Neo4j: {e}")
            return {"nodes": 0, "relationships": 0}

    app.include_router(admin_router)

    # ========================================================
    # ROUTES AUTHENTIFICATION (NEO4J)
    # ========================================================
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    async def get_current_user(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Token invalide")
            
            # Vérifier si l'utilisateur existe toujours dans Neo4j
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("MATCH (u:User {email: $email}) RETURN u", email=email)
                record = result.single()
            driver.close()
            
            if not record:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
            
            return {"email": record["u"]["email"], "role": record["u"]["role"]}
        except JWTError:
            raise HTTPException(status_code=401, detail="Token invalide")

    @app.post("/api/auth/register")
    async def register_user(user_data: UserRegister):
        try:
            # --- RÉCUPÉRATION SÉCURISÉE DES IDENTIFIANTS NEO4J ---
            import os
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            
            if not neo4j_uri or not neo4j_user or not neo4j_password:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Configuration Neo4j manquante sur Railway. URI: {neo4j_uri is not None}, User: {neo4j_user is not None}, Password: {neo4j_password is not None}"
                )
            
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            # ----------------------------------------------------
            
            with driver.session() as session:
                # 1. Vérifier si l'email existe déjà
                check_result = session.run("MATCH (u:User {email: $email}) RETURN u", email=user_data.email)
                if check_result.single():
                    raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
                
                # 2. Hacher le mot de passe
                hashed_password = get_password_hash(user_data.password)
                
                # 3. Créer le nœud User dans Neo4j
                session.run("""
                CREATE (u:User {
                    email: $email,
                    hashed_password: $hashed_password,
                    role: 'viewer',
                    status: 'pending',
                    created_at: datetime()
                })
                """, email=user_data.email, hashed_password=hashed_password)
                
            driver.close()
            return {"message": "Compte créé avec succès. En attente d'approbation admin."}
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            logger.error(f"❌ Erreur lors de l'inscription: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
    
    @app.post("/api/auth/login")
    async def login_user(user_data: UserLogin):
        try:
            # --- RÉCUPÉRATION SÉCURISÉE DES IDENTIFIANTS NEO4J ---
            import os
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            
            if not neo4j_uri or not neo4j_user or not neo4j_password:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Configuration Neo4j manquante sur Railway. URI: {neo4j_uri is not None}, User: {neo4j_user is not None}, Password: {neo4j_password is not None}"
                )
            
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            # ----------------------------------------------------
            
            with driver.session() as session:
                # 1. Chercher l'utilisateur dans Neo4j
                result = session.run("MATCH (u:User {email: $email}) RETURN u", email=user_data.email)
                record = result.single()
                
                if not record:
                    raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
                
                user = record["u"]
                
                # 2. Vérifier si le compte est actif
                if user.get("status") != "active":
                    raise HTTPException(status_code=403, detail="Compte en attente de validation ou désactivé")
                
                # 3. Vérifier le mot de passe
                if not verify_password(user_data.password, user["hashed_password"]):
                    raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
                
                # 4. Générer le token JWT
                access_token = create_access_token(data={"sub": user["email"], "role": user["role"]})
                
            driver.close()
            return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de la connexion: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne du serveur")
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Token invalide")
            
            # --- RÉCUPÉRATION SÉCURISÉE DES IDENTIFIANTS NEO4J ---
            import os
            neo4j_uri = os.getenv("NEO4J_URI")
            neo4j_user = os.getenv("NEO4J_USER")
            neo4j_password = os.getenv("NEO4J_PASSWORD")
            
            if not neo4j_uri or not neo4j_user or not neo4j_password:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Configuration Neo4j manquante pour get_current_user. URI: {neo4j_uri is not None}, User: {neo4j_user is not None}, Password: {neo4j_password is not None}"
                )
            
            driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            # ----------------------------------------------------
            
            with driver.session() as session:
                result = session.run("MATCH (u:User {email: $email}) RETURN u", email=email)
                record = result.single()
            driver.close()
            
            if not record:
                raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
            
            return {"email": record["u"]["email"], "role": record["u"]["role"]}
        except JWTError:
            raise HTTPException(status_code=401, detail="Token invalide")

    # ========================================================
    # ROUTES ADMIN USERS (GESTION UTILISATEURS)
    # ========================================================
    @app.get("/api/admin/users")
    async def get_all_users():
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("""
                MATCH (u:User)
                RETURN 
                    u.email as email,
                    u.name as name,
                    u.role as role,
                    u.status as status,
                    u.created_at as created_at
                """)
                users = [{"email": r["email"], "name": r["name"] or r["email"].split('@')[0], "role": r["role"], "status": r["status"] or "pending", "created_at": str(r["created_at"])} for r in result]
            driver.close()
            return users
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des utilisateurs: {e}")
            return []

    @app.post("/api/admin/users/{email:path}/approve")
    async def approve_user(email: str, payload: dict = Body(...)):
        new_role = payload.get('role', 'viewer')
        try:
            from dotenv import load_dotenv
            import os
            import sib_api_v3_sdk
            from sib_api_v3_sdk.rest import ApiException

            env_path = os.path.join(os.path.dirname(__file__), '../../.env')
            load_dotenv(env_path, override=True)

            # ==========================================
            # 1. MISE À JOUR DU STATUT DANS NEO4J
            # ==========================================
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                session.run("""
                MATCH (u:User {email: $email})
                SET u.status = 'active', u.role = $role
                """, email=email, role=new_role)
            driver.close()

            # ==========================================
            # 2. ENVOI D'EMAIL VIA BREVO
            # ==========================================
            email_sent = False
            try:
                configuration = sib_api_v3_sdk.Configuration()
                configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")
                api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

                sender_email = os.getenv("BREVO_SENDER_EMAIL", "admin@gnl.com")
                sender_name = os.getenv("BREVO_SENDER_NAME", "GNL Knowledge Graph")

                send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                    to=[{"email": email, "name": email.split("@")[0]}],
                    sender={"name": sender_name, "email": sender_email},
                    subject="✅ Votre compte GNL Knowledge Graph est approuvé !",
                    html_content=f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; color: #333;">
                            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                                <div style="text-align: center; margin-bottom: 20px;">
                                    <h1 style="color: #1e3a8a;">⛽ GNL Knowledge Graph</h1>
                                </div>
                                <h2>Félicitations {email.split('@')[0]} !</h2>
                                <p>Votre compte a été <strong>approuvé</strong> par l'administrateur.</p>
                                <p>Vous avez désormais le rôle : <strong style="color: #2563eb;">{new_role}</strong></p>
                                <div style="background-color: #f0f9ff; padding: 15px; border-radius: 8px; margin-top: 20px;">
                                    <p>Vous pouvez maintenant vous connecter à la plateforme :</p>
                                    <a href="http://localhost:3000/auth/login" style="display: inline-block; background-color: #1e3a8a; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold;">
                                        Se connecter
                                    </a>
                                </div>
                                <p style="margin-top: 20px; font-size: 12px; color: #888;">L'équipe GNL Knowledge Graph</p>
                            </div>
                        </body>
                    </html>
                    """
                )

                api_response = api_instance.send_transac_email(send_smtp_email)
                logger.info(f"📧 Email envoyé avec succès à {email}")
                email_sent = True

            except ApiException as e:
                logger.error(f"❌ Erreur lors de l'envoi de l'email: {e}")
                email_sent = False
            except Exception as e:
                logger.error(f"❌ Erreur inconnue lors de l'envoi de l'email: {e}")
                email_sent = False

            # ==========================================
            # 3. RETOURNER LE SUCCÈS AVEC LE STATUT DE L'EMAIL
            # ==========================================
            if email_sent:
                return {"message": f"Utilisateur {email} approuvé avec le rôle {new_role}. Email envoyé avec succès."}
            else:
                return {"message": f"Utilisateur {email} approuvé avec le rôle {new_role}. (Email non envoyé, vérifiez la configuration Brevo)."}

        except Exception as e:
            logger.error(f"❌ Erreur critique lors de l'approbation: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne")
    
    
    @app.post("/api/admin/users/{email:path}/disable")
    async def disable_user(email: str):
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                session.run("""
                MATCH (u:User {email: $email})
                SET u.status = 'inactive'
                """, email=email)
            driver.close()
            return {"message": f"Utilisateur {email} désactivé"}
        except Exception as e:
            logger.error(f"❌ Erreur lors de la désactivation: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne")

    @app.delete("/api/admin/users/{email:path}")
    async def delete_user(email: str):
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            
            with driver.session() as session:
                result = session.run("MATCH (u:User {email: $email}) DELETE u RETURN count(u) as deleted_count", email=email)
                record = result.single()
                deleted_count = record["deleted_count"] if record else 0
                
                if deleted_count == 0:
                    driver.close()
                    raise HTTPException(status_code=404, detail=f"Utilisateur {email} non trouvé")
            
            driver.close()
            logger.info(f"✅ Utilisateur {email} supprimé avec succès")
            return {"message": f"Utilisateur {email} supprimé"}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")
    # ========================================================

    # ========================================================
    # ROUTES POUR PILOTER L'ÉCOUTEUR IOT
    # ========================================================
    @app.post("/api/iot/control")
    async def iot_control(payload: dict = Body(...)):
        action = payload.get('action')
        try:
            import sys
            import os
            
            # --- SOLUTION ULTIME POUR RAILWAY ---
            # Obtenir le chemin absolu du dossier backend
            backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            scripts_data_dir = os.path.join(backend_root, 'scripts', 'data')
            
            # Ajouter au path Python
            if scripts_data_dir not in sys.path:
                sys.path.insert(0, scripts_data_dir)
            # ------------------------------------
            
            try:
                from iot_manager import start_listener, stop_listener, get_status
            except ImportError as e:
                return {"status": "error", "message": f"Impossible d'importer iot_manager : {str(e)}"}

            if action == 'start':
                return start_listener()
            elif action == 'stop':
                return stop_listener()
            elif action == 'status':
                return get_status()
            else:
                return {"status": "error", "message": "Action inconnue"}
        except Exception as e:
            return {"status": "error", "message": f"Erreur serveur: {str(e)}"}
    # ========================================================

    # ========================================================
    # ROUTES LOGISTIQUE
    # ========================================================
    @app.get("/api/logistics/supply-chain")
    async def get_supply_chain():
        try:
            driver = GraphDatabase.driver(
                settings.NEO4J_URI, 
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            with driver.session() as session:
                result = session.run("""
                MATCH (f:Fournisseur)-[:FOURNIT]->(t:Terminal)-[:ALIMENTE]->(p:Pipeline)-[:DESSERT]->(c:Client)
                RETURN f.id as source, t.id as target, 'Fournisseur' as type
                UNION
                MATCH (t:Terminal)-[:ALIMENTE]->(p:Pipeline)
                RETURN t.id as source, p.id as target, 'Terminal' as type
                UNION
                MATCH (p:Pipeline)-[:DESSERT]->(c:Client)
                RETURN p.id as source, c.id as target, 'Pipeline' as type
                """)
                nodes = [{"source": row["source"], "target": row["target"], "type": row["type"]} for row in result]
            driver.close()
            return nodes
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer la chaîne: {e}")
            return []

    @app.get("/api/logistics/risk-heatmap")
    async def get_risk_heatmap():
        try:
            driver = GraphDatabase.driver(
                settings.NEO4J_URI, 
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            with driver.session() as session:
                result = session.run("""
                MATCH (p:Pipeline)
                OPTIONAL MATCH (p)<-[:AFFECTE]-(i:Incident)
                WHERE i.date >= date() - duration('P30D')
                RETURN p.id as id, p.nom as nom, COUNT(i) as incident_count, p.statut as statut
                """)
                pipelines = [{"id": row["id"], "nom": row["nom"], "incidents": row["incident_count"], "statut": row["statut"]} for row in result]
            driver.close()
            
            for p in pipelines:
                p['reliability'] = max(0, 100 - (p['incidents'] * 10))
                if p.get('statut') == 'critique':
                    p['reliability'] -= 20
                elif p.get('statut') == 'warning':
                    p['reliability'] -= 10
                p['reliability'] = max(0, min(100, p['reliability']))
                
            return pipelines
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer la carte des risques: {e}")
            return []

    @app.post("/api/logistics/route")
    async def search_route_endpoint(request: RouteSearchRequest):
        try:
            from ..agents.agents.logistics_agent import LogisticsAgent
            agent = LogisticsAgent()
            params = {
                'start': request.start_id,
                'end': request.end_id,
                'exclude': request.exclude_id
            }
            response = agent.find_best_route(request.start_id, request.end_id)
            return response
        except Exception as e:
            logger.error(f"❌ Erreur dans /api/logistics/route: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    # ========================================================
    # ROUTES MAINTENANCE
    # ========================================================
    @app.get("/api/maintenance/equipment")
    async def get_maintenance_equipment():
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("""
                MATCH (n)
                WHERE n:Pipeline OR n:Compresseur OR n:Terminal
                OPTIONAL MATCH (n)<-[:AFFECTE]-(i:Incident)
                WHERE i.date >= date() - duration('P30D')
                RETURN n.id as id, n.nom as nom, labels(n)[0] as type, n.statut as statut, COUNT(i) as incidents
                """)
                equipment = [{"id": row["id"], "nom": row["nom"], "type": row["type"], "statut": row["statut"], "incidents": row["incidents"]} for row in result]
            driver.close()
            
            for eq in equipment:
                if eq['incidents'] >= 2:
                    eq['risk_level'] = 'ÉLEVÉ'
                elif eq['incidents'] >= 1:
                    eq['risk_level'] = 'MOYEN'
                else:
                    eq['risk_level'] = 'FAIBLE'
                    
            return equipment
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les équipements: {e}")
            return []

    @app.get("/api/maintenance/risks")
    async def get_maintenance_risks():
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("""
                MATCH (n)
                WHERE n:Pipeline OR n:Compresseur OR n:Terminal
                OPTIONAL MATCH (n)<-[:AFFECTE]-(i:Incident)
                WHERE i.date >= date() - duration('P30D')
                RETURN COUNT(DISTINCT n) as total, COUNT(DISTINCT i) as total_incidents
                """)
                data = result.single()
                total_eq = data["total"] if data else 0
                total_inc = data["total_incidents"] if data else 0
                
            driver.close()
            return {
                "critical": 1 if total_inc > 0 else 0,
                "high": 2 if total_inc > 0 else 0,
                "planned": 3,
                "avgResolution": "4h 30min",
                "history": [
                    {"date": "2026-07-08", "score": 65, "incidents": 1},
                    {"date": "2026-07-05", "score": 45, "incidents": 0},
                    {"date": "2026-07-01", "score": 30, "incidents": 0}
                ]
            }
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les risques: {e}")
            return {}

    # ========================================================
    # ROUTES ANALYSE
    # ========================================================
    @app.get("/api/analysis/{tab}")
    async def get_analysis_data(tab: str, period: str = '30d', equipment: str = 'all', severity: str = 'all'):
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            result_data = {}
            
            with driver.session() as session:
                if tab == 'incidents':
                    gravite_res = session.run("""
                    MATCH (i:Incident) RETURN i.gravite as label, count(i) as value
                    """)
                    gravite_data = [{"label": r["label"], "value": r["value"]} for r in gravite_res]

                    cause_res = session.run("""
                    MATCH (i:Incident) RETURN i.cause as label, count(i) as value
                    """)
                    cause_data = [{"label": r["label"], "value": r["value"]} for r in cause_res]

                    time_data = [{"label": "Jan", "value": 2}, {"label": "Fév", "value": 3}, {"label": "Mar", "value": 1}, {"label": "Avr", "value": 4}, {"label": "Mai", "value": 2}, {"label": "Juin", "value": 5}]

                    result_data = {
                        "incidents_by_severity": {
                            "labels": [d["label"] for d in gravite_data],
                            "datasets": [{"data": [d["value"] for d in gravite_data], "backgroundColor": ['#EF4444', '#F59E0B', '#EAB308']}]
                        },
                        "incidents_by_cause": {
                            "labels": [d["label"] for d in cause_data],
                            "datasets": [{"data": [d["value"] for d in cause_data], "backgroundColor": ['#8B5CF6', '#EC4899', '#F59E0B']}]
                        },
                        "incidents_over_time": {
                            "labels": [d["label"] for d in time_data],
                            "datasets": [{"data": [d["value"] for d in time_data], "color": "#3B82F6"}]
                        },
                        "resolution_time": {
                            "labels": ["Corrosion", "Mécanique", "Fluctuation"],
                            "datasets": [{"data": [120, 240, 45], "backgroundColor": '#3B82F6'}]
                        }
                    }

                elif tab == 'risks':
                    risk_res = session.run("""
                    MATCH (n) 
                    WHERE n:Pipeline OR n:Compresseur OR n:Terminal
                    RETURN n.risk_level as label, count(n) as value
                    """)
                    risk_data = [{"label": r["label"], "value": r["value"]} for r in risk_res]
                    if not risk_data:
                        risk_data = [{"label": "Inconnu", "value": 1}]

                    evolution_res = session.run("""
                    MATCH (h:RiskHistory) 
                    RETURN h.month as label, h.score as value
                    ORDER BY h.month
                    """)
                    evolution_data = [{"label": r["label"], "value": r["value"]} for r in evolution_res]

                    critical_res = session.run("""
                    MATCH (n) 
                    WHERE (n:Pipeline OR n:Compresseur OR n:Terminal) AND n.is_critical = true
                    RETURN n.id as label, 1 as value
                    """)
                    critical_data = [{"label": r["label"], "value": r["value"]} for r in critical_res]

                    corr_res = session.run("""
                    MATCH (n) 
                    WHERE n:Pipeline OR n:Compresseur OR n:Terminal
                    OPTIONAL MATCH (n)<-[:AFFECTE]-(i:Incident)
                    RETURN n.id as label, n.risk_level as risk, count(i) as incidents
                    """)
                    corr_data = [{"label": r["label"], "risk": r["risk"], "incidents": r["incidents"]} for r in corr_res]

                    result_data = {
                        "risk_levels": {
                            "labels": [d["label"] for d in risk_data],
                            "datasets": [{"data": [d["value"] for d in risk_data], "backgroundColor": ['#EF4444', '#F59E0B', '#3B82F6', '#10B981']}]
                        },
                        "risk_trend": {
                            "labels": [d["label"] for d in evolution_data],
                            "datasets": [{"data": [d["value"] for d in evolution_data], "color": "#EF4444"}]
                        },
                        "critical_equipment": {
                            "labels": [d["label"] for d in critical_data],
                            "datasets": [{"data": [d["value"] for d in critical_data], "backgroundColor": ['#EF4444', '#F59E0B']}]
                        },
                        "risk_correlation": {
                            "labels": [d["label"] for d in corr_data],
                            "datasets": [{
                                "label": "Risque",
                                "data": [3 if d["risk"] == "ÉLEVÉ" else 2 if d["risk"] == "MOYEN" else 1 for d in corr_data],
                                "backgroundColor": "#F59E0B"
                            }, {
                                "label": "Incidents",
                                "data": [d["incidents"] for d in corr_data],
                                "backgroundColor": "#EF4444"
                            }]
                        }
                    }

                elif tab == 'performance':
                    perf_res = session.run("""
                    MATCH (p:Pipeline) 
                    RETURN p.id as label, p.performance as value
                    """)
                    perf_data = [{"label": r["label"], "value": r["value"]} for r in perf_res]
                    if not perf_data:
                        perf_data = [{"label": "PIPE-001", "value": 95}, {"label": "PIPE-002", "value": 88}]

                    result_data = {
                        "pipeline_performance": {
                            "labels": [d["label"] for d in perf_data],
                            "datasets": [{"data": [d["value"] for d in perf_data], "backgroundColor": ['#10B981', '#F59E0B', '#3B82F6']}]
                        },
                        "availability": {
                            "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"],
                            "datasets": [{"data": [99, 98, 97, 96, 98, 99], "color": "#10B981"}]
                        },
                        "volume_transported": {
                            "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"],
                            "datasets": [{"data": [500, 550, 480, 600, 520, 580], "backgroundColor": "#3B82F6"}]
                        },
                        "energy_efficiency": {
                            "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"],
                            "datasets": [{"data": [85, 87, 86, 88, 87, 89], "color": "#8B5CF6"}]
                        }
                    }

                elif tab == 'trends':
                    hist_res = session.run("""
                    MATCH (h:History) 
                    RETURN h.month as label, h.risk_score as value
                    """)
                    hist_data = [{"label": r["label"], "value": r["value"]} for r in hist_res]
                    if not hist_data:
                        hist_data = [{"label": "Jan", "value": 45}, {"label": "Fév", "value": 50}, {"label": "Mar", "value": 55}]

                    result_data = {
                        "incident_trend": {
                            "labels": [d["label"] for d in hist_data],
                            "datasets": [{"data": [d["value"] for d in hist_data], "color": "#EF4444"}]
                        },
                        "incident_prediction": {
                            "labels": ["Août", "Sep", "Oct", "Nov", "Déc"],
                            "datasets": [{"data": [4, 3, 5, 4, 6], "color": "#8B5CF6"}]
                        },
                        "risk_trend": {
                            "labels": [d["label"] for d in hist_data],
                            "datasets": [{"data": [d["value"] for d in hist_data], "color": "#F59E0B"}]
                        },
                        "performance_trend": {
                            "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin"],
                            "datasets": [{"data": [85, 87, 86, 88, 87, 89], "color": "#10B981"}]
                        }
                    }
                else:
                    return {"error": "Onglet non pris en charge"}

            driver.close()
            return result_data
                
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les données d'analyse: {e}")
            return {}
    # ========================================================

    @app.get("/api/incidents")
    async def get_incidents(
        page: int = 1,
        limit: int = 100,
        severity: str = "all",
        status: str = "all",
        dateRange: str = "30d",
        search: str = ""
    ):
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            
            with driver.session() as session:
                result = session.run("""
                MATCH (i:Incident)
                OPTIONAL MATCH (i)-[:AFFECTE]->(e)
                RETURN 
                    i.id as id,
                    i.description as description,
                    i.gravite as gravite,
                    i.statut as statut,
                    i.date as date,
                    i.cause as cause,
                    i.duree_min as duree,
                    e.id as equipment_id,
                    e.nom as equipment_name
                ORDER BY i.date DESC
                """)
                
                incidents = []
                for record in result:
                    incidents.append({
                        "id": record["id"],
                        "description": record["description"],
                        "gravite": record["gravite"],
                        "statut": record["statut"],
                        "date": record["date"],
                        "cause": record["cause"],
                        "duree_min": record["duree"],
                        "equipment_id": record["equipment_id"],
                        "equipment_name": record["equipment_name"]
                    })
            
            driver.close()
            
            total = len(incidents)
            start = (page - 1) * limit
            end = start + limit
            items = incidents[start:end]
            
            return {"items": items, "total": total, "page": page, "limit": limit}
            
        except Exception as e:
            logger.warning(f"⚠️ Impossible de récupérer les incidents: {e}")
            return {"items": [], "total": 0, "page": 1, "limit": limit}
    @app.post("/api/incidents/auto")
    async def create_auto_incident(request: AutoIncidentRequest):
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                session.run("""
                CREATE (i:Incident {
                    id: $id,
                    description: $description,
                    gravite: $gravite,
                    date: $date,
                    cause: $cause,
                    duree_min: $duree_min
                })
                """, 
                id=request.id,
                description=request.description,
                gravite=request.gravite,
                date=request.date,
                cause=request.cause,
                duree_min=request.duree_min)

                session.run("""
                MATCH (i:Incident {id: $id})
                MATCH (e {id: $equipment_id})
                CREATE (i)-[:AFFECTE]->(e)
                """, 
                id=request.id,
                equipment_id=request.equipment_id)
            driver.close()
            return {"message": "Incident créé avec succès"}
        except Exception as e:
            logger.error(f"❌ Erreur création incident automatique: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    # ========================================================

    # ========================================================
    # ROUTES IOT SETTINGS
    # ========================================================
    @app.get("/api/settings/iot")
    async def get_iot_settings():
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                result = session.run("MATCH (s:IoTSettings) RETURN s")
                record = result.single()
            driver.close()
            
            if record:
                return dict(record["s"])
            else:
                return {
                    "mqtt_broker": "localhost",
                    "mqtt_port": 1883,
                    "mqtt_topic": "gnl/+/sensors",
                    "neo4j_label": "SensorData",
                    "alert_threshold_temperature": 80,
                    "alert_threshold_pression": 20
                }
        except Exception as e:
            logger.warning(f"⚠️ Impossible de lire les paramètres IoT: {e}")
            return {}

    @app.post("/api/settings/iot")
    async def save_iot_settings(request: IoTSettingsRequest):
        try:
            driver = GraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
            with driver.session() as session:
                session.run("""
                MERGE (s:IoTSettings)
                SET s.mqtt_broker = $mqtt_broker,
                    s.mqtt_port = $mqtt_port,
                    s.mqtt_topic = $mqtt_topic,
                    s.neo4j_label = $neo4j_label,
                    s.alert_threshold_temperature = $alert_threshold_temperature,
                    s.alert_threshold_pression = $alert_threshold_pression
                """, 
                mqtt_broker=request.mqtt_broker,
                mqtt_port=request.mqtt_port,
                mqtt_topic=request.mqtt_topic,
                neo4j_label=request.neo4j_label,
                alert_threshold_temperature=request.alert_threshold_temperature,
                alert_threshold_pression=request.alert_threshold_pression)
            driver.close()
            return {"message": "Configuration enregistrée avec succès"}
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement des paramètres IoT: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    # ========================================================

    # ========================================================
    # ROUTES ADMIN IMPORT & EXPORT
    # ========================================================
    @app.post("/api/admin/import")
    async def import_data_file(file: UploadFile = File(...)):
        try:
            import os
            import shutil
            
            raw_dir = os.path.join(os.path.dirname(__file__), '../../data/raw')
            os.makedirs(raw_dir, exist_ok=True)
            
            file_path = os.path.join(raw_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"✅ Fichier {file.filename} sauvegardé dans {raw_dir}")
            
            return {"success": True, "filename": file.filename, "importedCount": 0}
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'import: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    # ========================================================

    # ========================================================
    # ROUTE POUR SIMULER UN CAPTEUR IOT (DEPUIS L'INTERFACE)
    # ========================================================
    @app.post("/api/iot/simulate")
    async def simulate_sensor(sensor_data: dict = Body(...)):
        try:
            import paho.mqtt.client as mqtt
            import json
            
            equipment_id = sensor_data.get('equipment_id')
            temperature = sensor_data.get('temperature')
            pression = sensor_data.get('pression')
            
            if not equipment_id:
                raise HTTPException(status_code=400, detail="L'ID de l'équipement est requis")
            
            payload = {
                "temperature": temperature,
                "pression": pression
            }
            
            client = mqtt.Client()
            client.connect("localhost", 1883, 60)
            client.publish(f"gnl/{equipment_id}/sensors", json.dumps(payload))
            client.disconnect()
            
            logger.info(f"📤 Donnée de test envoyée pour {equipment_id}")
            return {"message": "Donnée de test envoyée avec succès"}
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'envoi de la donnée de test: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    # ========================================================

    # ========================================================
    # ENDPOINTS IA (Diagnostic, Logistics, Maintenance)
    # ========================================================
    @app.post("/api/agents/diagnostic")
    async def diagnostic_agent_endpoint(request: AgentRequest):
        try:
            from ..agents.agents.diagnostic_agent import DiagnosticAgent
            agent = DiagnosticAgent()
            return agent.execute(request.query, request.params)
        except Exception as e:
            logger.error(f"❌ Erreur agent diagnostic: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/agents/logistics")
    async def logistics_agent_endpoint(request: AgentRequest):
        try:
            from ..agents.agents.logistics_agent import LogisticsAgent
            agent = LogisticsAgent()
            return agent.execute(request.query, request.params)
        except Exception as e:
            logger.error(f"❌ Erreur agent logistics: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/agents/maintenance")
    async def maintenance_agent_endpoint(request: AgentRequest):
        try:
            from ..agents.agents.maintenance_agent import MaintenanceAgent
            agent = MaintenanceAgent()
            return agent.execute(request.query, request.params)
        except Exception as e:
            logger.error(f"❌ Erreur agent maintenance: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    # ========================================================

    # Inclure les autres routers standards
    app.include_router(
        health.router,
        prefix="/api/health",
        tags=["health"]
    )
    
    app.include_router(
        graph.router,
        prefix="/api/graph",
        tags=["graph"]
    )
    
    app.include_router(
        agents.router,
        prefix="/api/agents",
        tags=["agents"]
    )
    
    app.include_router(
        queries.router,
        prefix="/api/queries",
        tags=["queries"]
    )

    # Endpoint racine
    @app.get("/")
    async def root():
        return {
            "message": "GNL Knowledge Graph API",
            "version": "1.0.0",
            "docs": "/api/docs",
            "health": "/api/health"
        }
    
    app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

    return app

# Application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
