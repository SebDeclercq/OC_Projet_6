#!/usr/bin/env python3
'''
@desc    Script populating the OCP6 database (Openclassrooms DA Python)
@author  SDQ <sdq@afnor.org>
@version 1.1.0
@date    2019-01-18
@note    1.0.0 (2018-12-14) : first functional version
@note    1.1.0 (2019-01-18) : debugging product table feed + adding a FK
                              between orders and pizzerias
'''

from dataclasses import dataclass
import os
import random
import re
import time
import string
from typing import Callable, List, Dict, Optional, Any, Iterator
from argparse import ArgumentParser, Namespace
from passlib.hash import pbkdf2_sha256
from faker import Faker
import records
import sqlalchemy


@dataclass
class Member:
    '''Class representing tuples for the Member table'''
    name: str
    firstname: str
    works_at_pizzeria_id: Optional[int]  # REFERENCES Pizzeria
    user_account_id: Optional[int]  # REFERENCES UserAccount
    address_id: int  # REFERENCES Address


class FakeMember(Member):
    '''Class for fake Member generation, by populating
       the table Member for test)'''
    def __init__(self, pizzeria_id: int, address_id: int) -> None:
        fake: Faker = Faker('fr_FR')
        self.name = fake.last_name()
        self.firstname = fake.first_name()
        self.works_at_pizzeria_id = pizzeria_id
        self.address_id = address_id
        self.user_account_id = None


@dataclass
class Address:
    '''Class representing tuples for the Address table'''
    street_name: str
    home_number: str
    zip_code: str
    country: Optional[str] = 'France'


class FakeAddress(Address):
    '''Class for fake Address generation, by populating
       the table Address for test)'''
    def __init__(self) -> None:
        fake: Faker = Faker('fr_FR')
        street: str = fake.address().split('\n')[0]
        m: Optional[Any] = re.match(r'^(\d+),?(.*)$', street)
        if m and len(m.groups()) == 2:
            home_number: str = m[1]
            street_name: str = m[2].lstrip().title()
        else:
            home_number = fake.building_number()
            street_name = street.rstrip()
        self.street_name = street_name
        self.home_number = home_number
        self.zip_code = fake.postcode().replace(' ', '')
        self.country = 'France'


@dataclass
class UserAccount:
    '''Class representing tuples for the UserAccount table'''
    email: str
    phone_nb: str
    member_id: int  # REFERENCES Member
    hashed_pwd: str


class FakeUserAccount(UserAccount):
    '''Class for fake UserAccount generation, by populating
       the table UserAccount for test)'''
    def __init__(self, member_id: int) -> None:
        fake: Faker = Faker('fr_FR')
        self.email = fake.email()
        self.phone_nb = re.sub(r'^\+33|\D', '', fake.phone_number())
        if len(self.phone_nb) < 10:
            self.phone_nb = '0' + self.phone_nb
        self.member_id = member_id
        self.hashed_pwd = pbkdf2_sha256.hash(
            ''.join(random.sample(string.printable, 15))
        )


@dataclass
class TakenOrder:
    '''Class representing tuples for the TakenOrder table'''
    member_id: int  # REFERENCES Member
    address_id: int  # REFERENCES Address
    status_id: int  # REFERENCES OrderStatus
    pizzeria_id: int  # REFERENCES Pizzeria
    is_paid: bool
    bill_id: Optional[int] = None  # REFERENCES Bill


class FakeTakenOrder(TakenOrder):
    '''Class for fake TakenOrder generation, by populating
       the table TakenOrder for test)'''
    def __init__(self, member_id: int, address_id: int, pizzeria_id: int,
                 order_status_ids: List[int]) -> None:
        self.member_id = member_id
        self.address_id = address_id
        self.pizzeria_id = pizzeria_id
        self.status_id = random.choice(order_status_ids)
        self.is_paid = random.choice((True, False))
        self.bill_id = None


@dataclass
class Bill:
    '''Class representing tuples for the Bill table'''
    emission_date: str
    total_amout_ati: float
    order_id: int  # REFERENCES TakenOrder


class FakeBill(Bill):
    '''Class for fake Bill generation, by populating
       the table Bill for test)'''
    def __init__(self, order_id: int) -> None:
        fake: Faker = Faker('fr_FR')
        self.emission_date = fake.date_time_this_decade()
        self.total_amout_ati = fake.pyfloat(
            positive=True, left_digits=2, right_digits=2
        )
        self.order_id = order_id


