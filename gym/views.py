from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, logout, login
from .models import *
from .forms import *
from random import randint

import razorpay
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Razorpay client
razorpay_client = razorpay.Client(
    auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    )
)

# Create your views here.
def index(request):
    if request.method == "POST":
        u = request.POST['uname']
        p = request.POST['pwd']
        user = authenticate(username=u, password=p)
        if user:
            if user.is_staff:
                login(request, user)
                messages.success(request, "Logged In Successfully")
                return redirect('admin_home')
            else:
                messages.success(request, "Invalid Credentials, Please try again")
                return redirect('index')
    package = Package.objects.filter().order_by('id')[:5]
    return render(request, 'index.html', locals())

def registration(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['secondname']
        email = request.POST['email']
        pwd = request.POST['password']
        mobile = request.POST['mobile']
        address = request.POST['address']

        user = User.objects.create_user(first_name=fname, last_name=lname, email=email, password=pwd, username=email)
        Signup.objects.create(user=user, mobile=mobile,address=address)
        messages.success(request, "Register Successful")
        return redirect('user_login')
    return render(request, 'registration.html', locals())

def user_login(request):
    if request.method == "POST":
        email = request.POST['email']
        pwd = request.POST['password']
        user = authenticate(username=email, password=pwd)
        print(user)
        if user:
            if user.is_staff:
                messages.success(request, "Invalid User")
                return redirect('user_login')
            else:
                print(login(request, user))
                messages.success(request, "User Login Successful")
                return redirect('index')
        else:
            messages.success(request, "Invalid User")
            return redirect('user_login')
    return render(request, 'user_login.html', locals())

def admin_home(request):

    # Admin dashboard requires authentication
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('admin_login')


    totalcategory = Category.objects.all().count()

    totalpackagetype = Packagetype.objects.all().count()

    totalpackage = Package.objects.all().count()

    totalbooking = Booking.objects.all().count()


    # Booking status
    New = Booking.objects.filter(status=1)

    Partial = Booking.objects.filter(status=2)

    Full = Booking.objects.filter(status=3)


    return render(
        request,
        'admin/admin_home.html',
        {
            'totalcategory': totalcategory,
            'totalpackagetype': totalpackagetype,
            'totalpackage': totalpackage,
            'totalbooking': totalbooking,

            'New': New,
            'Partial': Partial,
            'Full': Full,
        }
    )

def Logout(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('index')

def user_logout(request):
    logout(request)
    messages.success(request, "Logout Successfully")
    return redirect('index')

def user_profile(request):
    if request.method == "POST":
        fname = request.POST['firstname']
        lname = request.POST['secondname']
        email = request.POST['email']
        mobile = request.POST['mobile']
        address = request.POST['address']

        user = User.objects.filter(id=request.user.id).update(first_name=fname, last_name=lname, email=email)
        Signup.objects.filter(user=request.user).update(mobile=mobile, address=address)
        messages.success(request, "Updation Successful")
        return redirect('user_profile')
    data = Signup.objects.get(user=request.user)
    return render(request, "user_profile.html", locals())

def user_change_password(request):
    if request.method=="POST":
        n = request.POST['pwd1']
        c = request.POST['pwd2']
        o = request.POST['pwd3']
        if c == n:
            u = User.objects.get(username__exact=request.user.username)
            u.set_password(n)
            u.save()
            messages.success(request, "Password changed successfully")
            return redirect('/')
        else:
            messages.success(request, "New password and confirm password are not same.")
            return redirect('user_change_password')
    return render(request,'user_change_password.html')

def manageCategory(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.all()
    try:
        if request.method == "POST":
            categoryname = request.POST['categoryname']

            try:
                Category.objects.create(categoryname=categoryname)
                error = "no"
            except:
                error = "yes"
    except:
        pass
    return render(request, 'admin/manageCategory.html', locals())

def editCategory(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    category = Category.objects.get(id=pid)
    if request.method == "POST":
        categoryname = request.POST['categoryname']

        category.categoryname = categoryname

        try:
            category.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/editCategory.html', locals())

def deleteCategory(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.get(id=pid)
    category.delete()
    return redirect('manageCategory')

@login_required(login_url='/admin_login/')
def reg_user(request):
    data = Signup.objects.all()
    d = {'data': data}
    return render(request, "admin/reg_user.html", locals())

@login_required(login_url='/admin_login/')
def delete_user(request, pid):
    data = Signup.objects.get(id=pid)
    data.delete()
    messages.success(request, "Delete Successful")
    return redirect('reg_user')

def managePackageType(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    package = Packagetype.objects.all()
    category = Category.objects.all()
    try:
        if request.method == "POST":
            cid = request.POST['category']
            categoryid = Category.objects.get(id=cid)

            packagename = request.POST['packagename']

            try:
                Packagetype.objects.create(category=categoryid, packagename=packagename)
                error = "no"
            except:
                error = "yes"
    except:
        pass
    return render(request, 'admin/managePackageType.html', locals())

def editPackageType(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.all()
    package = Packagetype.objects.get(id=pid)
    if request.method == "POST":
        cid = request.POST['category']
        categoryid = Category.objects.get(id=cid)
        packagename = request.POST['packagename']

        package.category = categoryid
        package.packagename = packagename

        try:
            package.save()
            error = "no"
        except:
            error = "yes"
    return render(request, 'admin/editPackageType.html', locals())


def deletePackageType(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    package = Packagetype.objects.get(id=pid)
    package.delete()
    return redirect('managePackageType')

def addPackage(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    category = Category.objects.all()
    packageid = request.GET.get('packagename', None)
    mypackage = None
    if packageid:
        mypackage = Packagetype.objects.filter(packagename=packageid)
    if request.method == "POST":
        cid = request.POST['category']
        categoryid = Category.objects.get(id=cid)
        packagename = request.POST['packagename']
        packageobj = Packagetype.objects.get(id=packagename)
        titlename = request.POST['titlename']
        duration = request.POST['duration']
        price = request.POST['price']
        description = request.POST['description']

        try:
            Package.objects.create(category=categoryid,packagename=packageobj,
                                   titlename=titlename, packageduration=duration,price=price,description=description)
            error = "no"
        except:
            error = "yes"
    mypackage = Packagetype.objects.all()
    return render(request, 'admin/addPackage.html',locals())

def managePackage(request):
    package = Package.objects.all()
    return render(request, 'admin/managePackage.html',locals())

@login_required(login_url='/user_login/')
def booking_history(request):
    data = Signup.objects.filter(user=request.user).first() 
    data = Booking.objects.filter(register=data)
    return render(request, "booking_history.html", locals())

@login_required(login_url='/admin_login/')
def new_booking(request):
    action = request.GET.get('action')
    data = Booking.objects.filter()
    if action == "New":
        data = data.filter(status="1")
    elif action == "Partial":
        data = data.filter(status="2")
    elif action == "Full":
        data = data.filter(status="3")
    elif action == "Total":
        data = data.filter()
    if request.user.is_staff:
        return render(request, "admin/new_booking.html", locals())
    else:
        return render(request, "booking_history.html", locals())


def booking_detail(request, pid):
    data = Booking.objects.get(id=pid)
    if request.method == "POST":
        price = request.POST['price']
        status = request.POST['status']
        data.status = status
        data.save()
        Paymenthistory.objects.create(booking=data, price=price, status=status)
        messages.success(request, "Action Updated")
        return redirect('booking_detail', pid)
    payment = Paymenthistory.objects.filter(booking=data)
    if request.user.is_staff:
        return render(request, "admin/admin_booking_detail.html", locals())
    else:
        return render(request, "user_booking_detail.html", locals())

def editPackage(request, pid):
    category = Category.objects.all()
    if request.method == "POST":
        cid = request.POST['category']
        categoryid = Category.objects.get(id=cid)
        packagename = request.POST['packagename']
        packageobj = Packagetype.objects.get(id=packagename)
        titlename = request.POST['titlename']
        duration = request.POST['duration']
        price = request.POST['price']
        description = request.POST['description']

        Package.objects.filter(id=pid).update(category=categoryid,packagename=packageobj,
                                   titlename=titlename, packageduration=duration,price=price,description=description)
        messages.success(request, "Updated Successful")
        return redirect('managePackage')
    data = Package.objects.get(id=pid)
    mypackage = Packagetype.objects.all()
    return render(request, "admin/editPackage.html", locals())

def load_subcategory(request):
    categoryid = request.GET.get('category')
    subcategory = Package.objects.filter(category=categoryid).order_by('PackageName')
    return render(request,'subcategory_dropdown_list_options.html',locals())

def deletePackage(request, pid):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    package = Package.objects.get(id=pid)
    package.delete()
    return redirect('managePackage')

def deleteBooking(request, pid):
    booking = Booking.objects.get(id=pid)
    booking.delete()
    messages.success(request, "Delete Successful")
    return redirect('new_booking')

def bookingReport(request):
    data = None
    data2 = None
    if request.method == "POST":
        fromdate = request.POST['fromdate']
        todate = request.POST['todate']

        data = Booking.objects.filter(creationdate__gte=fromdate, creationdate__lte=todate)
        data2 = True
    return render(request, "admin/bookingReport.html", locals())

def regReport(request):
    data = None
    data2 = None
    if request.method == "POST":
        fromdate = request.POST['fromdate']
        todate = request.POST['todate']

        data = Signup.objects.filter(creationdate__gte=fromdate, creationdate__lte=todate)
        data2 = True
    return render(request, "admin/regReport.html", locals())


def changePassword(request):
    if not request.user.is_authenticated:
        return redirect('admin_login')
    error = ""
    user = request.user
    if request.method == "POST":
        o = request.POST['oldpassword']
        n = request.POST['newpassword']
        try:
            u = User.objects.get(id=request.user.id)
            if user.check_password(o):
                u.set_password(n)
                u.save()
                error = "no"
            else:
                error = 'not'
        except:
            error = "yes"
    return render(request, 'admin/changePassword.html',locals())

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

# @login_required(login_url='/user_login/')
# def booking(request):
#     booking = None
#     bookinged = Booking.objects.filter(register__user=request.user)
#     bookinged_list = [i.policy.id for i in bookinged]
#     data = Package.objects.filter().exclude(id__in=bookinged_list)
#     if request.method == "POST":
#         booking = Package.objects.filter()
#         booking = BookingForm(request.POST, request.FILES, instance=booking)
#         if booking.is_valid():
#             booking = booking.save()
#             booking.bookingnumber = random_with_N_digits(10)
#             data.booking = booking
#             data.save()
#         Booking.objects.create(package=booking)
#         messages.success(request, "Action Updated")
#         return redirect('booking')
#     return render(request, "/", locals())

@login_required(login_url='/user_login/')
def apply_booking(request, pid):
    package = Package.objects.filter(id=pid).first()
    register = Signup.objects.filter(user=request.user).first()

    if not package or not register:
        messages.error(request, "Package or user details not found.")
        return redirect('index')

    # Create the booking first. It remains "Not Updated Yet" until
    # Razorpay payment is successfully verified.
    booking = Booking.objects.create(
        package=package,
        register=register,
        bookingnumber=random_with_N_digits(10)
    )

    return redirect('make_payment', booking_id=booking.id)


@login_required(login_url='/user_login/')
def make_payment(request, booking_id):
    if razorpay_client is None:
        messages.error(request, "Payment service is unavailable.")
        return redirect('booking_history')

    # Only allow the logged-in user to pay for their own booking.
    booking = Booking.objects.filter(
        id=booking_id,
        register__user=request.user
    ).select_related('package', 'register__user').first()

    if not booking:
        messages.error(request, "Booking not found.")
        return redirect('booking_history')

    if booking.status == 3:
        messages.info(request, "This booking is already fully paid.")
        return redirect('booking_history')

    try:
        amount = Decimal(str(booking.package.price))
        if amount <= 0:
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        messages.error(request, "Invalid package price.")
        return redirect('index')

    amount_in_paise = int(amount * 100)

    try:
        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": str(booking.bookingnumber),
            "payment_capture": 1
        })
    except Exception as e:
        messages.error(request, "Unable to create Razorpay order.")
        return redirect('booking_detail', booking.id)

    # Keep the existing Paymenthistory model unchanged.
    # A pending record is created and will become Full Payment after
    # Razorpay signature verification succeeds.
    payment = Paymenthistory.objects.create(
        user=booking.register,
        booking=booking,
        price=str(amount),
        status=1
    )

    context = {
        "booking": booking,
        "payment": payment,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount": amount_in_paise,
    }

    return render(request, "payment.html", context)


@csrf_exempt
@login_required(login_url='/user_login/')
def payment_success(request):
    if razorpay_client is None:
        return JsonResponse({
            "status": "failed",
            "message": "Payment service is unavailable."
        }, status=503)

    if request.method != "POST":
        return JsonResponse({
            "status": "failed",
            "message": "Invalid request."
        }, status=400)

    payment_id = request.POST.get("razorpay_payment_id")
    order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")
    booking_id = request.POST.get("booking_id")

    if not all([payment_id, order_id, signature, booking_id]):
        return JsonResponse({
            "status": "failed",
            "message": "Missing payment information."
        }, status=400)

    try:
        # Server-side signature verification.
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature
        })

        booking = Booking.objects.filter(
            id=booking_id,
            register__user=request.user
        ).first()

        if not booking:
            return JsonResponse({
                "status": "failed",
                "message": "Booking not found."
            }, status=404)

        # Find the pending payment record created for this booking.
        payment = Paymenthistory.objects.filter(
            booking=booking,
            status=1
        ).order_by('-id').first()

        if not payment:
            # Prevent creating duplicate full-payment records.
            payment = Paymenthistory.objects.filter(
                booking=booking,
                status=3
            ).order_by('-id').first()

        if not payment:
            return JsonResponse({
                "status": "failed",
                "message": "Payment record not found."
            }, status=404)

        # Existing STATUS choice: 3 = Full Payment.
        payment.status = 3
        payment.save()

        booking.status = 3
        booking.save(update_fields=["status"])

        return JsonResponse({
            "status": "success",
            "message": "Payment successful and booking updated."
        })

    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({
            "status": "failed",
            "message": "Payment verification failed."
        }, status=400)

    except Exception:
        return JsonResponse({
            "status": "failed",
            "message": "Unable to verify payment."
        }, status=500)

def yoga_page(request):
    return render(request, 'yoga_page.html')

def bodyBulding_page(request):
    return render(request, 'admin/bodyBulding_page.html')

def basicMuscle(request):
    return render(request, 'basicMuscle.html')

def protein_page(request):
    return render(request, 'protein_page.html')

def cardio_page(request):
    return render(request, 'cardio_page.html')

def bestequipment_page(request):
    return render(request, 'bestequipment_page.html')

def admin_login(request):

    # If already logged in as admin/staff
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_home')


    if request.method == "POST":

        username = request.POST.get('username', '').strip()

        password = request.POST.get('password', '')


        user = authenticate(
            request,
            username=username,
            password=password
        )


        # Only staff users can access admin dashboard
        if user is not None and user.is_staff:

            login(request, user)

            messages.success(
                request,
                "Welcome to FITFLOW HUB Admin Dashboard."
            )

            return redirect('admin_home')


        messages.error(
            request,
            "Invalid admin credentials or account is not authorized."
        )


    return render(
        request,
        'admin/admin_login.html'
    )