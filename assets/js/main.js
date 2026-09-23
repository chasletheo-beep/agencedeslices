/* Agence des Lices — scripts du site */
(function () {
  "use strict";

  var body = document.body;

  /* ---------- Menu mobile ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("main-nav");
  function closeNav() {
    body.classList.remove("nav-open");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = body.classList.toggle("nav-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) closeNav(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeNav(); });
    window.matchMedia("(min-width: 1200px)").addEventListener("change", function (mq) { if (mq.matches) closeNav(); });
  }

  /* ---------- En-tête au défilement ---------- */
  var header = document.querySelector(".site-header");
  function onScroll() { if (header) header.classList.toggle("is-scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Apparition au défilement ---------- */
  var reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -60px 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Année du pied de page ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- Biens ---------- */
  var BIENS = window.BIENS || [];
  var euro = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });
  var houseIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9v12h14V9"/><path d="M10 21v-6h4v6"/></svg>';

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function card(b) {
    var loc = b.transaction === "location";
    var specs = [];
    if (b.surface) specs.push(b.surface + " m²");
    if (b.pieces) specs.push(b.pieces + (b.pieces > 1 ? " pièces" : " pièce"));
    if (b.chambres) specs.push(b.chambres + (b.chambres > 1 ? " chambres" : " chambre"));
    if (loc && b.meuble) specs.push("Meublé");
    var media = b.photo
      ? '<img src="' + esc(b.photo) + '" alt="' + esc(b.titre + " – " + b.quartier) + '" loading="lazy" width="800" height="600">'
      : houseIcon;
    return '<article class="property">' +
      '<div class="property__media">' + media +
        '<span class="property__badge">' + (loc ? "À louer" : "À vendre") + "</span></div>" +
      '<div class="property__body">' +
        '<span class="property__city">' + esc(b.ville) + (b.quartier ? " · " + esc(b.quartier) : "") + "</span>" +
        '<h3 class="property__title">' + esc(b.titre) + "</h3>" +
        '<div class="property__specs">' + specs.map(function (s) { return "<span>" + esc(s) + "</span>"; }).join("") + "</div>" +
        '<div class="property__price">' + euro.format(b.prix) + (loc ? " <small>/ mois CC</small>" : "") + "</div>" +
      "</div></article>";
  }

  /* Accueil : biens à la une */
  var featured = document.getElementById("featured-list");
  if (featured) {
    var list = BIENS.filter(function (b) { return b.aLaUne; }).slice(0, 3);
    featured.innerHTML = list.length ? list.map(card).join("") :
      '<p class="empty-state">Nos nouvelles annonces arrivent très bientôt.</p>';
  }

  /* Page annonces : filtres */
  var listing = document.getElementById("listing");
  if (listing) {
    var params = new URLSearchParams(window.location.search);
    var state = {
      transaction: params.get("transaction") === "location" ? "location" : "vente",
      type: params.get("type") || "",
      budget: params.get("budget") || "",
      surface: params.get("surface") || ""
    };
    var segButtons = document.querySelectorAll("[data-transaction]");
    var typeSel = document.getElementById("f-type");
    var budgetSel = document.getElementById("f-budget");
    var surfaceSel = document.getElementById("f-surface");
    var count = document.getElementById("listing-count");

    var budgets = {
      vente: [["", "Tous budgets"], ["150000", "Jusqu'à 150 000 €"], ["300000", "Jusqu'à 300 000 €"], ["500000", "Jusqu'à 500 000 €"], ["800000", "Jusqu'à 800 000 €"]],
      location: [["", "Tous loyers"], ["500", "Jusqu'à 500 €"], ["750", "Jusqu'à 750 €"], ["1000", "Jusqu'à 1 000 €"], ["1500", "Jusqu'à 1 500 €"]]
    };

    function fillBudgets() {
      budgetSel.innerHTML = budgets[state.transaction].map(function (o) {
        return '<option value="' + o[0] + '"' + (o[0] === state.budget ? " selected" : "") + ">" + o[1] + "</option>";
      }).join("");
      if (budgetSel.value !== state.budget) state.budget = "";
    }

    function render() {
      segButtons.forEach(function (btn) {
        btn.setAttribute("aria-pressed", btn.dataset.transaction === state.transaction ? "true" : "false");
      });
      var res = BIENS.filter(function (b) {
        return b.transaction === state.transaction &&
          (!state.type || b.type === state.type) &&
          (!state.budget || b.prix <= Number(state.budget)) &&
          (!state.surface || b.surface >= Number(state.surface));
      });
      count.textContent = res.length + (res.length > 1 ? " biens disponibles" : " bien disponible");
      listing.innerHTML = res.length ? res.map(card).join("") :
        '<div class="empty-state"><p>Aucun bien ne correspond à ces critères pour le moment.</p>' +
        '<a class="btn btn--ghost" href="contact.html">Confier votre recherche</a></div>';
      var q = new URLSearchParams();
      Object.keys(state).forEach(function (k) { if (state[k]) q.set(k, state[k]); });
      history.replaceState(null, "", "?" + q.toString());
    }

    segButtons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        state.transaction = btn.dataset.transaction; state.budget = "";
        fillBudgets(); render();
      });
    });
    typeSel.value = state.type;
    typeSel.addEventListener("change", function () { state.type = typeSel.value; render(); });
    budgetSel.addEventListener("change", function () { state.budget = budgetSel.value; render(); });
    surfaceSel.value = state.surface;
    surfaceSel.addEventListener("change", function () { state.surface = surfaceSel.value; render(); });
    fillBudgets(); render();
  }

  /* Recherche rapide (accueil) : adapte les budgets à vente / location */
  var qs = document.getElementById("quick-search");
  if (qs) {
    var qsTrans = qs.querySelector("[name=transaction]");
    var qsBudget = qs.querySelector("[name=budget]");
    var qsOpts = {
      vente: [["", "Tous budgets"], ["150000", "≤ 150 000 €"], ["300000", "≤ 300 000 €"], ["500000", "≤ 500 000 €"], ["800000", "≤ 800 000 €"]],
      location: [["", "Tous loyers"], ["500", "≤ 500 €"], ["750", "≤ 750 €"], ["1000", "≤ 1 000 €"], ["1500", "≤ 1 500 €"]]
    };
    var fillQs = function () {
      qsBudget.innerHTML = qsOpts[qsTrans.value].map(function (o) { return '<option value="' + o[0] + '">' + o[1] + "</option>"; }).join("");
    };
    qsTrans.addEventListener("change", fillQs);
    fillQs();
  }

  /* ---------- Formulaires → e-mail ----------
     Site statique : les formulaires ouvrent la messagerie du visiteur
     avec un message pré-rempli adressé à l'agence. */
  document.querySelectorAll("form[data-mailto]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      var lines = [];
      Array.prototype.forEach.call(form.elements, function (el) {
        if (!el.name || el.type === "checkbox" || el.type === "submit" || !el.value) return;
        var label = form.querySelector('label[for="' + el.id + '"]');
        lines.push((label ? label.textContent.replace(/\s*\*$/, "") : el.name) + " : " + el.value);
      });
      var subject = form.dataset.subject || "Demande depuis le site";
      window.location.href = "mailto:" + form.dataset.mailto +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(lines.join("\n"));
      var status = form.querySelector(".form-status");
      if (status) status.textContent = "Votre messagerie va s'ouvrir avec votre demande pré-remplie. Il ne vous reste plus qu'à l'envoyer.";
    });
  });
})();
