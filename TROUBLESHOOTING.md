# 🔧 Guide de résolution - Erreur HTTPS Vercel

## ⚠️ Problème actuel

Votre site `https://vicecity-omega.vercel.app/` rencontre probablement l'une de ces erreurs :
- Page blanche / Erreur 404
- "Application Error" 
- Erreur de chargement des ressources
- Problème de CORS

## 🔍 Diagnostic

### Causes identifiées :

1. **Vercel ne supporte pas PHP natif** 
   - Votre `index.php` ne peut pas être exécuté tel quel sur Vercel

2. **Configuration manquante**
   - Aucun `vercel.json` n'existait pour indiquer à Vercel comment servir votre application

3. **Headers CORS manquants**
   - Les headers `Cross-Origin-Opener-Policy` et `Cross-Origin-Embedder-Policy` sont critiques pour WebAssembly

## ✅ Solution implémentée

J'ai créé les fichiers suivants :

### 1. `vercel.json` - Configuration de déploiement
Configure Vercel pour :
- Servir les fichiers statiques depuis `/dist/`
- Router les requêtes proxy via des fonctions serverless Python
- Ajouter automatiquement les headers CORS nécessaires

### 2. `api/vcsky.py` - Proxy serverless pour vcsky
Fonction serverless Python qui proxifie les requêtes vers `https://cdn.dos.zone/vcsky/`

### 3. `api/vcbr.py` - Proxy serverless pour vcbr  
Fonction serverless Python qui proxifie les requêtes vers `https://br.cdn.dos.zone/vcsky/`

### 4. `.vercelignore` - Fichiers exclus
Empêche le déploiement de fichiers inutiles (Python backend, Docker, etc.)

## 📋 Prochaines étapes

### Pour déployer sur Vercel :

1. **Commitez les changements** :
   ```bash
   git add .
   git commit -m "Add Vercel configuration and serverless functions"
   git push
   ```

2. **Redéployez sur Vercel** :
   - Allez sur [vercel.com/dashboard](https://vercel.com/dashboard)
   - Trouvez votre projet "vicecity-omega"
   - Cliquez sur "Redeploy" ou attendez le déploiement automatique du nouveau commit

3. **Testez votre site** :
   - Visitez `https://vicecity-omega.vercel.app/`
   - Vérifiez que le jeu se charge correctement

## 🔍 Debug si ça ne fonctionne toujours pas

### Vérifier les logs Vercel :
1. Allez sur votre projet dans le dashboard Vercel
2. Cliquez sur l'onglet "Deployments"
3. Cliquez sur le dernier déploiement
4. Consultez les logs dans l'onglet "Functions" et "Build Logs"

### Erreurs communes et solutions :

#### Erreur : "Application Error"
**Cause** : Timeout des fonctions serverless  
**Solution** : Vercel limite les fonctions à 10s (gratuit) / 60s (pro)

#### Erreur : “signaling indisponible” / `/api/rtc/*` renvoie `501`
**Cause** : **Vercel KV** non configuré (variables d’environnement manquantes).  
**Solution** :

1. Dans Vercel: **Storage → KV** → créez (ou sélectionnez) un store
2. **Connect** le store KV à votre projet
3. Vérifiez dans **Project → Settings → Environment Variables** la présence de :
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`
4. **Redeploy** le projet (obligatoire pour appliquer les env vars)

✅ **Alternative si KV est payant** : utilisez Upstash directement
- Ajoutez `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` dans les env vars Vercel
- Redeploy

#### Erreur : `/token/get` ou `/saves/*` renvoie `501`
**Cause** : **Vercel Blob** non configuré (token manquant).  
**Solution** :
- Ajoutez `BLOB_READ_WRITE_TOKEN` (et optionnellement `BLOB_READ_ONLY_TOKEN`) dans les env vars du projet
- Redeploy

#### Erreur : 404 sur les fichiers statiques
**Cause** : Chemins incorrects dans `vercel.json`  
**Solution** : Vérifiez que tous vos fichiers sont bien dans `/dist/`

#### Erreur : CORS / SharedArrayBuffer
**Cause** : Headers manquants  
**Solution** : Les headers sont déjà configurés dans `vercel.json`, attendez le redéploiement

## 🚀 Alternatives recommandées

Si Vercel ne convient pas à vos besoins (saves locaux, timeouts, etc.), considérez :

### 1. Railway.app ⭐ (Recommandé)
- **Avantages** : Support Python/FastAPI natif, pas de timeout strict
- **Prix** : Gratuit avec $5/mois de crédit
- **Déploiement** : 
  ```bash
  railway login
  railway init
  railway up
  ```

### 2. Render.com
- **Avantages** : Support Docker et Python
- **Prix** : Gratuit avec limitations
- **Déploiement** : Via l'interface web

### 3. Fly.io
- **Avantages** : Support Docker complet
- **Prix** : Gratuit jusqu'à 3 VMs
- **Déploiement** : 
  ```bash
  flyctl launch
  flyctl deploy
  ```

### 4. DigitalOcean App Platform
- **Avantages** : Support Docker, FastAPI, scaling
- **Prix** : ~$5/mois
- **Déploiement** : Via l'interface web

## 📝 Notes importantes

### Limitations Vercel :
- ❌ Pas de saves locaux (système de fichiers éphémère)
- ❌ Timeout de 10s pour les fonctions gratuites
- ❌ Pas de WebSocket persistant
- ✅ CDN global performant
- ✅ HTTPS automatique
- ✅ Déploiement continu depuis Git

### Pour utiliser toutes les fonctionnalités :
Si vous avez besoin de :
- Saves locaux (`--custom_saves`)
- Cache local (`--vcsky_cache`, `--vcbr_cache`)
- Contrôle total sur le backend

→ Utilisez **Railway.app** ou **Render.com** avec le fichier `server.py` original

## 📞 Support

Si vous rencontrez toujours des problèmes :
1. Vérifiez les logs Vercel
2. Testez en local avec `python server.py`
3. Comparez avec le README.md original du projet

## 🎮 Test final

Une fois déployé, testez :
1. ✅ Page d'accueil charge
2. ✅ Bouton "Click to play" fonctionne
3. ✅ Vidéo intro se charge
4. ✅ Barre de progression apparaît
5. ✅ Jeu démarre

Bonne chance ! 🚀
