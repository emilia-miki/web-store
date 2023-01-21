from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from decimal import Decimal, InvalidOperation
from .models import Product, Order, OrderProduct, OrderStatus
from .serializers import ProductSerializer
from django.db.models import Q, QuerySet
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, FieldDoesNotExist
from django.contrib.auth.models import User

OBJECTS_ON_PAGE = 20


def formulate_detail(rows: int, item: str) -> str:
    if rows == 0:
        return item + " not found"
    elif rows == 1:
        return item + " updated"
    else:
        return "internal error"

def formulate_status(rows: int) -> int:
    if rows == 0:
        return 404
    elif rows == 1:
        return 200
    else:
        return 500

def apply_product_parameters(request: Request) -> QuerySet:
    page = request.query_params.get("page")
    try:
        page = int(page)
    except (ValueError, TypeError):
        page = 1
    search = request.query_params.get("search")
    category = request.query_params.get("category")
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
    if category is not None:
        items = items.filter(category=category)
    if lower_price is not None:
        items = items.filter(price__gte=lower_price)
    if upper_price is not None:
        items = items.filter(price__lte=upper_price)
    if only_avaliable is not None:
        items = items.filter(left__gt=0)
    items = items.order_by(sort_by)
    items = items[((page - 1) * OBJECTS_ON_PAGE):(page * OBJECTS_ON_PAGE)]

@api_view(["GET", "POST"])
def products(request: Request) -> Response:
    if request.method == "GET":
        items = apply_product_parameters(request)

        return_list = []
        for p in items:
            return_dict = dict(ProductSerializer(p).data)
            return_dict["id"] = p.pk
            return_list.append(return_dict)

        return Response(return_list)
    elif request.method == "POST":
        if request.user.is_staff:            
            item: Product

            try:
                item = Product(**request.data)
                item.price = Decimal(request.data["price"])
            except (TypeError, IndexError, InvalidOperation, KeyError):
                return Response(data={"detail": "invalid data"}, status=400)

            try:
                item.save()
            except ValueError:
                return Response(data={"detail": "invalid data"}, status=400)

            return Response(data={"id": item.pk, "detail": "product created"}, status=201)
        else:
            return Response(data={"detail": "not authorized"}, status=401)


@api_view(["GET", "PUT", "DELETE"])
def product(request: Request, pk: str) -> Response:
    if request.method == "GET":
        try:
            item = Product.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(data={"detail": "product not found"}, status=404)

        return_dict = dict(ProductSerializer(item).data)
        return_dict["id"] = pk

        return Response(return_dict)
    elif request.method == "PUT":
        if not request.user.is_staff:
            return Response(data={"detail": "not authorized"}, status=401)

        dict_for_update = dict(request.data)
        if "price" in dict_for_update.keys():
            try:
                dict_for_update["price"] = Decimal(dict_for_update["price"])
            except InvalidOperation:
                return Response(data={"detail": "invalid data"}, status=400)

        try:
            rows = Product.objects.filter(pk=pk).update(**dict_for_update)
        except (KeyError, FieldDoesNotExist):
            return Response(data={"detail": "invalid data"}, status=400)

        return Response(data={"detail": formulate_detail(rows, "product")}, 
                        status=formulate_status(rows))
    elif request.method == "DELETE":
        if not request.user.is_staff:
            return Response(data={"detail": "not authorized"}, status=401)

        item: Product

        try:
            item = Product.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(data={"detail": "product not found"}, status=404)
        except MultipleObjectsReturned:
            return Response(data={"detail": "internal error"}, status=500)

        item.delete()

        return Response({"detail": "product deleted"})


@api_view(["GET", "POST"])
def orders(request: Request) -> Response:
    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response(data={"detail": "not authorized"}, status=401)

        items = Order.objects.filter(customer_id=request.user.pk)
        orders_view = [{"order_id": item.pk, "customer_id": item.customer.pk,
                        "products": [{"product_id": op.product.pk, "amount": op.amount}
                        for op in OrderProduct.objects.filter(order=item)]}
                       for item in items]

        return Response(orders_view)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response(data={"detail": "not authorized"}, status=401)

        customer_id = request.data.get("customer_id")
        products = request.data.get("products")
        if len(request.data.keys()) != 2 or customer_id is None or customer_id == "" or products is None:
            return Response(data={"detail": "invalid data"}, status=400)

        try:
            item = Order(customer=User.objects.get(pk=customer_id), status=OrderStatus.Created)
        except ObjectDoesNotExist:
            return Response(data={"detail": "invalid data"}, status=400)
       
        try:
            item.save()
        except ValueError:
            return Response(data={"detail": "invalid data"}, status=400)

        try:
            for op in products:
                OrderProduct(order=item,
                             product=Product.objects.get(pk=op["product_id"]), 
                             amount=op["amount"]).save()
        except (ObjectDoesNotExist, ValueError, TypeError):
            item.delete()
            return Response(data={"detail": "invalid data"}, status=400)

        return Response(data={"id": item.pk, "detail": "order created"}, status=201)


@api_view(["GET", "PUT"])
def order(request: Request, pk: str):
    if request.method == "GET":
        if not request.user.is_authenticated:
            return Response(data={"detail": "not authorized"}, status=401)

        try:
            item = Order.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(data={"detail": "order not found"}, status=404)

        if item.customer.pk != request.user.pk:
            return Response(data={"detail": "not authorized"}, status=401)

        orderproducts = OrderProduct.objects.filter(order=item)

        return Response({"order_id": pk, "customer_id": item.customer.pk,
                         "products": [{"product_id": op.product.pk, "amount": op.amount} 
                                      for op in orderproducts]})
    elif request.method == "PUT":
        if not request.user.is_staff:
            return Response(data={"detail": "not authorized"}, status=401)

        if len(request.data.keys()) != 1:
            return Response(data={"detail": "invalid data"}, status=400)

        new_status: OrderStatus
        try:
            new_status = OrderStatus(request.data["status"])
        except (ValueError, KeyError, TypeError):
            return Response(data={"detail": "invalid data"}, status=400)

        rows = Order.objects.filter(pk=pk).update(status=new_status)

        return Response(data={"detail": formulate_detail(rows, "order")}, 
                        status=formulate_status(rows))
