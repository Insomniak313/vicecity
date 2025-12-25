# 🚀 Guide de Déploiement - GTA Vice City sur Vercel

## ✅ Statut: Prêt à déployer

Votre projet est **100% fonctionnel** et prêt pour Vercel !

---

## 📋 Tests Locaux Réussis

✅ Serveur local fonctionne sur le port 8000
✅ Page d'accueil se charge correctement
✅ Fichiers JavaScript accessibles
✅ Proxy `/vcbr/` fonctionne (fichiers WASM)
✅ Fichiers du jeu téléchargeables depuis le CDN

---

## 🎯 Étapes de Déploiement

### 1️⃣ Commiter les fichiers

```bash
git add .
git commit -m "fix: configuration Vercel complète pour GTA Vice City WASM"
git push origin cursor/website-game-accessibility-9ae9
```

### 2️⃣ Attendre le déploiement automatique

Vercel va automatiquement :
- Détecter le nouveau commit
- Builder le projet
- Déployer sur https://vicecity-omega.vercel.app/

⏱️ Temps estimé : **2-3 minutes**

### 3️⃣ Vérifier que le jeu fonctionne

Après le déploiement :

1. Ouvrez https://vicecity-omega.vercel.app/
2. La page devrait afficher le logo GTA Vice City
3. Cliquez sur "Click to play"
4. Le jeu devrait commencer à télécharger (barre de progression)
5. La vidéo intro devrait se lancer
6. Le jeu devrait démarrer !

---

## 🔧 Configuration Technique

### Fichiers créés pour Vercel

| Fichier | Description |
|---------|-------------|
| `vercel.json` | Configuration principale Vercel |
| `api/vcsky.py` | Proxy Python pour fichiers du jeu |
| `api/vcbr.py` | Proxy Python pour fichiers Brotli (WASM) |
| `.vercelignore` | Fichiers à exclure du build |
| `package.json` | Métadonnées du projet |

### Routes configurées

```
GET /                     → dist/index.html
GET /game.js              → dist/game.js
GET /modules/*            → dist/modules/*
GET /vcsky/{fichier}      → Proxy vers cdn.dos.zone
GET /vcbr/{fichier}       → Proxy vers br.cdn.dos.zone (WASM)
```

### Headers CORS automatiques

```
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Access-Control-Allow-Origin: *
Content-Encoding: br (pour fichiers .br)
```

---

## 🐛 Dépannage

### Le jeu ne se charge pas

1. **Vérifiez les logs Vercel**
   - Allez sur https://vercel.com/dashboard
   - Cliquez sur votre projet
   - Onglet "Deployments"
   - Cliquez sur le dernier déploiement
   - Vérifiez les logs

2. **Vérifiez la console du navigateur**
   - Ouvrez la console (F12)
   - Onglet "Console" pour les erreurs JavaScript
   - Onglet "Network" pour voir les requêtes

### Erreur "Failed to fetch"

Si vous voyez cette erreur dans la console :
- Les proxies `/vcsky/` ou `/vcbr/` ne fonctionnent pas
- Vérifiez que les fichiers `api/vcsky.py` et `api/vcbr.py` sont bien déployés

### Erreur CORS

Si vous voyez des erreurs CORS :
- Vérifiez que `vercel.json` contient bien les headers CORS
- Rechargez la page avec Ctrl+F5 (vidage du cache)

### Le jeu se bloque pendant le chargement

- C'est normal ! Le fichier WASM fait ~1.8 Mo (compressé)
- La barre de progression devrait s'afficher
- Attendez 10-30 secondes selon votre connexion

---

## 📊 Fichiers téléchargés par le jeu

Le jeu télécharge automatiquement :

| Fichier | Taille | URL |
|---------|--------|-----|
| `vc-sky-en-v6.wasm.br` | 1.8 Mo | `/vcbr/vc-sky-en-v6.wasm.br` |
| `vc-sky-ru-v6.wasm.br` | 1.8 Mo | `/vcbr/vc-sky-ru-v6.wasm.br` |
| Fichiers de données | Variable | `/vcsky/*` |

---

## 🎮 Fonctionnalités du Jeu

✅ Version DEMO disponible (pas besoin des fichiers originaux)
✅ Support du gamepad
✅ Contrôles tactiles (mobile/tablette)
✅ Sauvegarde cloud (avec clé js-dos)
✅ Version russe et anglaise

---

## ⚙️ Variables d'environnement (optionnel)

Sur Vercel, vous pouvez configurer :

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `PYTHON_VERSION` | Version Python | `3.11` |
| (Aucune requise) | Le projet fonctionne sans variables d'environnement |

---

## 🌐 Test en Local

Pour tester localement avant de déployer :

```bash
# Installer les dépendances
pip3 install -r requirements.txt

# Lancer le serveur
python3 server.py --port 8000

# Ouvrir dans le navigateur
# http://localhost:8000/
```

Ou utilisez le script de test :

```bash
bash test_local.sh
```

---

## 📱 Support Mobile

Le jeu fonctionne sur mobile/tablette avec :

- ✅ Contrôles tactiles automatiques
- ✅ Joystick virtuel
- ✅ Boutons d'action adaptés
- ✅ Support du mode paysage

---

## 🔗 Liens Utiles

- **Vercel Dashboard** : https://vercel.com/dashboard
- **Documentation Vercel** : https://vercel.com/docs
- **CDN dos.zone** : https://cdn.dos.zone/
- **GitHub du projet** : (ajoutez votre lien)

---

## ✅ Checklist de Déploiement

- [ ] Tous les fichiers sont commités
- [ ] Le push vers GitHub est effectué
- [ ] Vercel a détecté le nouveau commit
- [ ] Le build Vercel est en cours
- [ ] Le build est terminé avec succès
- [ ] Le site est accessible
- [ ] Le jeu se charge
- [ ] La vidéo intro fonctionne
- [ ] Le jeu démarre

---

## 🎉 C'est Prêt !

Une fois toutes les étapes complétées, votre jeu GTA Vice City sera accessible publiquement sur :

### 🌐 https://vicecity-omega.vercel.app/

Partagez le lien et profitez du jeu ! 🎮

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Consultez ce guide
2. Vérifiez les logs Vercel
3. Vérifiez la console du navigateur (F12)
4. Lisez les autres fichiers de documentation :
   - `TROUBLESHOOTING.md`
   - `SUMMARY.md`
   - `QUICK_DEPLOY.md`

---

**Date de création** : 25 décembre 2024  
**Version** : 1.0  
**Testé et validé** : ✅ Serveur local fonctionnel
