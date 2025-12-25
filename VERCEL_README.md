[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/VOTRE_USERNAME/VOTRE_REPO)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Vercel Status](https://img.shields.io/badge/vercel-ready-brightgreen.svg)](https://vercel.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

# 🎮 GTA Vice City - Déploiement Vercel

> ✅ **Statut** : Configuration Vercel complète et prête à déployer

## 📋 Récapitulatif

Ce repository contient maintenant tout le nécessaire pour déployer GTA Vice City (version HTML5/WASM) sur **Vercel**.

### 🆕 Fichiers de configuration ajoutés

| Fichier | Description | Statut |
|---------|-------------|--------|
| `vercel.json` | Configuration principale Vercel | ✅ |
| `api/vcsky.py` | Fonction serverless proxy vcsky | ✅ |
| `api/vcbr.py` | Fonction serverless proxy vcbr | ✅ |
| `.vercelignore` | Fichiers exclus du build | ✅ |
| `package.json` | Métadonnées du projet | ✅ |

### 📚 Documentation ajoutée

| Document | Contenu |
|----------|---------|
| `SUMMARY.md` | ✅ Résumé complet de la configuration |
| `QUICK_DEPLOY.md` | 🚀 Guide de déploiement rapide (3 min) |
| `TROUBLESHOOTING.md` | 🐛 Guide de dépannage complet |
| `README_VERCEL.md` | 📖 Documentation technique détaillée |
| `VERCEL_DEPLOY.md` | 🔧 Instructions de déploiement |

## 🚀 Déploiement en 3 étapes

### 1️⃣ Commitez les fichiers

```bash
git add .
git commit -m "feat: add Vercel deployment configuration"
git push
```

### 2️⃣ Déployez sur Vercel

**Option A : Bouton de déploiement**
1. Cliquez sur le bouton "Deploy with Vercel" en haut
2. Connectez votre compte GitHub
3. Sélectionnez votre repository

**Option B : Dashboard Vercel**
1. Allez sur https://vercel.com/dashboard
2. Importez votre projet GitHub
3. Vercel détectera automatiquement `vercel.json`

### 3️⃣ Testez votre site

Visitez votre URL Vercel (ex: `https://vicecity-omega.vercel.app/`)

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────┐
│           VERCEL CDN (Global Edge Network)        │
├───────────────────────────────────────────────────┤
│                                                   │
│  📄 Fichiers statiques (/dist/)                   │
│  ├─ index.html                                    │
│  ├─ game.js                                       │
│  ├─ modules/*.js                                  │
│  └─ *.wasm, *.mp4, etc.                           │
│                                                   │
│  🔄 Proxies serverless (Python)                   │
│  ├─ /vcsky/* ──▶ api/vcsky.py ──▶ cdn.dos.zone   │
│  └─ /vcbr/*  ──▶ api/vcbr.py  ──▶ br.cdn.dos.zone│
│                                                   │
│  🛡️ Headers automatiques                          │
│  ├─ Cross-Origin-Opener-Policy: same-origin      │
│  ├─ Cross-Origin-Embedder-Policy: require-corp   │
│  └─ Access-Control-Allow-Origin: *               │
└───────────────────────────────────────────────────┘
```

## ✅ Fonctionnalités

| Fonctionnalité | Vercel | Python Local |
|----------------|--------|--------------|
| Fichiers statiques | ✅ | ✅ |
| Proxy CDN vcsky | ✅ | ✅ |
| Proxy CDN vcbr | ✅ | ✅ |
| Headers CORS | ✅ | ✅ |
| CDN global | ✅ | ❌ |
| HTTPS auto | ✅ | ❌ |
| Saves locaux | ❌ | ✅ |
| Cache local | ❌ | ✅ |
| Auth HTTP Basic | ❌* | ✅ |

*Disponible uniquement sur Vercel Pro

## ⚠️ Limitations

### Vercel Free Tier
- ⏱️ Timeout : 10 secondes par fonction
- 💾 Pas de stockage persistant (pas de saves locaux)
- 🔄 Cold start possible (~1-2s)

### Solutions alternatives

Si vous avez besoin de fonctionnalités avancées :

| Plateforme | Avantages | Prix |
|------------|-----------|------|
| **Railway.app** ⭐ | Python complet, pas de timeout strict | $5/mois crédit gratuit |
| **Render.com** | Support Docker et Python | Gratuit avec limites |
| **Fly.io** | Support Docker, edge computing | Gratuit (3 VMs) |
| **DigitalOcean** | Contrôle total, scaling | À partir de $5/mois |

## 📖 Documentation

- [`SUMMARY.md`](SUMMARY.md) - Résumé complet ✅
- [`QUICK_DEPLOY.md`](QUICK_DEPLOY.md) - Déploiement rapide 🚀
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) - Résolution de problèmes 🐛
- [`README_VERCEL.md`](README_VERCEL.md) - Documentation technique 📚
- [`VERCEL_DEPLOY.md`](VERCEL_DEPLOY.md) - Guide détaillé 🔧

## 🆘 Support

### Problèmes courants

#### Erreur 404 après déploiement
**Solution** : Vérifiez que tous les fichiers de `/dist/` sont dans votre repository

#### Erreur CORS / SharedArrayBuffer
**Solution** : Headers déjà configurés dans `vercel.json`, forcez un redéploiement

#### Fonction timeout
**Solution** : Passez à Vercel Pro ou utilisez Railway.app

### Consulter les logs

1. Dashboard Vercel → votre projet
2. Onglet "Deployments"
3. Cliquez sur le dernier déploiement
4. Consultez "Build Logs" et "Functions"

## 🎯 Checklist de déploiement

- [ ] Tous les fichiers sont committés
- [ ] Le push vers GitHub a réussi
- [ ] Le projet est importé dans Vercel
- [ ] Le build Vercel s'est terminé sans erreur
- [ ] Le site se charge sur l'URL Vercel
- [ ] Le bouton "Click to play" fonctionne
- [ ] Le jeu démarre correctement
- [ ] Pas d'erreur dans la console (F12)

## 🎮 Résultat attendu

Après un déploiement réussi :

1. ✅ Page d'accueil s'affiche instantanément
2. ✅ Cover du jeu visible
3. ✅ Bouton "Click to play" cliquable
4. ✅ Vidéo intro se charge
5. ✅ Barre de progression s'affiche
6. ✅ Jeu démarre en WebAssembly

## 📊 Performance

| Métrique | Valeur attendue |
|----------|-----------------|
| First Contentful Paint | < 1s |
| Time to Interactive | < 3s |
| Asset loading | Progressif via CDN |
| Cold start (fonctions) | ~1-2s |

## 🔗 Liens utiles

- [Documentation Vercel](https://vercel.com/docs)
- [Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Configuration vercel.json](https://vercel.com/docs/projects/project-configuration)
- [Headers CORS](https://vercel.com/docs/edge-network/headers)

## 📝 Changelog

### Version 1.0.0 (25 décembre 2024)
- ✅ Ajout configuration Vercel complète
- ✅ Création des fonctions serverless Python
- ✅ Configuration des headers CORS
- ✅ Documentation complète
- ✅ Guides de déploiement et troubleshooting

## 🙏 Crédits

- **Projet original** : DOS Zone ([@specialist003](https://github.com/okhmanyuk-ev), [@caiiiycuk](https://www.youtube.com/caiiiycuk), [@SerGen](https://t.me/ser_var))
- **Déobfuscation** : [@Lolendor](https://github.com/Lolendor)
- **Traduction russe** : [GamesVoice](https://www.gamesvoice.ru/)
- **Support PHP** : [Rohamgames](https://github.com/Rohamgames)
- **Configuration Vercel** : Ce repository

## 📄 Licence

Do what you want. Non affilié à Rockstar Games.

---

<div align="center">

**🎮 Prêt à jouer ? Déployez maintenant !**

[![Deploy Now](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/VOTRE_USERNAME/VOTRE_REPO)

*Remplacez `VOTRE_USERNAME/VOTRE_REPO` par votre repository GitHub*

</div>
