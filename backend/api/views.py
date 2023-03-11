from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view
from decimal import Decimal, InvalidOperation
from .models import Product, Order, OrderProduct, OrderStatus, Profile
from .serializers import ProductSerializer
from django.db.models import Q, QuerySet
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldDoesNotExist
from django.contrib.auth.models import User
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from typing import Union
from random import Random

OBJECTS_ON_PAGE = 20

def validate_data(actual: dict, 
                 required: list[str], 
                 optional: list[str] = []) -> Union[str, None]:
    invalid_keys = []
    absent_keys = []
    
    for key in actual.keys():
        if key not in required and key not in optional:
            invalid_keys.append(key)
    
    for key in required:
        if key not in actual.keys():
            absent_keys.append(key)

    if len(invalid_keys) == 0 and len(absent_keys) == 0:
        return None

    errors = f"The following keys are invalid: {', '.join(invalid_keys)}. "
    errors += f"The following keys are required, but absent: {', '.join(absent_keys)}."
    return errors

def formulate_detail(affected_rows: int, item_name: str) -> str:
    if affected_rows == 0:
        return item_name + " not found."
    elif affected_rows == 1:
        return item_name + " updated."
    else:
        return "Internal error."

def formulate_status(affected_rows: int) -> int:
    if affected_rows == 0:
        return 404
    elif affected_rows == 1:
        return 200
    else:
        return 500

@api_view(["POST"])
def register(request: Request) -> Response:
    if request.user.is_authenticated:
        return Response({"detail": "You are already logged in."}, 401)

    errors = validate_data(request.data, ["username", "password", "first_name", "last_name",
                                          "email", "phone"])

    if errors is not None:
        return Response({"detail": errors}, 400)

    new_dict = dict(request.data)
    del new_dict["phone"]

    user = User.objects.create_user(**new_dict)
    Profile.objects.create(user=user, phone=request.data["phone"])

    return Response({"detail": "User registered."}, 200)

@api_view(["GET"])
def account(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response({"detail": "You are not logged in."}, 401)

    u = request.user
    return Response({
        "username": u.username, 
        "first_name": u.first_name, 
        "last_name": u.last_name, 
        "email": u.email,
        "phone": Profile.objects.get(user=u).phone
    })

@api_view(["GET"])
def categories(request: Request) -> Response:
    return Response([p.category 
                     for p in Product.objects.order_by("category").distinct("category")])

@api_view(["POST"])
def generate_orders(request: Request) -> Response:
    rand = Random()
    for u in User.objects.all():
        number_of_orders = rand.randint(0, 5)
        for _ in range(number_of_orders):
            o = Order.objects.create(
                    customer=u, 
                    status=OrderStatus(rand.randint(0, len(OrderStatus.choices) - 1)))

            number_of_distinct_products = rand.randint(1, 6)
            for i in range(number_of_distinct_products):
                products = rand.sample(list(Product.objects.all()), number_of_distinct_products)
                OrderProduct.objects.create(order=o, 
                                            product=products[i], 
                                            amount=rand.randint(1, 9))

    return Response()

@api_view(["POST"])
def change_password(request: Request) -> Response:
    if not request.user.is_authenticated:
        return Response({"detail": "You are not logged in."}, 401)

    errors = validate_data(request.data, ["password", "new_password"])

    if errors is not None:
        return Response({"detail": errors}, 400)

    if not request.user.check_password(request.data["password"]):
        return Response({"detail": "Invalid credentials."}, 401)

    request.user.set_password(request.data["new_password"])
    request.user.save()

    return Response({"detail": "Password changed."})

def apply_product_parameters(request: Request) -> QuerySet:
    page = request.query_params.get("page")
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    search = request.query_params.get("search")
    categories = request.query_params.getlist("categories")
    _lower_price = request.query_params.get("lower_price")
    try:
        lower_price = Decimal(_lower_price) if _lower_price is not None else None
    except (ValueError, TypeError):
        lower_price = None
    _upper_price = request.query_params.get("upper_price")
    try:
        upper_price = Decimal(_upper_price) if _lower_price is not None else None
    except (ValueError, TypeError):
        upper_price = None
    sort_by = request.query_params.get("sort_by")
    if sort_by is None:
        sort_by = "-left"
    only_avaliable = request.query_params.get("only_available")

    items = Product.objects.all()
    if search is not None:
        items = items.filter(Q(name__contains=search) | Q(description__contains=search))
    if len(categories) > 0:
        filters = Q(category=categories[0])
        for category in categories[1:]:
            filters |= Q(category=category)

        items = items.filter(filters)
    if lower_price is not None:
        items = items.filter(price__gte=lower_price)
    if upper_price is not None:
        items = items.filter(price__lte=upper_price)
    if only_avaliable is not None:
        items = items.filter(left__gt=0)
    items = items.order_by(sort_by)
    items = items[((page - 1) * OBJECTS_ON_PAGE):(page * OBJECTS_ON_PAGE)]

    return items

@api_view(["GET", "POST"])
def products(request: Request) -> Response:
    if request.method == "GET":
        errors = validate_data(request.data, [], 
                              ["page", "search", "categories", "lower_price",
                               "upper_price", "sort_by", "only_available"])

        if errors is not None:
            return Response({"detail": errors}, 400)
        
        items = apply_product_parameters(request)

        return_list = []
        for p in items:
            return_dict = dict(ProductSerializer(p).data)
            return_dict["id"] = p.pk
            return_list.append(return_dict)

        return Response(return_list)
    elif request.method == "POST":
        if not request.user.is_staff:
            return Response({"detail": "You are not authorized for this action."}, 401)

        errors = validate_data(request.data, 
                               ["name", "category", "description", "img", "price", "left"])

        if errors is not None:
            return Response({"detail": errors}, 400)

        item: Product

        try:
            item = Product(**request.data)
            item.price = Decimal(request.data["price"])
        except (TypeError, IndexError, InvalidOperation, KeyError):
            return Response({"detail": "Invalid data."}, 400)

        try:
            item.save()
        except ValueError:
            return Response({"detail": "Invalid data."}, 400)

        return Response({"id": item.pk, "detail": "Product created."}, 201)


@api_view(["GET", "PUT", "DELETE"])
def product(request: Request, pk: str) -> Response:
    if request.method == "GET":
        try:
            item = Product.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(data={"detail": "Product not found."}, status=404)

        return_dict = dict(ProductSerializer(item).data)
        return_dict["id"] = pk

        return Response(return_dict)
    elif request.method == "PUT":
        if not request.user.is_staff:
            return Response({"detail": "You are not authorized for this action."}, 401)

        errors = validate_data(request.data, [], 
                              ["name", "description", "category", "img", "price", "left"])

        if errors is not None:
            return Response({"detail": errors}, 400)

        dict_for_update = dict(request.data)
        if "price" in dict_for_update.keys():
            try:
                dict_for_update["price"] = Decimal(dict_for_update["price"])
            except InvalidOperation:
                return Response({"detail": "Invalid data."}, 400)

        try:
            rows = Product.objects.filter(pk=pk).update(**dict_for_update)
        except (KeyError, FieldDoesNotExist):
            return Response({"detail": "Invalid data."}, 400)

        return Response({"detail": formulate_detail(rows, "Product")}, 
                        formulate_status(rows))
    elif request.method == "DELETE":
        if not request.user.is_staff:
            return Response({"detail": "You are not authorized for this action."}, 401)

        item: Product

        try:
            item = Product.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"detail": "Product not found."}, 404)
        except MultipleObjectsReturned:
            return Response({"detail": "Internal error."}, 500)

        item.delete()

        return Response({"detail": "Product deleted."})


