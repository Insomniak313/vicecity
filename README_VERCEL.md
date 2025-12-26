# 🎮 GTA Vice City - Configuration Vercel

## 📋 Résumé des modifications

Ce projet a été configuré pour fonctionner sur **Vercel** avec les adaptations suivantes :

### 🆕 Fichiers ajoutés

| Fichier | Description |
|---------|-------------|
| `vercel.json` | Configuration principale de Vercel (routes, headers, builds) |
| `api/vcsky.py` | Fonction serverless Python pour proxy des assets vcsky |
| `api/vcbr.py` | Fonction serverless Python pour proxy des assets vcbr |
| `.vercelignore` | Fichiers à exclure du déploiement |
| `package.json` | Métadonnées du projet pour Vercel |
| `QUICK_DEPLOY.md` | Guide de déploiement rapide |
| `TROUBLESHOOTING.md` | Guide de résolution de problèmes détaillé |
| `VERCEL_DEPLOY.md` | Documentation complète du déploiement Vercel |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      VERCEL CDN                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │   /dist/*    │     │ /vcsky/*     │     │  /vcbr/*   │ │
│  │  (Statique)  │     │ (Serverless) │     │(Serverless)│ │
│  │              │     │              │     │            │ │
│  │  - index.html│────▶│ api/vcsky.py │────▶│cdn.dos.zone│ │
│  │  - *.js      │     │              │     │            │ │
│  │  - *.wasm    │     └──────────────┘     │            │ │
│  │  - *.mp4     │                          │            │ │
│  │  - modules/  │     ┌──────────────┐     │            │ │
│  └──────────────┘     │ api/vcbr.py  │────▶│br.cdn.dos  │ │
│                       │              │     │  .zone     │ │
│                       └──────────────┘     └────────────┘ │
│                                                             │
│  Headers automatiques sur toutes les routes :              │
│  • Cross-Origin-Opener-Policy: same-origin                 │
│  • Cross-Origin-Embedder-Policy: require-corp              │
│  • Access-Control-Allow-Origin: *                          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Déploiement

### Prérequis
- Compte GitHub
- Compte Vercel (gratuit) lié à GitHub
- Repository contenant ce code

### Étapes

1. **Commitez les fichiers de configuration** :
   ```bash
   git add .
   git commit -m "feat: add Vercel configuration"
   git push
   ```

2. **Vercel détectera automatiquement le déploiement** ou allez sur :
   - https://vercel.com/dashboard
   - Sélectionnez votre projet
   - Attendez la fin du build

3. **Testez votre site** :
   - Visitez votre URL Vercel (ex: `https://vicecity-omega.vercel.app/`)

## ⚙️ Configuration technique

### Routes configurées

| Route | Destination | Type |
|-------|-------------|------|
| `/` | `/dist/index.html` | Fichier statique |
| `/*.js` | `/dist/*.js` | Fichier statique |
| `/*.wasm` | `/dist/*.wasm` | Fichier statique |
| `/modules/*` | `/dist/modules/*` | Fichier statique (avec cache) |
| `/vcsky/*` | `api/vcsky.py` → CDN | Serverless proxy |
| `/vcbr/*` | `api/vcbr.py` → CDN | Serverless proxy |

### Headers CORS

Tous les fichiers servis incluent automatiquement :
```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Access-Control-Allow-Origin: *
```

Ces headers sont **obligatoires** pour :
- Utiliser `SharedArrayBuffer` (nécessaire pour WebAssembly multithreading)
- Charger les modules WASM correctement
- Éviter les erreurs CORS

### Types MIME forcés

| Extension | Content-Type |
|-----------|--------------|
| `.wasm` | `application/wasm` |
| `.js` | `application/javascript` |
| `.br` | `Content-Encoding: br` |

## 🔧 Fonctions serverless

### `api/vcsky.py`
Proxie les requêtes vers `https://cdn.dos.zone/vcsky/`

**Exemple** :
- Request: `https://votre-site.vercel.app/vcsky/data/gta3.img`
- Proxied to: `https://cdn.dos.zone/vcsky/data/gta3.img`

### `api/vcbr.py`
Proxie les requêtes vers `https://br.cdn.dos.zone/vcsky/`

**Exemple** :
- Request: `https://votre-site.vercel.app/vcbr/vc-sky-en-v6.wasm.br`
- Proxied to: `https://br.cdn.dos.zone/vcsky/vc-sky-en-v6.wasm.br`

## ⚠️ Limitations Vercel

| Limitation | Valeur | Impact |
|------------|--------|--------|
| **Timeout fonction** | 10s (gratuit) / 60s (pro) | Fichiers très volumineux peuvent timeout |
| **Taille max fonction** | 50MB | OK pour les proxies |
| **Stockage persistant** | ❌ Non disponible | Pas de saves locaux |
| **WebSocket** | Limité | Pas critique pour ce projet |

## 🧰 Vercel KV (recommandé) — RTC / Multijoueur P2P

Ce projet inclut un “signaling” WebRTC via `api/rtc.py` utilisé par `dist/p2p-webrtc.js` (endpoints `/api/rtc/*`).
Pour qu’il fonctionne, vous devez connecter **Vercel KV** au projet afin que Vercel injecte les variables d’environnement KV.

### Étapes (Dashboard Vercel)

1. **Storage → KV → Create**
2. **Connect** le store KV à votre projet
3. Vérifiez dans **Project → Settings → Environment Variables** que vous avez (au moins) :
   - `KV_REST_API_URL`
   - `KV_REST_API_TOKEN`
4. **Redeploy** (les env vars ne sont prises en compte qu’après un déploiement)

### Variables supportées

- **Vercel KV (officiel)**: `KV_REST_API_URL`, `KV_REST_API_TOKEN` (et optionnellement `KV_REST_API_READ_ONLY_TOKEN`)
- **Upstash direct** (fallback): `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`

### Test rapide

- Ouvrez la page, puis cliquez **“Créer une salle”** (UI multijoueur).
- Si KV n’est pas configuré, les endpoints `/api/rtc/*` répondront `501` avec un message d’aide.

## 🆚 Comparaison avec le serveur Python original

| Fonctionnalité | Python (server.py) | Vercel |
|----------------|-------------------|--------|
| Fichiers statiques | ✅ | ✅ |
| Proxy vcsky | ✅ | ✅ |
| Proxy vcbr | ✅ | ✅ |
| Headers CORS | ✅ | ✅ |
| Saves locaux (`--custom_saves`) | ✅ | ❌ |
| Cache local (`--vcsky_cache`) | ✅ | ❌ |
| HTTP Basic Auth | ✅ | ❌ (sauf Vercel Pro) |
| Fichiers locaux offline | ✅ | ❌ |

## 💡 Recommandations

### Utilisez Vercel si :
- ✅ Vous voulez un déploiement simple et gratuit
- ✅ Vous n'avez pas besoin de saves locaux
- ✅ Vous voulez un CDN global performant
- ✅ Vous préférez l'intégration Git automatique

### Utilisez un autre hébergeur si :
- ❌ Vous avez besoin de saves locaux persistants
- ❌ Vous voulez un contrôle total sur le backend
- ❌ Vous avez besoin de fonctions longues (> 10s)
- ❌ Vous voulez servir tous les assets localement

**Alternatives recommandées** :
- **Railway.app** - Support Python complet
- **Render.com** - Support Docker
- **Fly.io** - Support Docker avec edge locations
- **DigitalOcean App Platform** - Support Docker

## 🐛 Debug

### Problèmes courants

#### 1. Erreur 404 sur les fichiers
**Diagnostic** :
```bash
# Vérifiez que les fichiers existent dans dist/
ls -la dist/
ls -la dist/modules/
```

**Solution** : Assurez-vous que tous les fichiers sont bien commités dans Git

#### 2. Erreur CORS
**Diagnostic** : Ouvrez la console du navigateur (F12)

**Solution** : Les headers sont déjà configurés, forcez un redéploiement

#### 3. Fonction serverless timeout
**Diagnostic** : Consultez les logs Vercel

**Solution** : Passez à Vercel Pro ou utilisez Railway.app

### Consulter les logs

```bash
# Via CLI Vercel
vercel logs vicecity-omega --follow

# Ou sur le dashboard
# https://vercel.com/dashboard → projet → Deployments → dernier build
```

## 📚 Documentation

- [Vercel Documentation](https://vercel.com/docs)
- [Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Configuration (vercel.json)](https://vercel.com/docs/projects/project-configuration)
- [Headers](https://vercel.com/docs/edge-network/headers)

## 🎯 Prochaines étapes

1. ✅ Commitez et pushez les fichiers de configuration
2. ✅ Attendez le déploiement automatique sur Vercel
3. ✅ Testez le site en production
4. ✅ Vérifiez les logs si des erreurs apparaissent
5. ✅ Profitez du jeu ! 🎮

---

**Créé pour** : Résoudre l'erreur HTTPS sur https://vicecity-omega.vercel.app/

**Date** : Décembre 2024

**Auteur** : Configuration automatique via Cursor AI
