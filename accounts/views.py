from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import orderForm, createUserForm, customerForm
from django.forms import inlineformset_factory
from .models import *
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user, allowed_users
from django.contrib.auth.models import Group
# Create your views here.


def deleteCus(request, cid):
    customer = Customer.objects.get(id=cid)
    if request.method == 'POST':
        customer.delete()
        return redirect('/')
    context = {
        'customer': customer
    }
    return render(request, 'accounts/deleteCus.html', context)


def profilePage(request):
    customer = request.user.customer
    form = customerForm(instance=customer)
    if request.method == 'POST':
        form = customerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid:
            form.save()
    context = {
        'form': form,
        'customer': customer
    }
    return render(request, 'accounts/accountSettings.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def userPage(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivred = orders.filter(status='Delivred').count()
    Pending = orders.filter(status='Pending').count()
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'delivred': delivred,
        'Pending': Pending
    }
    return render(request, 'accounts/userPage.html', context)


@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'it\'s fucked up')

    return render(request, 'accounts/login.html')


@unauthenticated_user
def register(request):
    form = createUserForm()
    if request.method == 'POST':
        form = createUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(request, username +
                             " account is created succesfully")
            group = Group.objects.get(name='customer')
            user.groups.add(group)
            Customer.objects.create(
                user=user,
                name=username,
                email=email
            )
            return redirect('login')

    context = {
        'form': form
    }

    return render(request, 'accounts/register.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    total_orders = Order.objects.all().count()
    delivred = orders.filter(status='Delivred').count()
    Pending = orders.filter(status='Pending').count()

    context = {
        'customers': customers,
        'orders': orders,
        'total_orders': total_orders,
        'delivred': delivred,
        'Pending': Pending
    }
    return render(request, 'accounts/dashboard.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def products(request):
    products = Product.objects.all()
    return render(request, 'accounts/products.html', {'products': products})


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def customer(request, cid):
    customer = Customer.objects.get(id=cid)
    orders = customer.order_set.all()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {
        'myFilter': myFilter,
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'accounts/customer.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def createOrder(request, cid):
    orderFormSet = inlineformset_factory(
        Customer, Order, fields=('Product', 'status'))
    customer = Customer.objects.get(id=cid)
    formSet = orderFormSet(instance=customer)
    # form = orderForm(initial={'Customer': customer})
    if request.method == 'POST':
        formSet = orderFormSet(request.POST, instance=customer)
        if formSet.is_valid():
            formSet.save()
            return redirect('/')
    context = {
        'formSet': formSet,
    }
    return render(request, 'accounts/order-form.html', context)


@login_required(login_url='login')
def updateOrder(request, oid):
    order = Order.objects.get(id=oid)
    formSet = orderForm(instance=order)
    if request.method == 'POST':
        formSet = orderForm(request.POST, instance=order)
        if formSet.is_valid():
            formSet.save()
            return redirect('/')
    context = {
        'formSet': formSet,
        'order': order,
    }
    return render(request, 'accounts/order-form.html', context)


@login_required(login_url='login')
def delete(request, oid):
    item = Order.objects.get(id=oid)
    if request.method == 'POST':
        item.delete()
        return redirect('/')
    context = {
        'item': item,
    }
    return render(request, 'accounts/delete.html', context)
