document.addEventListener('DOMContentLoaded', function () {
    const panierBtn = document.getElementById('panierDropdown');
    const menuPanier = document.getElementById('panierDropdownMenu');
    const boutonsAjouter = document.querySelectorAll('.ajouter-panier-rapide');

    // 🔁 Récupération du token CSRF
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // 🔢 Mise à jour du badge de panier
    function updateCartCount() {
        fetch('/boutique/panier/count/')
            .then(response => response.json())
            .then(data => {
                const badge = document.getElementById('panier-count');
                badge.textContent = data.count;
                badge.style.display = data.count > 0 ? 'inline' : 'none';
            });
    }

    // 🛒 Rafraîchit le contenu du dropdown panier
    function rafraichirDropdownPanier() {
        fetch('/boutique/panier/dropdown/')
            .then(response => response.json())
            .then(data => {
                menuPanier.innerHTML = '';  // 🔁 Nettoie d'abord

                // ✅ Ajoute toujours le bloc d’alerte
                const alertElement = document.createElement('li');
                alertElement.innerHTML = `
                <div id="panier-alert" class="alert alert-warning d-none mb-2 p-2 small text-center" role="alert"></div>
            `;
                menuPanier.appendChild(alertElement);

                // 🧺 Panier vide ?
                if (data.produits.length === 0) {
                    const emptyItem = document.createElement('li');
                    emptyItem.classList.add('dropdown-item', 'text-muted');
                    emptyItem.textContent = 'Votre panier est vide.';
                    menuPanier.appendChild(emptyItem);
                    return;
                }

                // ✅ Affiche chaque produit
                data.produits.forEach(item => {
                    const li = document.createElement('li');
                    li.classList.add('dropdown-item', 'd-flex', 'justify-content-between', 'align-items-center', 'gap-2');

                    li.innerHTML = `
                    <div class="flex-grow-1">
                        <strong>${item.nom}</strong><br>
                        <small>
                            <button class="btn btn-sm btn-outline-secondary btn-moins" data-id="${item.id}">−</button>
                            ${item.quantite}
                            <button class="btn btn-sm btn-outline-secondary btn-plus" data-id="${item.id}">+</button>
                            × ${item.prix_unitaire.toFixed(2)} €
                        </small>
                    </div>
                    <span>${item.sous_total.toFixed(2)} €</span>
                    <button class="btn btn-sm btn-outline-danger btn-supprimer mt-1 p-1" data-id="${item.id}" title="Supprimer">
                        🗑️
                    </button>
                `;

                    menuPanier.appendChild(li);
                });

                // ➕ Total et bouton commande
                const isAuthenticated = document.body.dataset.auth === "true";
                const urlCommande = isAuthenticated ? "/commande/" : "/comptes/connexion/?next=/commande/";

                menuPanier.insertAdjacentHTML('beforeend', `
                    <li class="dropdown-divider"></li>
                    <li class="dropdown-item text-end"><strong>Total : ${data.total.toFixed(2)} €</strong></li>
                    <li class="dropdown-item text-center mt-2">
                        <button id="btn-commande" class="btn btn-sm btn-custom">Passer la commande</button>
                    </li>
                `);
                const btnCommande = document.getElementById('btn-commande');
                if (btnCommande) {
                    btnCommande.addEventListener('click', () => {
                        window.location.href = urlCommande;
                    });
                }
            });
    }

    // 🧮 Mise à jour initiale
    window.updateCartCount = updateCartCount;
    updateCartCount();

    menuPanier.addEventListener('click', function (e) {
        e.stopPropagation();
        const clicked = e.target;

        // ➕➖ Gestion quantité (connecté ou non)
        if (clicked.classList.contains('btn-plus') || clicked.classList.contains('btn-moins')) {
            const produitId = clicked.dataset.id;
            const action = clicked.classList.contains('btn-plus') ? 'plus' : 'moins';

            // ➤ Détermine l’URL à appeler selon si l'utilisateur est connecté
            const isAuthenticated = document.body.getAttribute('data-auth') === 'true';
            const url = isAuthenticated
                ? '/boutique/panier/update/'
                : '/boutique/panier/update-session/';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: `produit_id=${produitId}&action=${action}`
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        rafraichirDropdownPanier();
                        updateCartCount();

                        const dropdown = bootstrap.Dropdown.getOrCreateInstance(panierBtn);
                        dropdown.show();
                    } else {
                        const alertBox = document.getElementById('panier-alert');
                        if (alertBox) {
                            alertBox.textContent = data.message || "Une erreur s’est produite.";
                            alertBox.classList.remove('d-none');

                            setTimeout(() => {
                                alertBox.classList.add('d-none');
                            }, 4000);
                        }
                    }
                });
        }


        // 🗑️ Gestion suppression
        const deleteBtn = clicked.closest('.btn-supprimer');
        if (deleteBtn) {
            const produitId = deleteBtn.dataset.id;

            // Vérifie si l'utilisateur est connecté via le body (déjà mis plus tôt)
            const isAuthenticated = document.body.dataset.auth === 'true';
            const url = isAuthenticated
                ? '/boutique/panier/supprimer/'
                : '/boutique/panier/supprimer/session/';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: `produit_id=${produitId}`
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        rafraichirDropdownPanier();
                        updateCartCount();

                        const dropdown = bootstrap.Dropdown.getOrCreateInstance(panierBtn);
                        dropdown.show();
                    } else {
                        const alertBox = document.getElementById('panier-alert');
                        if (alertBox) {
                            alertBox.textContent = data.message || "Erreur lors de la suppression.";
                            alertBox.classList.remove('d-none');

                            setTimeout(() => {
                                alertBox.classList.add('d-none');
                            }, 4000);
                        }
                    }
                });
        }

    });

    // 🖱️ Clic sur icône panier = affichage ou redirection mobile
    panierBtn.addEventListener('click', function (e) {
        const isMobile = window.innerWidth <= 768;

        if (isMobile) {
            window.location.href = "/panier/";
        } else {
            rafraichirDropdownPanier();
        }
    });

    // 🛍️ Clic bouton "ajouter au panier rapide"
    boutonsAjouter.forEach(bouton => {
        bouton.addEventListener('click', function () {
            const produitId = this.dataset.id;
            const carte = this.closest('.card');
            const messageErreur = carte.querySelector('.panier-erreur');

            fetch(`/boutique/panier/ajouter/${produitId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCartCount();
                        // Si réussite, on masque le message d'erreur s’il était visible
                        if (messageErreur) {
                            messageErreur.classList.add('d-none');
                            messageErreur.textContent = '';
                        }
                    } else {
                        if (messageErreur) {
                            messageErreur.textContent = data.message || "Une erreur s’est produite.";
                            messageErreur.classList.remove('d-none');

                            setTimeout(() => {
                                messageErreur.classList.add('d-none');
                            }, 4000);
                        }
                    }
                });
        });
    });


    // 🔍 Clic sur "Voir le produit" → remplit et affiche la modale
    document.querySelectorAll('.open-modal-btn').forEach(button => {
        button.addEventListener('click', function () {
            const produitId = this.dataset.id;
            const nom = this.dataset.nom;
            const description = this.dataset.description;
            const prix = parseFloat(this.dataset.prix).toFixed(2);
            const imageUrl = this.dataset.image;

            // Remplissage de la modale
            document.getElementById('modal-ajouter-panier').dataset.id = produitId;
            document.getElementById('modal-product-name').textContent = nom;
            document.getElementById('modal-product-description').textContent = description;
            document.getElementById('modal-product-price').textContent = `${prix} €`;
            document.getElementById('modal-quantity').value = 1;
            document.getElementById('modal-product-image').src = imageUrl || "/static/img/placeholder_chiot.png";

            console.log("🧪 [MODALE] ID récupéré :", produitId);

            // Stocke l’ID dans un attribut du bouton
            const boutonAjouter = document.getElementById('modal-ajouter-panier');
            boutonAjouter.dataset.id = produitId;

            console.log("🧪 [MODALE] ID placé sur le bouton :", boutonAjouter.dataset.id);

            // 🔐 Gère la disponibilité du stock
            const messageStock = document.getElementById('modal-stock-message'); // zone d'affichage info
            const stock = parseInt(this.dataset.stock);
            if (stock <= 0) {
                boutonAjouter.disabled = true;
                boutonAjouter.textContent = "Indisponible";
                if (messageStock) messageStock.textContent = "Ce produit est en rupture de stock.";
            } else {
                boutonAjouter.disabled = false;
                boutonAjouter.textContent = "Ajouter au panier";
                if (messageStock) messageStock.textContent = `Stock disponible : ${stock}`;
            }

            // Affiche la modale
            document.getElementById('productModal').style.display = 'flex';
        });
    });

    // 🛒 Ajout au panier depuis la modale
    const boutonModalAjouter = document.getElementById('modal-ajouter-panier');

    if (boutonModalAjouter) {
        boutonModalAjouter.addEventListener('click', function () {
            const produitId = this.dataset.id;
            const quantite = parseInt(document.getElementById('modal-quantity').value);

            console.log("🧪 [JS] Bouton modal cliqué");
            console.log("🧪 ID produit :", produitId);
            console.log("🧪 Quantité :", quantite);


            if (!produitId || quantite < 1) {
                alert("Erreur : ID produit ou quantité invalide.");
                return;
            }

            fetch(`/boutique/panier/ajouter/${produitId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                },
                body: `quantite=${quantite}`
            })
                .then(response => response.json())
                .then(data => {
                    console.log("🧪 Réponse serveur :", data);
                    if (data.success) {
                        updateCartCount();
                        const modal = document.getElementById('productModal');
                        modal.style.display = 'none'; // refermer la modale
                    } else {
                        const alertBox = document.getElementById('modal-alert');
                            if (alertBox) {
                                alertBox.textContent = data.message || "Une erreur s’est produite.";
                                alertBox.classList.remove('d-none');

                                setTimeout(() => {
                                    alertBox.classList.add('d-none');
                                }, 4000);
                        }
                    }
                });
        });
    }

    // 🔐 Fermeture modale avec la croix
    const modalCloseBtn = document.querySelector('#productModal .close');
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', function () {
            document.getElementById('productModal').style.display = 'none';
        });
}

    // 🔐 Fermeture modale si clic en dehors du contenu
    window.addEventListener('click', function (e) {
        const modal = document.getElementById('productModal');
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});
