from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fixes incorrect permission ContentType associations and reassigns permissions to groups.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("--- Avvio correzione e configurazione permessi ---"))

        with transaction.atomic():
            # --- 1. RECUPERO E CORREZIONE DEI CONTENTTYPE ---


            # Mappa per memorizzare i ContentType recuperati per app_label.model
            content_types_map = {}
            models_to_check = {
                'review': 'review',
                'products': 'product',
                'users': 'customuser',
                'users': 'address',
                'users': 'paymentmethod',
                'core': 'cart',
                'core': 'cartitem',
                'core': 'order',
                'core': 'orderitem',
                'core': 'deliveryaddress',
                'products': 'category',
                'admin': 'logentry',  # Per i permessi di admin
                'auth': 'group',  # Per i permessi sui gruppi
                'auth': 'permission',  # Per i permessi sui permessi stessi
            }

            for app_label, model_name in models_to_check:
                cts = ContentType.objects.filter(app_label=app_label, model=model_name)
                if cts.count() > 1:
                    # Caso grave: ContentType duplicati. Tenta di risolvere prendendo il primo come corretto.
                    self.stdout.write(self.style.ERROR(
                        f"  ATTENZIONE GRAVE: Trovati ContentType duplicati per {app_label}.{model_name}! Tentativo di risoluzione..."))
                    correct_ct = cts.order_by('pk').first()  # Prendi il primo PK come "corretto"
                    for ct_dup in cts.exclude(pk=correct_ct.pk):
                        # Reindirizza eventuali permessi che puntano al duplicato
                        Permission.objects.filter(content_type=ct_dup).update(content_type=correct_ct)
                        self.stdout.write(
                            f"    Spostati permessi da ContentType duplicato (PK: {ct_dup.pk}) a corretto (PK: {correct_ct.pk}).")
                        ct_dup.delete()  # Elimina il duplicato
                        self.stdout.write(
                            f"    ContentType duplicato {app_label}.{model_name} (PK: {ct_dup.pk}) eliminato.")
                    content_types_map[f"{app_label}.{model_name}"] = correct_ct
                    self.stdout.write(self.style.SUCCESS(
                        f"  Duplicati per {app_label}.{model_name} risolti. PK principale: {correct_ct.pk}"))
                elif cts.count() == 1:
                    content_types_map[f"{app_label}.{model_name}"] = cts.first()
                else:
                    self.stdout.write(self.style.ERROR(
                        f"  ERRORE CRITICO: ContentType per '{app_label}.{model_name}' non trovato. Assicurati che le app siano migrate."))
                    return

                    # Assegna i ContentType recuperati a variabili per comodità
            review_content_type = content_types_map.get('review.review')
            product_content_type = content_types_map.get('products.product')
            user_content_type = content_types_map.get('users.customuser')
            address_content_type = content_types_map.get('users.address')
            payment_content_type = content_types_map.get('users.paymentmethod')
            cart_content_type = content_types_map.get('core.cart')
            cartitem_content_type = content_types_map.get('core.cartitem')
            order_content_type = content_types_map.get('core.order')
            orderitem_content_type = content_types_map.get('core.orderitem')
            deliveryaddress_content_type = content_types_map.get('core.deliveryaddress')
            category_content_type = content_types_map.get('products.category')
            logentry_content_type = content_types_map.get('admin.logentry')
            group_content_type = content_types_map.get('auth.group')
            permission_content_type = content_types_map.get('auth.permission')

            self.stdout.write(self.style.SUCCESS("ContentType recuperati correttamente."))

            # --- 2. ELIMINAZIONE DEI PERMESSI MAL ASSOCIATI (GENERALIZZATO) ---

            expected_ct_by_codename_prefix = {
                'add_review': review_content_type, 'change_review': review_content_type,
                'delete_review': review_content_type, 'view_review': review_content_type,
                'view_all_review': review_content_type,
                'add_product': product_content_type, 'change_product': product_content_type,
                'delete_product': product_content_type, 'view_product': product_content_type,
                'add_category': category_content_type, 'change_category': category_content_type,
                'delete_category': category_content_type, 'view_category': category_content_type,
                'add_customuser': user_content_type, 'change_customuser': user_content_type,
                'view_customuser': user_content_type, 'delete_customuser': user_content_type,
                'add_address': address_content_type, 'change_address': address_content_type,
                'delete_address': address_content_type, 'view_address': address_content_type,
                'add_paymentmethod': payment_content_type, 'change_paymentmethod': payment_content_type,
                'delete_paymentmethod': payment_content_type, 'view_paymentmethod': payment_content_type,
                'add_cart': cart_content_type, 'change_cart': cart_content_type, 'delete_cart': cart_content_type,
                'view_cart': cart_content_type,
                'add_cartitem': cartitem_content_type, 'change_cartitem': cartitem_content_type,
                'delete_cartitem': cartitem_content_type, 'view_cartitem': cartitem_content_type,
                'add_order': order_content_type, 'change_order': order_content_type, 'delete_order': order_content_type,
                'view_order': order_content_type, 'view_all_orders': order_content_type,
                'add_orderitem': orderitem_content_type, 'change_orderitem': orderitem_content_type,
                'delete_orderitem': orderitem_content_type, 'view_orderitem': orderitem_content_type,
                'add_deliveryaddress': deliveryaddress_content_type,
                'change_deliveryaddress': deliveryaddress_content_type,
                'delete_deliveryaddress': deliveryaddress_content_type,
                'view_deliveryaddress': deliveryaddress_content_type,
                'add_logentry': logentry_content_type, 'change_logentry': logentry_content_type,
                'delete_logentry': logentry_content_type, 'view_logentry': logentry_content_type,
                'add_group': group_content_type, 'change_group': group_content_type, 'delete_group': group_content_type,
                'view_group': group_content_type,
                'add_permission': permission_content_type, 'change_permission': permission_content_type,
                'delete_permission': permission_content_type, 'view_permission': permission_content_type,
            }

            incorrectly_linked_perms_count = 0
            all_permissions = Permission.objects.all()


            permissions_to_delete = []

            for perm in all_permissions:
                is_correct = False
                for prefix, expected_ct in expected_ct_by_codename_prefix.items():
                    if perm.codename.startswith(prefix) and perm.content_type == expected_ct:
                        is_correct = True
                        break

                # Questa logica cerca i permessi che NON sono correttamente associati al loro ContentType
                # basandosi sui codename. Se un permesso ha un codename come 'add_review' ma
                # il suo content_type NON è quello di 'review.review', allora è "corrotto".
                if not is_correct and perm.codename in expected_ct_by_codename_prefix:
                    # Questo cattura i casi in cui il codename suggerisce un certo CT, ma il CT è diverso
                    permissions_to_delete.append(perm)
                elif perm.content_type.app_label == 'core' and perm.content_type.model == 'deliveryaddress' and \
                        any(perm.codename.startswith(prefix) for prefix in
                            ['add_review', 'change_review', 'delete_review', 'view_review', 'view_all_review']):
                    # Cattura specificamente il caso noto di 'review' sotto 'core.deliveryaddress'
                    permissions_to_delete.append(perm)
                # Potresti aggiungere altre condizioni specifiche se hai notato altri schemi di corruzione

            if permissions_to_delete:
                incorrectly_linked_perms_count = len(permissions_to_delete)
                self.stdout.write(self.style.WARNING(
                    f"Trovati {incorrectly_linked_perms_count} permessi associati in modo errato. Eliminazione in corso..."))
                for p in permissions_to_delete:
                    self.stdout.write(
                        f"  Eliminazione: {p.codename} (attuale CT: {p.content_type.app_label}.{p.content_type.model})")
                    p.delete()
                self.stdout.write(self.style.SUCCESS("Permessi errati eliminati."))
            else:
                self.stdout.write(self.style.SUCCESS("Nessun permesso associato in modo errato trovato."))

            # --- 3. RECUPERO/CREAZIONE DEI PERMESSI CORRETTI ---


            # Permessi per Review
            add_review_perm, _ = Permission.objects.get_or_create(codename='add_review',
                                                                  defaults={'name': 'Can add review'},
                                                                  content_type=review_content_type)
            view_review_perm, _ = Permission.objects.get_or_create(codename='view_review',
                                                                   defaults={'name': 'Can view review'},
                                                                   content_type=review_content_type)
            change_review_perm, _ = Permission.objects.get_or_create(codename='change_review',
                                                                     defaults={'name': 'Can change review'},
                                                                     content_type=review_content_type)
            delete_review_perm, _ = Permission.objects.get_or_create(codename='delete_review',
                                                                     defaults={'name': 'Can delete review'},
                                                                     content_type=review_content_type)
            view_all_review_perm, _ = Permission.objects.get_or_create(codename='view_all_review',
                                                                       defaults={'name': 'Can view all reviews'},
                                                                       content_type=review_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Review verificati/ricreati correttamente."))

            # Permessi per Product
            add_product_perm, _ = Permission.objects.get_or_create(codename='add_product',
                                                                   defaults={'name': 'Can add product'},
                                                                   content_type=product_content_type)
            view_product_perm, _ = Permission.objects.get_or_create(codename='view_product',
                                                                    defaults={'name': 'Can view product'},
                                                                    content_type=product_content_type)
            change_product_perm, _ = Permission.objects.get_or_create(codename='change_product',
                                                                      defaults={'name': 'Can change product'},
                                                                      content_type=product_content_type)
            delete_product_perm, _ = Permission.objects.get_or_create(codename='delete_product',
                                                                      defaults={'name': 'Can delete product'},
                                                                      content_type=product_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Product verificati/ricreati correttamente."))

            # Permessi per Category
            add_category_perm, _ = Permission.objects.get_or_create(codename='add_category',
                                                                    defaults={'name': 'Can add category'},
                                                                    content_type=category_content_type)
            view_category_perm, _ = Permission.objects.get_or_create(codename='view_category',
                                                                     defaults={'name': 'Can view category'},
                                                                     content_type=category_content_type)
            change_category_perm, _ = Permission.objects.get_or_create(codename='change_category',
                                                                       defaults={'name': 'Can change category'},
                                                                       content_type=category_content_type)
            delete_category_perm, _ = Permission.objects.get_or_create(codename='delete_category',
                                                                       defaults={'name': 'Can delete category'},
                                                                       content_type=category_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Category verificati/ricreati correttamente."))

            # Permessi per Order e OrderItem
            view_order_perm, _ = Permission.objects.get_or_create(codename='view_order',
                                                                  defaults={'name': 'Can view order'},
                                                                  content_type=order_content_type)
            change_order_perm, _ = Permission.objects.get_or_create(codename='change_order',
                                                                    defaults={'name': 'Can change order'},
                                                                    content_type=order_content_type)
            view_all_orders_perm, _ = Permission.objects.get_or_create(codename='view_all_orders',
                                                                       defaults={'name': 'Può vedere tutti gli ordini'},
                                                                       content_type=order_content_type)
            view_orderitem_perm, _ = Permission.objects.get_or_create(codename='view_orderitem',
                                                                      defaults={'name': 'Can view order item'},
                                                                      content_type=orderitem_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Order/OrderItem verificati/ricreati correttamente."))

            # Permessi per Cart e CartItem
            view_cart_perm, _ = Permission.objects.get_or_create(codename='view_cart',
                                                                 defaults={'name': 'Can view cart'},
                                                                 content_type=cart_content_type)
            add_cartitem_perm, _ = Permission.objects.get_or_create(codename='add_cartitem',
                                                                    defaults={'name': 'Can add cart item'},
                                                                    content_type=cartitem_content_type)
            change_cartitem_perm, _ = Permission.objects.get_or_create(codename='change_cartitem',
                                                                       defaults={'name': 'Can change cart item'},
                                                                       content_type=cartitem_content_type)
            delete_cartitem_perm, _ = Permission.objects.get_or_create(codename='delete_cartitem',
                                                                       defaults={'name': 'Can delete cart item'},
                                                                       content_type=cartitem_content_type)
            view_cartitem_perm, _ = Permission.objects.get_or_create(codename='view_cartitem',
                                                                     defaults={'name': 'Can view cart item'},
                                                                     content_type=cartitem_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Cart/CartItem verificati/ricreati correttamente."))

            # Permessi per CustomUser
            view_customuser_perm, _ = Permission.objects.get_or_create(codename='view_customuser',
                                                                       defaults={'name': 'Can view user'},
                                                                       content_type=user_content_type)
            change_customuser_perm, _ = Permission.objects.get_or_create(codename='change_customuser',
                                                                         defaults={'name': 'Can change user'},
                                                                         content_type=user_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi CustomUser verificati/ricreati correttamente."))

            # Permessi per Address
            add_address_perm, _ = Permission.objects.get_or_create(codename='add_address',
                                                                   defaults={'name': 'Can add address'},
                                                                   content_type=address_content_type)
            view_address_perm, _ = Permission.objects.get_or_create(codename='view_address',
                                                                    defaults={'name': 'Can view address'},
                                                                    content_type=address_content_type)
            change_address_perm, _ = Permission.objects.get_or_create(codename='change_address',
                                                                      defaults={'name': 'Can change address'},
                                                                      content_type=address_content_type)
            delete_address_perm, _ = Permission.objects.get_or_create(codename='delete_address',
                                                                      defaults={'name': 'Can delete address'},
                                                                      content_type=address_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Address verificati/ricreati correttamente."))

            # Permessi per PaymentMethod
            add_paymentmethod_perm, _ = Permission.objects.get_or_create(codename='add_paymentmethod',
                                                                         defaults={'name': 'Can add payment method'},
                                                                         content_type=payment_content_type)
            view_paymentmethod_perm, _ = Permission.objects.get_or_create(codename='view_paymentmethod',
                                                                          defaults={'name': 'Can view payment method'},
                                                                          content_type=payment_content_type)
            change_paymentmethod_perm, _ = Permission.objects.get_or_create(codename='change_paymentmethod', defaults={
                'name': 'Can change payment method'}, content_type=payment_content_type)
            delete_paymentmethod_perm, _ = Permission.objects.get_or_create(codename='delete_paymentmethod', defaults={
                'name': 'Can delete payment method'}, content_type=payment_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi PaymentMethod verificati/ricreati correttamente."))

            # Permessi per DeliveryAddress
            view_deliveryaddress_perm, _ = Permission.objects.get_or_create(codename='view_deliveryaddress', defaults={
                'name': 'Can view delivery address'}, content_type=deliveryaddress_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi DeliveryAddress verificati/ricreati correttamente."))

            # Permessi di Django Admin (generici)
            view_logentry_perm, _ = Permission.objects.get_or_create(codename='view_logentry',
                                                                     defaults={'name': 'Can view log entry'},
                                                                     content_type=logentry_content_type)
            view_group_perm, _ = Permission.objects.get_or_create(codename='view_group',
                                                                  defaults={'name': 'Can view group'},
                                                                  content_type=group_content_type)
            view_permission_perm, _ = Permission.objects.get_or_create(codename='view_permission',
                                                                       defaults={'name': 'Can view permission'},
                                                                       content_type=permission_content_type)
            self.stdout.write(self.style.SUCCESS("Permessi Django Admin verificati/ricreati correttamente."))

            # --- 4. CONFIGURAZIONE DEI GRUPPI E ASSEGNAZIONE PERMESSI ---

            # Gruppo Store Managers
            store_managers_group, created = Group.objects.get_or_create(name='Store Managers')
            if created: self.stdout.write(self.style.SUCCESS("Gruppo 'Store Managers' creato."))

            all_store_manager_perms = [
                view_cart_perm, view_all_orders_perm, view_order_perm, view_category_perm, change_category_perm,
                delete_category_perm, add_category_perm, add_product_perm, change_product_perm, delete_product_perm,
                view_product_perm, add_review_perm, change_review_perm, delete_review_perm, view_all_review_perm,
                view_review_perm,
                view_logentry_perm, view_group_perm, view_permission_perm,
                view_orderitem_perm, view_deliveryaddress_perm
            ]
            store_managers_group.permissions.set(all_store_manager_perms)
            self.stdout.write(self.style.SUCCESS("Permessi assegnati a 'Store Managers'."))

            # Gruppo Customers
            customers_group, created = Group.objects.get_or_create(name='Customers')
            if created: self.stdout.write(self.style.SUCCESS("Gruppo 'Customers' creato."))

            all_customer_perms = [
                view_cart_perm, add_cartitem_perm, change_cartitem_perm, delete_cartitem_perm, view_cartitem_perm,
                add_address_perm, change_address_perm, delete_address_perm, view_address_perm,
                change_customuser_perm, view_customuser_perm,
                add_review_perm, view_review_perm,
                add_paymentmethod_perm, view_paymentmethod_perm, change_paymentmethod_perm, delete_paymentmethod_perm,
                view_product_perm
            ]
            customers_group.permissions.set(all_customer_perms)
            self.stdout.write(self.style.SUCCESS("Permessi assegnati a 'Customers'."))

            # --- 5. ASSEGNAZIONE UTENTI AI GRUPPI ---
            User = get_user_model()
            try:
                store_manager_user = User.objects.get(username='store_manager')
                store_manager_user.groups.add(store_managers_group)
                store_manager_user.is_staff = True
                store_manager_user.save()
                self.stdout.write(self.style.SUCCESS("Utente 'store_manager' aggiunto al gruppo 'Store Managers'."))
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING("Attenzione: Utente 'store_manager' non trovato. Assicurati che esista."))

            try:
                customer_user = User.objects.get(username='customer1')
                customer_user.groups.add(customers_group)
                customer_user.save()
                self.stdout.write(self.style.SUCCESS("Utente 'customer1' aggiunto al gruppo 'Customers'."))
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING("Attenzione: Utente 'customer1' non trovato. Assicurati che esista."))

        self.stdout.write(self.style.MIGRATE_HEADING("--- Correzione e configurazione permessi completata ---"))