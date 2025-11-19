from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings
import razorpay
import json

from .models import Product, Category, Cart

# ------------------- Home & Product Views -------------------

def home(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "home.html", {"products": products, "categories": categories})

def category_filter(request, id):
    products = Product.objects.filter(category=id)
    categories = Category.objects.all()
    return render(request, "home.html", {"products": products, "categories": categories})

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    return render(request, "product_list.html", {"products": products, "categories": categories})

def product_detail(request, id):
    product = Product.objects.get(id=id)
    categories = Category.objects.all()
    return render(request, "product_detail.html", {"product": product, "categories": categories})

# ------------------- Search -------------------

def search(request):
    query = request.GET.get("q", "")
    categories = Category.objects.all()
    products = Product.objects.all()

    if query:
        words = query.split()
        for w in words:
            products = products.filter(Q(title__icontains=w) | Q(description__icontains=w))
    else:
        products = []

    return render(request, "search.html", {"query": query, "categories": categories, "products": products})

# ------------------- User Authentication -------------------

def signup_user(request):
    if request.method == "POST":
        uname = request.POST['username']
        email = request.POST['email']
        pwd = request.POST['password']
        User.objects.create_user(username=uname, email=email, password=pwd)
        messages.success(request, "Account created! Please login.")
        return redirect("login_user")
    return render(request, "signup.html")

def login_user(request):
    if request.method == "POST":
        uname = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=uname, password=pwd)
        if user:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")

def logout_user(request):
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user).delete()
    logout(request)
    return redirect("login_user")


# ------------------- Cart & Checkout -------------------
def add_to_cart(request, id):
    if not request.user.is_authenticated:
        return redirect("login_user")

    product = Product.objects.get(id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        cart_item.quantity = 1  # First time
    else:
        cart_item.quantity += 1  # Next times

    cart_item.save()

    return redirect('cart')



def cart(request):
    if not request.user.is_authenticated:
        return redirect("login_user")
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, "cart.html", {"cart": cart_items, "total": total})

def checkout(request):
    if not request.user.is_authenticated:
        return redirect("login_user")

    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    # Cart.objects.filter(user=request.user).delete()

    context = {
        "total": total,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    }
    return render(request, "checkout.html", context)


# ------------------- Razorpay Payment -------------------

# Razorpay payment page
def payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    order = client.order.create({
        "amount": total * 100,  # amount in paise
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, "payment.html", {
        "order_id": order["id"],
        "amount": total * 100,
        "key_id": settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
def payment_success(request):
    if request.user.is_authenticated:
        # Clear cart after payment
        Cart.objects.filter(user=request.user).delete()

    return render(request, "payment_success.html")




@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            amount = int(data.get("amount")) * 100  # convert ₹ to paise
        except (ValueError, KeyError, TypeError):
            return JsonResponse({"error": "Invalid amount"}, status=400)

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        return JsonResponse({
            "id": order["id"],
            "amount": order["amount"],
            "key_id": settings.RAZORPAY_KEY_ID
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


def clear_cart(request):
    if not request.user.is_authenticated:
        return redirect("login_user")
    
    Cart.objects.filter(user=request.user).delete()
    return redirect('cart')