@api_view(["GET", "POST"])
def orders(request: Request) -> Response:
    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response({"detail": "You are not logged in."}, 401)

        items = Order.objects.filter(customer_id=request.user.pk)
        orders_view = [{"id": item.pk, "customer_id": item.customer.pk,
                        "price": item.price,
                        "status": OrderStatus.labels[item.status], "date": item.date,
                        "products": [{"id": op.product.pk, "amount": op.amount}
                        for op in OrderProduct.objects.filter(order=item)]}
                       for item in items]

        return Response(orders_view)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response({"detail": "You are not logged in."}, 401)

        errors = validate_data(request.data, ["products"])

        if errors is not None:
            return Response({"detail": errors}, 400)

        products = request.data["products"]

        item = Order(customer=User.objects.get(pk=request.user.pk), 
                        status=OrderStatus.Created)
       
        try:
            item.save()
        except ValueError:
            return Response({"detail": "Invalid data."}, 400)

        try:
            for op in products:
                OrderProduct(order=item,
                             product=Product.objects.get(pk=op["id"]), 
                             amount=op["amount"]).save()
        except (ObjectDoesNotExist, ValueError, TypeError):
            item.delete()
            return Response({"detail": "Invalid data."}, 400)

        return Response({"id": item.pk, "detail": "Order created."}, 201)


@api_view(["GET", "PUT"])
def order(request: Request, pk: str):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response({"detail": "You are not logged in."}, 401)

        try:
            item = Order.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"detail": "Order not found."}, 404)

        if item.customer.pk != request.user.pk:
            return Response({"detail": "You are not authorized to view this order."}, 401)

        orderproducts = OrderProduct.objects.filter(order=item)

        return Response({"id": pk, "customer_id": item.customer.pk,
                         "price": item.price,
                         "status": OrderStatus.labels[item.status], "date": item.date,
                         "products": [{"id": op.product.pk, "amount": op.amount} 
                                      for op in orderproducts]})
    elif request.method == "PUT":
        if not request.user.is_authenticated:
            return Response({"detail": "You are not authorized for this action."}, 401)

        errors = validate_data(request.data, ["status"])

        if errors is not None:
            return Response({"detail": errors}, 400)

        try:
            order = Order.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response({"detail": "Order not found."}, 404)

        new_status: OrderStatus
        try:
            index = OrderStatus.labels.index(request.data["status"])
            new_status = OrderStatus(int(index))
        except (ValueError, KeyError, TypeError):
            return Response({"detail": "Invalid data."}, 400)

        if not request.user.is_staff and (
            order.status != OrderStatus.Created 
            or new_status != OrderStatus.Canceled):
            return Response({"detail": "You are not authorized for this action."}, 401)

        rows = Order.objects.filter(pk=pk).update(status=new_status)

        return Response({"detail": formulate_detail(rows, "Order")}, 
                        formulate_status(rows))
