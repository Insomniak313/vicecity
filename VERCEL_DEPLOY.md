# Déploiement sur Vercel

## Configuration effectuée

Le projet a été configuré pour fonctionner sur Vercel avec les modifications suivantes :

### Fichiers ajoutés :
1. **`vercel.json`** - Configuration du déploiement Vercel
2. **`api/vcsky.py`** - Fonction serverless pour proxy vcsky
3. **`api/vcbr.py`** - Fonction serverless pour proxy vcbr
4. **`.vercelignore`** - Fichiers à exclure du déploiement

## Comment déployer

### Option 1 : Via l'interface Vercel (Recommandé)

1. Allez sur [vercel.com](https://vercel.com)
2. Connectez votre compte GitHub
3. Cliquez sur "Import Project"
4. Sélectionnez votre repository GitHub
5. Vercel détectera automatiquement la configuration via `vercel.json`
6. Cliquez sur "Deploy"

### Option 2 : Via la CLI Vercel

```bash
# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Déployer depuis le dossier du projet
vercel

# Pour un déploiement en production
vercel --prod
```

## Architecture sur Vercel

- **`/dist/`** → Fichiers statiques servis directement
- **`/vcsky/*`** → Proxifié via la fonction serverless `api/vcsky.py` vers `https://cdn.dos.zone/vcsky/`
- **`/vcbr/*`** → Proxifié via la fonction serverless `api/vcbr.py` vers `https://br.cdn.dos.zone/vcsky/`

## Headers CORS configurés

Les headers suivants sont automatiquement ajoutés :
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Embedder-Policy: require-corp`
- `Access-Control-Allow-Origin: *`

## Limitations sur Vercel

⚠️ **Attention** : Vercel a des limitations pour les fonctions serverless :
- **Timeout** : 10 secondes (plan gratuit) / 60 secondes (plan pro)
- **Taille maximale** : 50MB par fonction
- **Pas de sauvegarde locale** : Les fonctionnalités `--custom_saves` ne fonctionneront pas

## Alternative recommandée

Si vous avez besoin de fonctionnalités avancées (saves locaux, cache, etc.), considérez ces alternatives :
- **Railway.app** - Supporte Python/FastAPI
- **Render.com** - Supporte Python/FastAPI
- **Fly.io** - Supporte Docker
- **DigitalOcean App Platform** - Supporte Docker

## Support

Pour plus d'informations, consultez :
- [Documentation Vercel](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
