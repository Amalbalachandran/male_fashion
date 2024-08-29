from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Cart, CartItem, Category, Product, Wishlist
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
# from django.urls import reverse

def index(request):
    trending_products = Product.objects.filter(trending=True, status=False)[:8]  # Fetch trending products, limit to 8
    return render(request, 'index.html', {'trending_products': trending_products})

def shop(request, slug=None):
    categories = Category.objects.filter(status=False)
    if slug and Category.objects.filter(slug=slug, status=False).exists():
        selected_category = Category.objects.get(slug=slug)   
    else:
        selected_category = categories.first() if categories.exists() else None
    if selected_category:
        products = Product.objects.filter(category=selected_category)
    else:
        products = Product.objects.none()

    # Sorting
    sort_by = request.GET.get('sort_by', '')
    if sort_by == 'price_asc':
        products = products.order_by('selling_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-selling_price')
    
    # Pagination
    paginator = Paginator(products, 3)  # Show 3 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'shop.html', {
        'categories': categories,
        'products': page_obj,
        'selected_category': selected_category,
        'page_obj': page_obj,
        'sort_by': sort_by
    })


def search(request):
    query = request.GET.get('q', '').strip()
    if query:
        products_list = Product.objects.filter(name__icontains=query)
    else:
        products_list = Product.objects.none()  # Return an empty QuerySet if no query is provided

    paginator = Paginator(products_list, 9)  # Show 9 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'search.html', {
        'page_obj': page_obj,
        'query': query  # Pass the query to the template to retain it in the search form
    })


@login_required(login_url='authen:register')
def productview(request, cate_slug, prod_slug):

    # Check if the category exists
    category = Category.objects.filter(slug=cate_slug, status=0).first()
    if not category:
        messages.error(request, "No such category found")
        return redirect('papp:shop')
    
    # Check if the product exists within the category
    product = Product.objects.filter(slug=prod_slug, category=category, status=0).first()
    if not product:
        messages.error(request, "No product found")
        return redirect('papp:shop')
    
     # Get related products (e.g., products from the same category)
    related_products = Product.objects.filter(category=category).exclude(id=product.id)[:4]
    return render(request, 'productview.html', {
        "prod": product,
        "products": related_products})
   

def shoppingcart(request):
    try:
        cart = Cart.objects.get(user=request.user, completed=False)
        cart_items = cart.items.all()
    except Cart.DoesNotExist:
        cart_items = []

    # Calculate subtotal and total
    subtotal = sum(item.total_price() for item in cart_items)
    total = subtotal  # Adjust total as necessary
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
    }
    request.session['total'] = total
    return render(request, 'shoppingcart.html', context)


def addtocart(request, prod_slug):
    product = get_object_or_404(Product, slug=prod_slug)
    cart, created = Cart.objects.get_or_create(user=request.user, completed=False)

    size = request.POST.get('size', '')  # Get size from POST data
    quantity = int(request.POST.get('quantity', 1))  # Get quantity from POST data, default to 1

    # Check if the item already exists in the cart
    cart_item = CartItem.objects.filter(cart=cart, product=product).first()

    if cart_item:
        # If item exists, redirect to shopping cart
        return redirect('papp:shoppingcart')
    else:
        # If item does not exist, create it
        CartItem.objects.create(cart=cart, product=product, size=size, quantity=quantity)
        # Redirect to shopping cart after adding the item
        return redirect('papp:shoppingcart')



def removefromcart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()  # Delete the item from the cart
    return redirect('papp:shoppingcart')  # Redirect to the shopping cart page


def checkout(request):
    # Get the cart for the current user
    cart = get_object_or_404(Cart, user=request.user, completed=False)
    
    # Calculate subtotal and total
    items = cart.items.all()
    subtotal = sum(item.total_price() for item in items)
    total = subtotal  # Add any additional charges to total if necessary

    context = {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'total': total
    }
    return render(request, 'checkout.html', context)

@login_required(login_url='authen:register')
def add_to_wishlist(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        # Product already in wishlist
        return redirect('papp:wishlist')
    return redirect('papp:wishlist')


def remove_from_wishlist(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    if wishlist_item:
        wishlist_item.delete()
    return redirect('papp:wishlist')

@login_required(login_url='authen:register')
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})


def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def blog(request):
    return render(request, 'blog.html')

def blog_a(request):
    return render(request, 'blog_a.html')
def blog_b(request):
    return render(request, 'blog_b.html')
def blog_c(request):
    return render(request, 'blog_c.html')

def final(request):
    return render(request, 'final.html')
















    