@dataclass
class Product:
    '''Class representing tuples for the Product table'''
    name: str
    barcode: str
    gram_weight: int
    unit_price_ati: int


class FakeProduct(Product):
    '''Class for fake Product generation, by populating
       the table Product for test)'''
    def __init__(self, name: str) -> None:
        fake: Faker = Faker('fr_FR')
        self.name = name
        self.barcode = fake.ean13()
        self.gram_weight = random.randint(20, 2000) * 5
        self.unit_price_ati = fake.pyfloat(
            positive=True, left_digits=2, right_digits=2
        )


@dataclass
class Pizzeria:
    '''Class representing tuples for the Pizzeria table'''
    name: str
    phone_nb: str
    address_id: Optional[int]


class FakePizzeria(Pizzeria):
    '''Class for fake Pizzeria generation, by populating
       the table Pizzeria for test)'''
    def __init__(self, name: str, address_id: int) -> None:
        fake: Faker = Faker('fr_FR')
        self.name = name
        self.phone_nb = re.sub(r'\+33|\D', '', fake.phone_number())
        if len(self.phone_nb) < 10:
            self.phone_nb = '0' + self.phone_nb
        self.address_id = address_id


@dataclass
class Recipe:
    '''Class representing tuples for the Recipe table'''
    name: str
    description: str
    is_public: bool = False


class FakeRecipe(Recipe):
    '''Class for fake Recipe generation, by populating
       the table Recipe for test)'''
    def __init__(self, name: str) -> None:
        fake: Faker = Faker('fr_FR')
        self.name = name
        self.description = fake.paragraphs()
        self.is_public = random.choice((True, False))


@dataclass
class CatalogItem:
    '''Class representing tuples for the CatalogItem table'''
    name: str
    description: str
    picture_file: str
    unit_price_ati: float
    is_available: bool
    is_displayed: bool
    recipe_id: Optional[int] = None
    product_id: Optional[int] = None


class FakeCatalogItem(CatalogItem):
    '''Class for fake CatalogItem generation, by populating
       the table CatalogItem for test)'''
    def __init__(self, name: str, parent: str, parent_id: int) -> None:
        fake: Faker = Faker('fr_FR')
        self.name = name
        self.description = fake.sentences()
        self.picture_file = fake.file_name(extension='jpg')
        self.unit_price_ati = fake.pyfloat(
            positive=True, left_digits=2, right_digits=2
        )
        self.is_available = random.choice((True, False))
        self.is_displayed = random.choice((True, False))
        if parent == 'recipe':
            self.recipe_id = parent_id
            self.product_id = None
        elif parent == 'product':
            self.product_id = parent_id
            self.recipe_id = None
        else:
            raise AttributeError(f'Unknown parent "{parent}"')


@dataclass
class Role:
    '''Class representing tuples for the Role table'''
    name: str


@dataclass
class Permission:
    '''Class representing tuples for the Permission table'''
    label: str


@dataclass
class OrderStatus:
    '''Class representing tuples for the OrderStatus table'''
    label: str


@dataclass
class Keyword:
    '''Class representing tuples for the Keyword table'''
    name: str


