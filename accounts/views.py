from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
#Following line is copied to forms.py. Forms must be handled in forms.py file.
from django.contrib.auth.forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group


from .models import *
from . forms import *
from .filters import OrderFilter
from .decorators import *
#-------------------(DETAIL/LIST VIEWS) -------------------

@unauthenticated_user
def registerPage(request):
        form=CreateUserForm()
        
        if request.method== 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user= form.save()
                username=form.cleaned_data.get('username')
            #   Following data is moved to signals.py file
                # group= Group.objects.get(name='customer')
                # user.groups.add(group)
                # Customer.objects.create(
                #     user=user
                    
                # )
                messages.success(request, 'Account was created for ' + username)
                return redirect('login')
        context={'form': form}
        return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method=='POST':
        username= request.POST.get('username')
        password= request.POST.get('password')
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'username or password incorrect')
    context={}
    return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
#@allowed_users(allowed_roles=['admin'])
@admin_only
def dashBoard(request):
	orders = Order.objects.all().order_by('-status')[0:5]
	customers = Customer.objects.all()

	total_customers = customers.count()

	total_orders = Order.objects.all().count()
	delivered = Order.objects.filter(status='Delivered').count()
	pending = Order.objects.filter(status='Pending').count()



	context = {'customers':customers, 'orders':orders,
	'total_customers':total_customers,'total_orders':total_orders, 
	'delivered':delivered, 'pending':pending}
	return render(request, 'accounts/dashBoard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
    orders= request.user.customer.order_set.all()
    
    total_orders = orders.count()
    delivered = orders.filter(status='Delivered').count()
    pending = orders.filter(status='Pending').count()
    print('ORDERs:', orders)
    context={'orders':orders, 'total_orders':total_orders, 'delivered':delivered, 'pending':pending}
    return render(request, 'accounts/user.html', context)
    
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def accountSettings(request):
    customer=request.user.customer
    form=CustomerForm(instance=customer)
    
    if request.method=='POST':
        form=CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()
    context={'form':form}
    return render(request, 'accounts/account_settings.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
	products = Product.objects.all()
	context = {'products':products}
	return render(request, 'accounts/products.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk):
	customer = Customer.objects.get(id=pk)
	orders = customer.order_set.all()
	total_orders = orders.count()


	#myFilter=OrderFilter()
	orderFilter = OrderFilter(request.GET, queryset=orders) 
	orders = orderFilter.qs
	# we could have passed orderFilter as context if above 2 lines were not commented.
	context = {'customer':customer, 'orders':orders, 'total_orders':total_orders,
	'orderFilter':orderFilter}
	return render(request, 'accounts/customer.html', context)




#-------------------(CREATE VIEWS) -------------------
#def createOrder(request):
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request, pk):
    OrderFormSet=inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10 )
    customer=Customer.objects.get(id=pk)
	#action = 'create'
    #form = OrderForm(initial={'customer':customer})
    formset=OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == 'POST':
        # form = OrderForm(request.POST)
        formset= OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')
    #context =  {'form':form}
    context={'formset': formset}
    return render(request, 'accounts/order_form.html', context)

#-------------------(UPDATE VIEWS) -------------------
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def updateOrder(request, pk):
	action = 'update'
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)

	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/customer/' + str(order.customer.id))

	context =  {'action':action, 'form':form}
	return render(request, 'accounts/order_form.html', context)

#-------------------(DELETE VIEWS) -------------------
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])

def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		customer_id = order.customer.id
		customer_url = '/customer/' + str(customer_id)
		order.delete()
		return redirect(customer_url)
		
	return render(request, 'accounts/delete_item.html', {'item':order})



