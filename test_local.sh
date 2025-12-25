#!/bin/bash
# Test local du serveur avant déploiement Vercel

echo "🧪 Test du serveur local..."
echo ""

# Démarrer le serveur en arrière-plan
echo "▶️  Démarrage du serveur sur http://localhost:8000"
python3 server.py --port 8000 > /tmp/server.log 2>&1 &
SERVER_PID=$!

# Attendre que le serveur démarre
sleep 3

echo ""
echo "✅ Serveur démarré (PID: $SERVER_PID)"
echo ""

# Test 1: Page d'accueil
echo "1️⃣  Test de la page d'accueil..."
if curl -s http://localhost:8000/ | grep -q "Vice City"; then
    echo "   ✅ Page d'accueil OK"
else
    echo "   ❌ Page d'accueil ERREUR"
fi

# Test 2: Fichier JS
echo "2️⃣  Test des fichiers JavaScript..."
if curl -s http://localhost:8000/game.js | head -1 | grep -q "const"; then
    echo "   ✅ Fichiers JS OK"
else
    echo "   ❌ Fichiers JS ERREUR"
fi

# Test 3: Proxy vcbr (fichier WASM)
echo "3️⃣  Test du proxy /vcbr/ (fichier WASM)..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/vcbr/vc-sky-en-v6.wasm.br)
if [ "$STATUS" = "200" ]; then
    echo "   ✅ Proxy WASM OK (Status: $STATUS)"
else
    echo "   ❌ Proxy WASM ERREUR (Status: $STATUS)"
fi

# Test 4: Headers CORS
echo "4️⃣  Test des headers CORS..."
CORS=$(curl -s -I http://localhost:8000/ | grep -i "cross-origin")
if [ ! -z "$CORS" ]; then
    echo "   ✅ Headers CORS OK"
else
    echo "   ❌ Headers CORS MANQUANTS"
fi

echo ""
echo "📋 Résumé:"
echo "   URL: http://localhost:8000/"
echo "   Logs: tail -f /tmp/server.log"
echo ""
echo "🛑 Pour arrêter le serveur:"
echo "   kill $SERVER_PID"
echo ""
echo "🌐 Ouvrez http://localhost:8000/ dans votre navigateur pour tester le jeu"
echo ""