class RandomDataGenerator:
    '''Static class for random data generation. Holds a bunch of
       rendering methods iterators containing Fake* objects'''
    @staticmethod
    def addresses(size: int = 10) -> Iterator[Address]:
        for i in range(size):
            yield FakeAddress()

    @staticmethod
    def members(address_ids: List[int], pizzeria_ids: List[int],
                size: int = 10) -> Iterator[Member]:
        if len(address_ids) < size:
            raise ValueError('Not enough address_ids')
        pizzeria_ids = [random.choice((None, i)) for i in pizzeria_ids]
        random.shuffle(address_ids)
        for i in range(size):
            yield FakeMember(
                random.choice(pizzeria_ids),
                address_ids[i]
            )

    @staticmethod
    def user_accounts(member_ids: List[int], size: int = 10)\
            -> Iterator[UserAccount]:
        if len(member_ids) < size:
            raise ValueError('Not enough member_ids')
        random.shuffle(member_ids)
        for i in range(size):
            yield FakeUserAccount(member_ids[i])

    @staticmethod
    def taken_orders(member_ids: List[int], address_ids: List[int],
                     pizzeria_ids: List[int], order_status_ids: List[int],
                     size: int = 10) -> Iterator[TakenOrder]:
        if len(member_ids) < size:
            raise ValueError('Not enough member_ids')
        elif len(address_ids) < size:
            raise ValueError('Not enough address_ids')
        random.shuffle(member_ids)
        random.shuffle(address_ids)
        for i in range(size):
            yield FakeTakenOrder(
                random.choice(member_ids),
                random.choice(address_ids),
                random.choice(pizzeria_ids),
                order_status_ids
            )

    @staticmethod
    def bills(taken_order_ids: List[int], size: int = 10)\
            -> Iterator[Bill]:
        if len(taken_order_ids) < size:
            print(taken_order_ids)
            raise ValueError('Not enough taken_order_ids')
        for i in range(size):
            yield FakeBill(taken_order_ids[i])

    @staticmethod
    def products() -> Iterator[Product]:
        product_names: List[str] = [
            'farine de blé', 'tomate pelée', 'pulpe de tomate',
            'mozzarella', 'ananas', 'parmesan', 'viande hachée de boeuf',
            'saumon', 'fromage de chèvre', 'artichaut', 'poivron',
            'thon', 'oignon', 'ail', 'pâte', 'oeuf', 'mélange fruits de mer',
            'jambon', 'jambon sec', 'chorizo', 'truffe', 'petit pois',
            'viande de boeuf', 'moule', 'palourde', 'coque',
            "farine d'épeautre", 'langoustine', 'écrevisse', 'crevette rose',
            'crevette grise', 'olive', 'roquette', 'basilic', 'champignon',
        ]
        for product_name in product_names:
            yield FakeProduct(product_name)

    @staticmethod
    def pizzerias(address_ids: List[Optional[int]])\
            -> Iterator[Pizzeria]:
        # OC Pizza has currently 5 stores
        pizzeria_names: List[str] = [
            'OC Pizza #1', 'OC Pizza bis', 'The Best of OC Pizza',
            'OC Pizza Original', "OC Pizza's"
        ]
        if len(address_ids) < 5:
            address_ids += [None] * 5
            random.shuffle(address_ids)
        for i, name in enumerate(pizzeria_names):
            yield FakePizzeria(name, address_ids[i])

    @staticmethod
    def recipes() -> Iterator[Recipe]:
        recipe_names: List[str] = [
            'Spaghetti bolognaise', 'Pizza regina', 'Pizza calzone',
            'Pizza quatre saisons', 'Pizza de la mer', 'Ravioles au crabe',
            'Tagliatelle au saumon', 'Pizza Margarita', 'Pizza hawaïenne',
            'Pâtes à la carbonara', 'Risotto à la truffe', 'Minestrone',
            'Linguine aux fruits de mer', 'Pâtes au pesto', 'Lasagne',
            'Lasagne végétarienne', 'Raviolis quatre fromages',
            'Escalope à la milanaise', 'Carpaccio de boeuf',
            'Scalopine', 'Pizza chèvre miel', 'Pizza végétarienne',
            'Pizza napolitaine',
        ]
        for recipe_name in recipe_names:
            yield FakeRecipe(recipe_name)

    @staticmethod
    def catalog_items(recipes: Dict[str, int])\
            -> Iterator[CatalogItem]:
        for recipe_name, recipe_id in recipes.items():
            yield FakeCatalogItem(
                recipe_name, 'recipe', int(recipe_id)
            )

    @staticmethod
    def order_status() -> Iterator[OrderStatus]:
        labels: List[str] = [
            'Panier', 'En cours', 'En attente', 'Terminée'
        ]
        for label in labels:
            yield OrderStatus(label)

    @staticmethod
    def keywords() -> Iterator[Keyword]:
        labels: List[str] = [
            'pizza', 'pâtes', 'végétarien', 'poisson', 'viande',
            'champignon', 'spaghetti', 'macaroni', 'tagliatelle',
            'fromage', 'chèvre', 'artichaut', 'parmesan', 'gruyère',
            'tomate', 'poivron', 'thon', 'saumon', 'carbonara',
            'moule', 'palourde', 'crevette', 'langoustine', 'écrevisse',
            'porc', 'boeuf', 'poulet', 'volaille', 'oignon', 'ail',
            'napolitain', 'truffe', 'veau', 'pesto', 'riz',
        ]
        for label in labels:
            yield Keyword(label)

    @staticmethod
    def permissions() -> Iterator[Permission]:
        labels: List[str] = [
            'Modifier compte', 'Créer compte', 'Créer commande',
            'Consulter commande tierse', 'Modifier compte tiers',
        ]
        for label in labels:
            yield Permission(label)

    @staticmethod
    def roles() -> Iterator[Role]:
        names: List[str] = [
            'Client', 'Gestionnaire', 'Pizzaïolo', 'Livreur',
            'Opérateur de commande',
        ]
        for name in names:
            yield Role(name)

    @staticmethod
    def has_permission_to(role_ids: List[int],
                          permission_ids: List[int]) -> Dict[str, int]:
        return {'role_id': random.choice(role_ids),
                'permission_id': random.choice(permission_ids)}

    @staticmethod
    def contains_item(taken_order_ids: List[int],
                      catalog_item_ids: List[int]) -> Dict[str, Any]:
        return {'order_id': random.choice(taken_order_ids),
                'item_id': random.choice(catalog_item_ids),
                'quantity': random.randint(1, 10),
                'unit_price_ati': random.uniform(5.00, 80.00)}

    @staticmethod
    def has_product_in_stock(pizzeria_ids: List[int],
                             product_ids: List[int]) -> Dict[str, int]:
        return {'pizzeria_id': random.choice(pizzeria_ids),
                'product_id': random.choice(product_ids),
                'quantity': random.randint(1, 100)}

    @staticmethod
    def requires_product(recipe_ids: List[int],
                         product_ids: List[int]) -> Dict[str, int]:
        return {'recipe_id': random.choice(recipe_ids),
                'product_id': random.choice(product_ids),
                'gram_amount': random.randint(1, 1000)}

    @staticmethod
    def has_keyword(catalog_item_ids: List[int],
                    keyword_ids: List[int]) -> Dict[str, int]:
        return {'item_id': random.choice(catalog_item_ids),
                'keyword_id': random.choice(keyword_ids)}


