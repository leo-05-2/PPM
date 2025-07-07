# Marketplace PPM

Marketplace PPM è una piattaforma e-commerce sviluppata con Django, pensata per la vendita di alimenti, integratori, attrezzature o in generale articoli per la palestra.  
L'applicazione offre funzionalità di registrazione, accesso, gestione del profilo utente,
ricerca e filtraggio dei prodotti per categoria, prezzo e disponibilità, visualizzazione dettagliata dei prodotti, aggiunta e gestione del carrello,
gestione degli indirizzi e dei metodi di pagamento, checkout con selezione del metodo di spedizione e pagamento, visualizzazione della cronologia ordini, recensioni sui prodotti,
gestione dei preferiti, Gli Store Manager dispongono di una dashboard dedicata per la gestione di prodotti, categorie, ordini e la moderazione delle recensioni
---

## Prerequisiti e Accesso

- Per utilizzare tutte le funzionalità è necessario registrarsi o accedere con un account.
- Alcune funzionalità (come la gestione prodotti) sono riservate agli Store Manager.
- Credenziali di test disponibili:

| Ruolo          | Email                    | Password       |
|----------------|--------------------------|----------------|
| store_manager  | storemanager@test.com    | PasswordStore1 |
| store_manager2 | storemanager2@test.com   | PasswordStore2 |
| customer1      | customer@custom.it       | PasswordUser1  |
| customer2      | customer2@custom.com     | PasswordUser2  |
| admin          | admin@admin.com          | admin          |

---

## Funzionalità principali

### Navigazione tra le categorie e ricerca prodotti

- **Homepage**: mostra le categorie principali e gli ultimi prodotti inseriti.
- **Navigazione**: clicca su una categoria per vedere tutti i prodotti associati.
- **Ricerca**: utilizza la barra di ricerca per trovare prodotti per nome o descrizione.
- **Filtri**: puoi filtrare i prodotti per categoria, prezzo e disponibilità, con diverse modalità di ordinamento.

### Visualizzazione dettagliata di un prodotto, aggiunta al carrello e ai preferiti

- **Dettaglio prodotto**: cliccando su un prodotto si accede alla pagina con tutte le informazioni (immagini, descrizione, prezzo, disponibilità, recensioni).
- **Aggiunta al carrello**: seleziona la quantità e clicca su "Aggiungi al carrello".
- **Aggiunta ai preferiti**: clicca sull’icona a forma di cuore per salvare il prodotto tra i preferiti (visibili nella tua area personale).

### Gestione del carrello

- **Visualizzazione carrello**: accedi al carrello per vedere tutti i prodotti aggiunti, con quantità e prezzo totale.
- **Modifica quantità**: puoi aumentare o diminuire la quantità di ogni prodotto.
- **Rimozione articoli**: rimuovi un prodotto dal carrello con un click.
- **Scelta metodo di spedizione**: seleziona il metodo di spedizione preferito prima del checkout.

### Procedura di checkout

- **Gestione indirizzi**: inserisci un nuovo indirizzo di spedizione o seleziona uno già salvato.
- **Gestione metodi di pagamento**: aggiungi una nuova carta o scegli tra quelle già registrate.
- **Riepilogo ordine**: verifica tutti i dettagli prima di confermare l’acquisto.
- **Conferma ordine**: dopo il pagamento, riceverai una conferma e il carrello verrà svuotato.

### Visualizzazione della cronologia ordini e dettaglio di un ordine

- **Storico ordini**: nella tua area personale puoi vedere tutti gli ordini effettuati.
- **Dettaglio ordine**: clicca su un ordine per vedere i prodotti acquistati, lo stato della spedizione e i dettagli di pagamento.

### Funzionalità per Store Manager

- **Dashboard dedicata**: accessibile solo agli Store Manager, permette di gestire tutti i prodotti e le categorie.
- **Aggiunta prodotto**: inserisci nuovi prodotti specificando nome, descrizione, prezzo, categoria, immagini, ecc.
- **Modifica prodotto**: aggiorna le informazioni di un prodotto già esistente.
- **Eliminazione prodotto**: rimuovi prodotti dal catalogo.
- **Gestione ordini**: visualizza e aggiorna lo stato degli ordini ricevuti.
- **Moderazione recensioni**: visualizza e gestisci le recensioni lasciate dagli utenti sui prodotti.

---

## Esempi di interfaccia

- **Lista prodotti**: griglia con immagine, nome, prezzo e pulsanti per aggiungere al carrello o ai preferiti.
- **Pagina prodotto**: dettagli completi, recensioni, pulsanti per acquisto e preferiti.
- **Carrello**: tabella con prodotti, quantità modificabili, totale e pulsante per procedere al checkout.
- **Dashboard Store Manager**: elenco prodotti con azioni rapide (modifica, elimina), statistiche ordini e recensioni.

---

## Note aggiuntive

- Solo gli utenti autenticati possono acquistare, recensire o aggiungere prodotti ai preferiti.
- Le recensioni possono essere lasciate solo su prodotti effettivamente acquistati e ricevuti.
- Gli Store Manager hanno accesso esclusivo alle funzionalità di gestione prodotti e ordini.
- Il sito supporta la gestione di più indirizzi e metodi di pagamento per ogni utente.

---
