from django.test import TestCase
from .models import OrderProduct, OrderStatus, Product, Order
from random import Random
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import json

OBJECTS_ON_PAGE = 20


class ApiTest(TestCase):
    def _generate_word(self):
        word_length = self.rand.randint(3, 9)
        word = ""
        for _ in range(word_length):
            word += chr(self.rand.randint(ord("a"), ord("z")))

        return word

    def setUp(self):
        Product.objects.all().delete()
        Order.objects.all().delete()
        OrderProduct.objects.all().delete()

        try:
            self.test_user = User.objects.get(username="test_user")
        except ObjectDoesNotExist:
            self.test_user = User.objects.create_user(username="test_user")

        try:
            self.test_admin = User.objects.get(username="test_admin")
        except ObjectDoesNotExist:
            self.test_admin = User.objects.create_user(username="test_admin", is_staff=True)
        
        self.rand = Random()

        self.number_of_products = 50
        self.number_of_categories = self.rand.randint(3, 7)
        self.search_keywords = ["Cleaner", "Apple", "Electric", "Stone", "Light"]
        self.search_expected_results = [0, 0, 0, 0, 0]

        self.product_ids = []
        for _ in range(self.number_of_products):
            p = Product.objects.create(
                name=f'Product {self.rand.choice(self.search_keywords)} ' + self._generate_word(),
                description=f'Description {self.rand.choice(self.search_keywords)}' + self._generate_word(),
                category=f'Category {self.rand.randint(1, self.number_of_categories)}',
                price=Decimal(round(self.rand.random() * 1000.0, 2)),
                left=self.rand.randint(0, 10)
            )
            self.product_ids.append(p.pk)

        for p in Product.objects.all():
            for i, word in enumerate(self.search_keywords):
                if word in p.name or word in p.description:
                    self.search_expected_results[i] += 1

        self.number_of_products_per_category = []
        for i in range(self.number_of_categories):
            self.number_of_products_per_category.append(
                len(Product.objects.filter(category=f'Category {i + 1}')))

        self.number_of_available_products = len(Product.objects.filter(left__gt=0))

        self.number_of_orders = 20
        self.number_of_orderproducts = 0
        self.order_ids = []
        for i in range(self.number_of_orders):
            customer = User.objects.create_user(username=f"user {i + 1}", password=f"user_password{i + 1}",
                                     email=f"user{i + 1}@email.com", first_name=f"fname{i + 1}",
                                     last_name=f"lname{i + 1}")
            order = Order.objects.create(customer=customer,
                                 status=OrderStatus.Created)
            self.order_ids.append(order.pk)
            distinct_products_amount = self.rand.randint(1, 5)
            self.number_of_orderproducts += distinct_products_amount
            for _ in range(distinct_products_amount):
                product_id = self.rand.choice(self.product_ids)
                OrderProduct.objects.create(order=order, product=Product.objects.get(pk=product_id),
                                            amount=self.rand.randint(1, 5))

    def test_get_products(self):
        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), OBJECTS_ON_PAGE)

    def test_get_products_pagination(self):
        last_page = self.number_of_products // OBJECTS_ON_PAGE + 1
        number_of_products_on_last_page = self.number_of_products % OBJECTS_ON_PAGE

        response = self.client.get("/api/products/", {"page": last_page})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), number_of_products_on_last_page)

    def test_get_products_filter_search_with_sorting(self):
        keyword = self.rand.choice(self.search_keywords)
        names = []
        for p in Product.objects.all():
            if keyword in p.name or keyword in p.description:
                names.append(p.name)
        expected_result = sorted(names)[:OBJECTS_ON_PAGE]
        
        response = self.client.get("/api/products/", {"search": keyword, "sort_by": "name"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(expected_result))
        for i in range(len(expected_result)):
            self.assertEqual(response.data[i]["name"], expected_result[i])

    def test_get_products_by_category(self):
        for i in range(self.number_of_categories):
            response = self.client.get("/api/products/", {"category": f"Category {i + 1}"})

            self.assertEqual(response.status_code, 200)
            expected = self.number_of_products_per_category[i]
            if expected > OBJECTS_ON_PAGE:
                expected = OBJECTS_ON_PAGE
            self.assertEqual(len(response.data), expected)

    def test_get_products_filter_price_with_sorting(self):
        lower_price = Decimal("100.25")
        upper_price = Decimal("547.99")
        prices = []
        for p in Product.objects.all():
            if lower_price <= p.price and p.price <= upper_price:
                prices.append(p.price)
        expected_result = [str(p) for p in sorted(prices)[:OBJECTS_ON_PAGE]]

        response = self.client.get("/api/products/",
                                   {"lower_price": str(lower_price), 
                                   "upper_price": str(upper_price),
                                   "sort_by": "price"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(expected_result))
        for i in range(len(expected_result)):
            self.assertEqual(response.data[i]["price"], str(expected_result[i]))

    def test_get_products_only_available_with_sorting(self):
        descriptions = []
        for p in Product.objects.all():
            if p.left > 0:
                descriptions.append(p.description)
        expected_result = sorted(descriptions, reverse=True)[:OBJECTS_ON_PAGE]

        response = self.client.get("/api/products/", 
                                   {"only_available": "true", "sort_by": "-description"})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(expected_result))
        for i in range(len(expected_result)):
            self.assertEqual(response.data[i]["description"], expected_result[i])

    def test_post_product(self):
        self.client.force_login(self.test_admin)

        response = self.client.post("/api/products/",
                                    json.dumps({"name": "Name", "description": "Desc", "category": "Cat", 
                                          "price": "23.4", "left": 0}),
                                    content_type="application/json")
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["detail"], "product created")
        self.assertIsNotNone(response.data["id"])
        exception_raised = False
        try:
            Product.objects.get(name="Name")
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            exception_raised = True
        self.assertFalse(exception_raised)

    def test_post_product_not_authorized(self):
        response1 = self.client.post("/api/products/")

        self.client.force_login(self.test_user)
        response2 = self.client.post("/api/products/")
        responses = [response1, response2]

        for response in responses:
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data["detail"], "not authorized")

    def test_post_product_invalid_data(self):
        self.client.force_login(self.test_admin)

        response1 = self.client.post("/api/products/",
                                    json.dumps({"name": "", "description": "", "category": "", 
                                     "price": ""}),
                                     content_type="application/json")
        response2 = self.client.post("/api/products/",
                                     json.dumps({"name": "", "description": "", "category": "", 
                                     "price": "", "left": 0, "redundant": ""}),
                                     content_type="application/json")
        response3 = self.client.post("/api/products/",
                                     json.dumps({"name": "", "description": "", "category": "", 
                                     "invalid": ""}),
                                     content_type="application/json")
        responses = [response1, response2, response3]

        for response in responses:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["detail"], "invalid data")
            self.assertEqual(len(Product.objects.all()), self.number_of_products)

    def test_get_product(self):
        pk = self.product_ids[0]
        response = self.client.get(f"/api/products/{pk}/")
        p = Product.objects.get(pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], p.name)

    def test_get_product_not_found(self):
        response = self.client.get("/api/products/3258235/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "product not found")

    def test_put_product(self):
        self.client.force_login(self.test_admin)

        pk = self.product_ids[0]
        response = self.client.put(f"/api/products/{pk}/", 
                                   json.dumps({"price": "34.99", "left": 0}),
                                   content_type="application/json")
        p = Product.objects.get(pk=pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "product updated")
        self.assertEqual(p.price, Decimal("34.99"))
        self.assertEqual(p.left, 0)

    def test_put_product_not_authorized(self):
        pk = self.product_ids[0]
        response1 = self.client.put(f"/api/products/{pk}/")

        self.client.force_login(self.test_user)
        response2 = self.client.put(f"/api/products/{pk}/")
        responses = [response1, response2]

        for response in responses:
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data["detail"], "not authorized")

    def test_put_product_invalid_data(self):
        self.client.force_login(self.test_admin)

        pk = self.product_ids[0]
        response1 = self.client.put(f"/api/products/{pk}/",
                                   json.dumps({"dajfsk": ""}),
                                   content_type="application/json")

        response2 = self.client.put(f"/api/products/{pk}/",
                                    json.dumps({ "price": ""}),
                                    content_type="application/json")
        responses = [response1, response2]

        for response in responses:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["detail"], "invalid data")

    def test_put_product_not_found(self):
        self.client.force_login(self.test_admin)

        response = self.client.put("/api/products/2352352/", json.dumps({"name": "new_name"}),
                                   content_type="application/json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "product not found")


    def test_delete_product(self):
        self.client.force_login(self.test_admin)

        pk = self.product_ids[0]
        response = self.client.delete(f"/api/products/{pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "product deleted")

    def test_delete_product_not_authorized(self):
        pk = self.product_ids[0]
        response1 = self.client.delete(f"/api/products/{pk}/")

        self.client.force_login(self.test_user)
        response2 = self.client.delete(f"/api/products/{pk}/")
        responses = [response1, response2]

        for response in responses:
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.data["detail"], "not authorized")

    def test_delete_product_not_found(self):
        self.client.force_login(self.test_admin)

        response = self.client.delete("/api/products/42582436/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "product not found")
        self.assertEqual(self.number_of_products, len(Product.objects.all()))

    def test_get_orders(self):
        self.client.force_login(self.test_user)

        counter = 0
        for order in Order.objects.all():
            if order.customer_id == self.test_user.pk:
                counter += 1

        response = self.client.get("/api/orders/", {"customer_id": self.test_user.pk})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), counter)

    def test_get_orders_not_authorized(self):
        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "not authorized")

    def test_get_order(self):
        order = Order.objects.first()
        self.client.force_login(order.customer)

        response = self.client.get(f"/api/orders/{order.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(int(response.data["order_id"]), order.pk)

    def test_get_order_not_authorized(self):
        order = Order.objects.first()
        excluded = Order.objects.exclude(customer=order.customer).first()
        pk = excluded.pk
        self.client.force_login(order.customer)

        response = self.client.get(f"/api/orders/{pk}/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "not authorized")

    def test_get_order_not_found(self):
        self.client.force_login(self.test_user)

        response = self.client.get("/api/orders/439682/")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "order not found")

    def test_post_order(self):
        self.client.force_login(self.test_user)

        pk1 = self.product_ids[0]
        pk2 = self.product_ids[1]
        response = self.client.post("/api/orders/",
                                    json.dumps({"products": [{"product_id": pk1, "amount": 3},
                                    {"product_id": pk2, "amount": 1}],
                                    "customer_id": self.test_user.pk}),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["detail"], "order created")
        self.assertEqual(len(Order.objects.all()), self.number_of_orders + 1)
        self.assertEqual(len(OrderProduct.objects.all()), self.number_of_orderproducts + 2)
        self.assertEqual(Order.objects.get(pk=response.data["id"]).customer.pk, self.test_user.pk)

    def test_post_order_not_authorized(self):
        response = self.client.post("/api/orders/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "not authorized")

    def test_post_order_invalid_data(self):
        self.client.force_login(self.test_user)

        response1 = self.client.post("/api/orders/",
                                    json.dumps({"dsgfd": ""}),
                                    content_type="application/json")

        response2 = self.client.post("/api/orders/",
                                    json.dumps({"customer_id": "", "products": []}),
                                    content_type="application/json")
        responses = [response1, response2]

        for response in responses:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["detail"], "invalid data")                   


    def test_put_order(self):
        self.client.force_login(self.test_admin)

        pk = self.order_ids[0]
        response = self.client.put(f"/api/orders/{pk}/", json.dumps({"status": 4}), 
                                   content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "order updated")
        self.assertEqual(Order.objects.get(pk=pk).status, 4)

    def test_put_order_not_authorized(self):
        pk = self.order_ids[0]
        response = self.client.put(f"/api/orders/{pk}/", "", content_type="application/json")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "not authorized")

    def test_put_order_invalid_data(self):
        self.client.force_login(self.test_admin)

        pk = self.order_ids[0]
        response1 = self.client.put(f"/api/orders/{pk}/", json.dumps({"status": 9}), 
                                    content_type="application/json")
        response2 = self.client.put(f"/api/orders/{pk}/", json.dumps({"dsaf": ""}),
                                    content_type="application/json")
        responses = [response1, response2]

        for response in responses:
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data["detail"], "invalid data")

    def test_put_order_not_found(self):
        self.client.force_login(self.test_admin)

        response = self.client.put("/api/orders/2352352/", json.dumps({"status": 3}),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["detail"], "order not found")
