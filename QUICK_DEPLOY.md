# 🚀 Déploiement Rapide - Vercel

## ✅ Fichiers de configuration créés

Les fichiers suivants ont été ajoutés pour permettre le déploiement sur Vercel :

- ✅ `vercel.json` - Configuration principale Vercel
- ✅ `api/vcsky.py` - Fonction serverless pour proxy vcsky
- ✅ `api/vcbr.py` - Fonction serverless pour proxy vcbr
- ✅ `.vercelignore` - Fichiers exclus du déploiement
- ✅ `package.json` - Métadonnées du projet
- ✅ `TROUBLESHOOTING.md` - Guide de résolution de problèmes

## 📦 Déploiement maintenant

### Méthode 1 : Push vers GitHub (Recommandé)

```bash
# 1. Ajoutez les nouveaux fichiers
git add .

# 2. Créez un commit
git commit -m "feat: add Vercel deployment configuration"

# 3. Pushez vers GitHub
git push origin cursor/vercel-deployment-https-error-5192
```

**Ensuite sur Vercel** :
1. Allez sur https://vercel.com/dashboard
2. Votre projet "vicecity-omega" détectera automatiquement les changements
3. Attendez la fin du déploiement (environ 2-3 minutes)
4. Testez sur https://vicecity-omega.vercel.app/

### Méthode 2 : Redéploiement manuel

Si vous êtes déjà connecté à Vercel :

1. Allez sur votre dashboard Vercel
2. Trouvez le projet "vicecity-omega"
3. Cliquez sur "Redeploy"
4. Attendez la fin du déploiement

## 🔍 Vérification

Une fois déployé, vérifiez que :

1. ✅ La page d'accueil se charge sans erreur 404
2. ✅ Le bouton "Click to play" est visible
3. ✅ La console du navigateur ne montre pas d'erreurs CORS
4. ✅ Les fichiers `.js` et `.wasm` se chargent correctement

## 🐛 En cas d'erreur

### Erreur 404 sur tous les fichiers
**Cause** : Routes mal configurées  
**Solution** : Vérifiez que votre projet pointe bien vers la branche avec les nouveaux fichiers

### Erreur "Application Error"
**Cause** : Problème avec les fonctions serverless  
**Solution** : 
1. Allez dans "Settings" → "Functions" sur Vercel
2. Vérifiez que Python Runtime est activé
3. Consultez les logs dans "Deployments" → cliquez sur votre déploiement → "Functions"

### Erreur CORS / SharedArrayBuffer
**Cause** : Headers manquants  
**Solution** : Déjà résolu dans `vercel.json`, attendez le redéploiement complet

### Le jeu ne démarre pas
**Cause** : Fichiers .wasm ou .data manquants  
**Solution** : Vérifiez que tous les fichiers du dossier `dist/` sont bien présents dans votre repo

## 📊 Vérifier les logs

Pour voir les logs détaillés :

1. Allez sur https://vercel.com/dashboard
2. Cliquez sur votre projet
3. Cliquez sur "Deployments"
4. Cliquez sur le dernier déploiement
5. Consultez les onglets :
   - **Build Logs** - Logs de construction
   - **Functions** - Logs des fonctions serverless
   - **Runtime Logs** - Logs d'exécution

## 💡 Conseils

### Pour de meilleures performances :
- Les fichiers statiques sont automatiquement mis en cache par le CDN Vercel
- Les proxies Python peuvent avoir un léger délai lors du premier appel (cold start)
- Considérez Railway.app si vous avez besoin de plus de contrôle

### Limitations à connaître :
- ⏱️ Timeout de 10 secondes pour les fonctions (gratuit)
- 💾 Pas de système de fichiers persistant (pas de saves locaux)
- 🔄 Les fonctions Python peuvent avoir un "cold start" de 1-2 secondes

## ✅ Checklist finale

Avant de merger la PR :

- [ ] Tous les fichiers ont été ajoutés au git
- [ ] Le commit a été créé
- [ ] Le push vers GitHub a réussi
- [ ] Le déploiement Vercel est terminé sans erreur
- [ ] Le site https://vicecity-omega.vercel.app/ fonctionne
- [ ] Le jeu se charge et démarre correctement
- [ ] Pas d'erreurs dans la console du navigateur

---

**Besoin d'aide ?** Consultez `TROUBLESHOOTING.md` pour plus de détails.