class DatabaseFeeder:
    '''Main class used to feed all tables in the database'''
    address_ids: List[int]
    member_ids: List[int]
    pizzeria_ids: List[int]
    user_accounts: Dict[int, int]
    recipes: Dict[str, int]
    product_ids: List[int]
    catalog_item_ids: List[int]
    order_status_ids: List[int]
    keyword_ids: List[int]
    permission_ids: List[int]

    def __init__(self, user: str, password: str,
                 host: str, dbname: str, size: int = 10) -> None:
        self.db = records.Database(
            f'postgresql://{user}:{password}@{host}/{dbname}'
        )
        self.size = size

    def populate(self) -> Any:
        s = time.time()
        print('START')
        print('INSERTING ADDRESS')
        self._insert_addresses()
        print('INSERTING PIZZERIAS')
        self._insert_pizzerias()
        print('INSERTING MEMBERS')
        self._insert_members()
        print('INSERTING USER ACCOUNTS')
        self._insert_user_accounts()
        print('UPDATING MEMBERS USER ACCOUNTS')
        self._update_members_user_account()
        print('INSERTING RECIPES')
        self._insert_recipes()
        print('INSERTING PRODUCTS')
        self._insert_products()
        print('INSERTING CATALOG ITEMS')
        self._insert_catalog_items()
        print('INSERTING ORDER STATUS')
        self._insert_order_status()
        print('INSERTING TAKEN ORDERS')
        self._insert_taken_orders()
        print('INSERTING BILLS')
        self._insert_bills()
        print('INSERTING KEYWORDS')
        self._insert_keywords()
        print('INSERTING PERMISSIONS')
        self._insert_permissions()
        print('INSERTING ROLES')
        self._insert_roles()
        print('UPDATING MEMBERS ROLES')
        self._update_members_role()
        print('POPULATING ASSOCIATIVE ENTITIES')
        self._insert_relations_many_to_many()
        e = time.time()
        print(f'END ({e - s:.2f} sec.)')

    def _insert_addresses(self) -> List[int]:
        for address in RandomDataGenerator.addresses(size=self.size):
            self.db.query(
                '''INSERT INTO address
                (street_name, home_number, zip_code, country)
                VALUES (:street_name, :home_number,
                :zip_code, :country);''', **address.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM address;'''
        )
        self.address_ids = [r.id for r in rows]
        return self.address_ids

    def _insert_pizzerias(self) -> List[int]:
        for pizzeria in RandomDataGenerator.pizzerias(self.address_ids):
            self.db.query(
                '''INSERT INTO pizzeria (name, phone_nb, address_id)
                VALUES (:name, :phone_nb, :address_id);''',
                **pizzeria.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM pizzeria;'''
        )
        self.pizzeria_ids = [r.id for r in rows]
        return self.pizzeria_ids

    def _insert_members(self) -> List[int]:
        gen_members: Iterator[Member] = RandomDataGenerator\
            .members(self.address_ids, self.pizzeria_ids, size=self.size)
        for member in gen_members:
            self.db.query(
                '''INSERT INTO member
                (name, firstname, works_at_pizzeria_id,
                user_account_id, address_id)
                VALUES
                (:name, :firstname, :works_at_pizzeria_id,
                :user_account_id, :address_id);''',
                **member.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM member;'''
        )
        self.member_ids = [r.id for r in rows]
        return self.member_ids

    def _insert_user_accounts(self) -> Dict[int, int]:
        gen_user_accounts: Iterator[UserAccount] = \
            RandomDataGenerator.user_accounts(self.member_ids, size=self.size)
        for user_account in gen_user_accounts:
            self.db.query(
                '''INSERT INTO user_account (member_id, email,
                phone_nb, hashed_pwd) VALUES (:member_id, :email,
                :phone_nb, :hashed_pwd);''',
                **user_account.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id, member_id FROM user_account;'''
        )
        self.user_accounts = {r.member_id: r.id for r in rows}
        return self.user_accounts

    def _insert_taken_orders(self) -> List[int]:
        taken_orders: Iterator[TakenOrder] = RandomDataGenerator\
            .taken_orders(self.member_ids, self.address_ids,
                          self.pizzeria_ids, self.order_status_ids,
                          size=self.size)
        for taken_order in taken_orders:
            self.db.query(
                '''INSERT INTO taken_order (member_id, address_id,
                pizzeria_id, status_id, is_paid, bill_id) VALUES (:member_id,
                :address_id, :pizzeria_id, :status_id, :is_paid, :bill_id)''',
                **taken_order.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM taken_order;'''
        )
        self.taken_order_ids = [r.id for r in rows]
        return self.taken_order_ids

    def _insert_bills(self) -> None:
        bills: Iterator[Bill] = RandomDataGenerator\
                .bills(self.taken_order_ids, size=self.size)
        for bill in bills:
            self.db.query(
                '''INSERT INTO bill (emission_date, total_amout_ati,
                order_id) VALUES (:emission_date, :total_amout_ati,
                :order_id);''', **bill.__dict__
            )

    def _insert_recipes(self) -> Dict[str, int]:
        for recipe in RandomDataGenerator.recipes():
            self.db.query(
                '''INSERT INTO recipe (name, description, is_public)
                VALUES (:name, :description, :is_public);''',
                **recipe.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT name, id FROM recipe;'''
        )
        self.recipes = {r.name: r.id for r in rows}
        return self.recipes

    def _insert_products(self) -> Any:
        for product in RandomDataGenerator.products():
            self.db.query(
                '''INSERT INTO product
                (name, barcode, gram_weight, unit_price_ati)
                VALUES (:name, :barcode, :gram_weight, :unit_price_ati);''',
                **product.__dict__
            )
            rows: records.RecordCollection = self.db.query(
                '''SELECT id FROM product;'''
            )
            self.product_ids = [r.id for r in rows]
        return self.product_ids

    def _insert_catalog_items(self) -> List[int]:
        for item in RandomDataGenerator.catalog_items(self.recipes):
            self.db.query(
                '''INSERT INTO catalog_item
                (name, description, picture_file,
                unit_price_ati, is_available, is_displayed,
                recipe_id, product_id) VALUES
                (:name, :description, :picture_file,
                :unit_price_ati, :is_available, :is_displayed,
                :recipe_id, :product_id);''',
                **item.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM catalog_item;'''
        )
        self.catalog_item_ids = [r.id for r in rows]
        return self.catalog_item_ids

    def _update_members_user_account(self) -> None:
        for member_id, ua_id in self.user_accounts.items():
            self.db.query(
                '''UPDATE member SET user_account_id = :ua_id
                WHERE id = :member_id;''',
                **{'member_id': member_id, 'ua_id': ua_id}
            )

    def _update_members_role(self) -> None:
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM member WHERE
            works_at_pizzeria_id IS NOT NULL;'''
        )
        for r in rows:
            self.db.query(
                '''UPDATE member set role_id = :role_id
                WHERE id = :member_id''',
                **{'member_id': r.id,
                   'role_id': random.choice(self.role_ids)}
            )

    def _insert_order_status(self) -> List[int]:
        for status in RandomDataGenerator.order_status():
            self.db.query(
                '''INSERT INTO order_status (label) VALUES (:label);''',
                **status.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM order_status;'''
        )
        self.order_status_ids = [r.id for r in rows]
        return self.order_status_ids

    def _insert_keywords(self) -> Any:
        for keyword in RandomDataGenerator.keywords():
            self.db.query(
                '''INSERT INTO keyword (name) VALUES (:name);''',
                **keyword.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM keyword;'''
        )
        self.keyword_ids = [r.id for r in rows]
        return self.keyword_ids

    def _insert_permissions(self) -> List[int]:
        for permission in RandomDataGenerator.permissions():
            self.db.query(
                '''INSERT INTO permission (label) VALUES (:label);''',
                **permission.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM permission;'''
        )
        self.permission_ids = [r.id for r in rows]
        return self.permission_ids

    def _insert_roles(self) -> List[int]:
        for role in RandomDataGenerator.roles():
            self.db.query(
                '''INSERT INTO role (name) VALUES (:name);''',
                **role.__dict__
            )
        rows: records.RecordCollection = self.db.query(
            '''SELECT id FROM role;'''
        )
        self.role_ids = [r.id for r in rows]
        return self.role_ids

    def _insert_relations_many_to_many(self) -> None:
        callbacks: List[Callable] = [
            self._insert_has_permission_to,
            self._insert_contains_item,
            self._insert_requires_product,
            self._insert_has_product_in_stock,
            self._insert_has_keyword,
        ]
        for callback in callbacks:
            for i in range(self.size):
                try:
                    callback()
                except sqlalchemy.exc.IntegrityError:
                    pass

    def _insert_has_permission_to(self) -> None:
        self.db.query(
            '''INSERT INTO has_permission_to VALUES
                (:role_id, :permission_id);''',
            **RandomDataGenerator.has_permission_to(
                self.role_ids, self.permission_ids
            )
        )

    def _insert_contains_item(self) -> None:
        self.db.query(
            '''INSERT INTO contains_item VALUES
            (:order_id, :item_id, :quantity, :unit_price_ati);''',
            **RandomDataGenerator.contains_item(
                self.taken_order_ids, self.catalog_item_ids
            )
        )

    def _insert_has_product_in_stock(self) -> None:
        self.db.query(
            '''INSERT INTO has_product_in_stock VALUES
            (:pizzeria_id, :product_id, :quantity);''',
            **RandomDataGenerator.has_product_in_stock(
                self.pizzeria_ids, self.product_ids
            )
        )

    def _insert_requires_product(self) -> None:
        self.db.query(
            '''INSERT INTO requires_product VALUES
            (:recipe_id, :product_id, :gram_amount);''',
            **RandomDataGenerator.requires_product(
                list(self.recipes.values()), self.product_ids
            )
        )

    def _insert_has_keyword(self) -> None:
        self.db.query(
            '''INSERT INTO has_keyword VALUES (:item_id, :keyword_id)''',
            **RandomDataGenerator.has_keyword(
                self.catalog_item_ids, self.keyword_ids
            )
        )


def main() -> None:
    arg_parser: ArgumentParser = ArgumentParser(
        description='Script populating an OCP6 Database with fake data'
    )
    arg_parser.add_argument('-s', '--size', type=int, default=10,
                            help='Size of batch of inserted data')
    args: Namespace = arg_parser.parse_args()
    dbfeeder: DatabaseFeeder = DatabaseFeeder(
        os.environ['user'], os.environ['password'],
        os.environ['host'], os.environ['dbname'],
        size=args.size
    )
    dbfeeder.populate()


if __name__ == '__main__':
    main()
