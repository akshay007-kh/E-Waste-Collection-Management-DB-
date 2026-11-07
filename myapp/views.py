
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q
from .models import *
from datetime import datetime
from django.db import transaction
from django.utils import timezone

# ---------------- HOME ----------------

def home(request):
    return render(request, 'home.html')


# ---------------- USER REGISTER ----------------

def register(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('register')

        User.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            password=make_password(password),
            view_pass=password
        )

        messages.success(request, 'Registration successful')
        return redirect('login')

    return render(request, 'register.html')


# ---------------- STAFF REGISTER ----------------

def staff_register(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        password = request.POST.get('password')

        if Staff.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('staff_register')

        Staff.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            password=make_password(password),
            view_pass=password
        )

        messages.success(request, 'Staff registered successfully')
        return redirect('login')

    return render(request, 'staff_register.html')


# ---------------- COMMON LOGIN ----------------

def user_login(request):

    if request.method == 'POST':

        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')

        # 1. ADMIN LOGIN

        admin_user = authenticate(
            request,
            username=identifier,
            password=password
        )

        if admin_user and admin_user.is_superuser:

            auth_login(request, admin_user)

            request.session['user_type'] = 'admin'

            return redirect('admin_home')

        # 2. NORMAL USER LOGIN

        user = User.objects.filter(email=identifier).first()

        if user and check_password(password, user.password):

            request.session.flush()

            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['user_type'] = 'user'

            return redirect('user_home')

        # 3. STAFF LOGIN

        staff = Staff.objects.filter(email=identifier).first()

        if staff and check_password(password, staff.password):

            request.session.flush()

            request.session['staff_id'] = staff.id
            request.session['staff_name'] = staff.name
            request.session['user_type'] = 'staff'

            return redirect('staff_home')

        # INVALID LOGIN

        messages.error(
            request,
            'Invalid username/email or password'
        )

    return render(request, 'login.html')


# ---------------- USER DASHBOARD ----------------

def user_home(request):
    if not check_user(request):
        return redirect('login')

    user = get_object_or_404(
        User,
        id=request.session.get('user_id')
    )

    total_requests = CollectionRequest.objects.filter(user=user).count()

    pending_requests = CollectionRequest.objects.filter(
        user=user, status='Pending'
    ).count()

    completed_requests = CollectionRequest.objects.filter(
        user=user, status='Collected'
    ).count()

    context = {
        'user': user,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
    }

    return render(request, 'user_home.html', context)


# ---------------- STAFF DASHBOARD ----------------

def staff_home(request):
    if not check_staff(request):
        return redirect('login')

    staff = get_object_or_404(
        Staff,
        id=request.session.get('staff_id')
    )

    assignments = Assignment.objects.filter(staff=staff)

    total_assignments = assignments.count()

    pending_assignments = assignments.filter(
        status='Assigned'
    ).count()

    in_progress_assignments = assignments.filter(
        status='In Progress'
    ).count()

    completed_assignments = assignments.filter(
        status='Completed'
    ).count()

    context = {
        'staff': staff,
        'total_assignments': total_assignments,
        'pending_assignments': pending_assignments,
        'in_progress_assignments': in_progress_assignments,
        'completed_assignments': completed_assignments,
    }

    return render(request, 'staff_home.html', context)


# ---------------- ADMIN DASHBOARD ----------------
def admin_home(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('login')

    context = {
        'total_users': User.objects.count(),
        'total_staff': Staff.objects.count(),
        'total_centres': CollectionCentre.objects.count(),
        'total_requests': CollectionRequest.objects.count(),
        'pending_requests': CollectionRequest.objects.filter(
            status='Pending'
        ).count(),

        'collected_requests': CollectionRequest.objects.filter(
            status='Collected'
        ).count(),

        'total_collections': Collection.objects.count(),
        'total_recycling': Recycling.objects.count(),
        'total_feedback': Feedback.objects.count(),
    }

    return render(request, 'admin_home.html', context)

# ---------------- COMMON LOGOUT ----------------

def user_logout(request):

    if request.user.is_authenticated:
        auth_logout(request)
    else:
        request.session.flush()

    messages.success(request, 'Logged out successfully')

    return redirect('home')


# ---------------- STAFF LOGOUT ----------------

def staff_logout(request):

    return user_logout(request)


# ---------------- ADMIN LOGOUT ----------------

def admin_logout(request):

    return user_logout(request)


# ---------------- ADMIN CHECK ----------------

def check_admin(request):
    return (
        request.user.is_authenticated
        and request.user.is_superuser
    )


# ---------------- MANAGE USERS ----------------

def manage_users(request):

    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    users = User.objects.all().order_by('-id')

    if search:
        users = users.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search)
        )

    return render(request, 'manage_users.html', {
        'users': users,
        'search': search
    })


# ---------------- VIEW USER DETAILS ----------------

def view_user(request, id):

    if not check_admin(request):
        return redirect('login')

    user = User.objects.filter(id=id).first()

    if not user:
        messages.error(request, 'User not found')
        return redirect('manage_users')

    return render(request, 'view_user.html', {
        'user': user
    })


# ---------------- EDIT USER ----------------

def edit_user(request, id):

    if not check_admin(request):
        return redirect('login')

    user = User.objects.filter(id=id).first()

    if not user:
        messages.error(request, 'User not found')
        return redirect('manage_users')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, phone, email, address]):
            messages.error(request, 'Please fill all fields')
            return redirect('edit_user', id=id)

        if User.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, 'Email already exists')
            return redirect('edit_user', id=id)

        user.name = name
        user.phone = phone
        user.email = email
        user.address = address
        user.save()

        messages.success(request, 'User updated successfully')
        return redirect('manage_users')

    return render(request, 'edit_user.html', {
        'user': user
    })


# ---------------- DELETE USER ----------------

def delete_user(request, id):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        user = User.objects.filter(id=id).first()

        if user:
            user.delete()
            messages.success(request, 'User deleted successfully')
        else:
            messages.error(request, 'User not found')

    return redirect('manage_users')



# ---------------- MANAGE STAFF ----------------

def manage_staff(request):

    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    staff_list = Staff.objects.all().order_by('-id')

    if search:
        staff_list = staff_list.filter(
            Q(name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    return render(request, 'manage_staff.html', {
        'staff_list': staff_list,
        'search': search
    })


# ---------------- ADD STAFF ----------------

def add_staff(request):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '')

        if not all([name, phone, email, address, password]):
            messages.error(request, 'Please fill all fields')
            return redirect('add_staff')

        if Staff.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('add_staff')

        Staff.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
            password=make_password(password)
        )

        messages.success(request, 'Staff added successfully')
        return redirect('manage_staff')

    return render(request, 'add_staff.html')


# ---------------- VIEW STAFF DETAILS ----------------

def view_staff(request, id):

    if not check_admin(request):
        return redirect('login')

    staff = Staff.objects.filter(id=id).first()

    if not staff:
        messages.error(request, 'Staff not found')
        return redirect('manage_staff')

    return render(request, 'view_staff.html', {
        'staff': staff
    })


# ---------------- EDIT STAFF ----------------

def edit_staff(request, id):

    if not check_admin(request):
        return redirect('login')

    staff = Staff.objects.filter(id=id).first()

    if not staff:
        messages.error(request, 'Staff not found')
        return redirect('manage_staff')

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, phone, email, address]):
            messages.error(request, 'Please fill all fields')
            return redirect('edit_staff', id=id)

        if Staff.objects.filter(email=email).exclude(id=id).exists():
            messages.error(request, 'Email already exists')
            return redirect('edit_staff', id=id)

        staff.name = name
        staff.phone = phone
        staff.email = email
        staff.address = address
        staff.save()

        messages.success(request, 'Staff updated successfully')
        return redirect('manage_staff')

    return render(request, 'edit_staff.html', {
        'staff': staff
    })


# ---------------- DELETE STAFF ----------------

def delete_staff(request, id):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        staff = Staff.objects.filter(id=id).first()

        if staff:
            staff.delete()
            messages.success(request, 'Staff deleted successfully')
        else:
            messages.error(request, 'Staff not found')

    return redirect('manage_staff')


# ---------------- MANAGE COLLECTION CENTRES ----------------

def manage_centres(request):

    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    centres = CollectionCentre.objects.all().order_by('-id')

    if search:
        centres = centres.filter(
            Q(centre_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search) |
            Q(address__icontains=search)
        )

    return render(request, 'manage_centres.html', {
        'centres': centres,
        'search': search
    })


# ---------------- ADD COLLECTION CENTRE ----------------

def add_centre(request):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        centre_name = request.POST.get('centre_name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        if not all([centre_name, address, phone, email]):
            messages.error(request, 'Please fill all fields')
            return redirect('add_centre')

        if CollectionCentre.objects.filter(email=email).exists():
            messages.error(request, 'Centre email already exists')
            return redirect('add_centre')

        CollectionCentre.objects.create(
            centre_name=centre_name,
            address=address,
            phone=phone,
            email=email
        )

        messages.success(request, 'Collection centre added successfully')
        return redirect('manage_centres')

    return render(request, 'add_centre.html')


# ---------------- VIEW CENTRE DETAILS ----------------

def view_centre(request, id):

    if not check_admin(request):
        return redirect('login')

    centre = CollectionCentre.objects.filter(id=id).first()

    if not centre:
        messages.error(request, 'Collection centre not found')
        return redirect('manage_centres')

    return render(request, 'view_centre.html', {
        'centre': centre
    })


# ---------------- EDIT COLLECTION CENTRE ----------------

def edit_centre(request, id):

    if not check_admin(request):
        return redirect('login')

    centre = CollectionCentre.objects.filter(id=id).first()

    if not centre:
        messages.error(request, 'Collection centre not found')
        return redirect('manage_centres')

    if request.method == 'POST':

        centre_name = request.POST.get('centre_name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()

        if not all([centre_name, address, phone, email]):
            messages.error(request, 'Please fill all fields')
            return redirect('edit_centre', id=id)

        if CollectionCentre.objects.filter(
            email=email
        ).exclude(id=id).exists():
            messages.error(request, 'Centre email already exists')
            return redirect('edit_centre', id=id)

        centre.centre_name = centre_name
        centre.address = address
        centre.phone = phone
        centre.email = email
        centre.save()

        messages.success(request, 'Collection centre updated successfully')
        return redirect('manage_centres')

    return render(request, 'edit_centre.html', {
        'centre': centre
    })


# ---------------- DELETE COLLECTION CENTRE ----------------

def delete_centre(request, id):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        centre = CollectionCentre.objects.filter(id=id).first()

        if centre:
            centre.delete()
            messages.success(request, 'Collection centre deleted successfully')
        else:
            messages.error(request, 'Collection centre not found')

    return redirect('manage_centres')

# ---------------- MANAGE CATEGORIES ----------------

def manage_categories(request):

    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    categories = Category.objects.all().order_by('-id')

    if search:
        categories = categories.filter(
            Q(category_name__icontains=search) |
            Q(description__icontains=search)
        )

    return render(request, 'manage_categories.html', {
        'categories': categories,
        'search': search
    })


# ---------------- ADD CATEGORY ----------------

def add_category(request):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()

        if not category_name or not description:
            messages.error(request, 'Please fill all fields')
            return redirect('add_category')

        if Category.objects.filter(
            category_name__iexact=category_name
        ).exists():
            messages.error(request, 'Category already exists')
            return redirect('add_category')

        Category.objects.create(
            category_name=category_name,
            description=description
        )

        messages.success(request, 'Category added successfully')
        return redirect('manage_categories')

    return render(request, 'add_category.html')


# ---------------- VIEW CATEGORY ----------------

def view_category(request, id):

    if not check_admin(request):
        return redirect('login')

    category = Category.objects.filter(id=id).first()

    if not category:
        messages.error(request, 'Category not found')
        return redirect('manage_categories')

    return render(request, 'view_category.html', {
        'category': category
    })


# ---------------- EDIT CATEGORY ----------------

def edit_category(request, id):

    if not check_admin(request):
        return redirect('login')

    category = Category.objects.filter(id=id).first()

    if not category:
        messages.error(request, 'Category not found')
        return redirect('manage_categories')

    if request.method == 'POST':

        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()

        if not category_name or not description:
            messages.error(request, 'Please fill all fields')
            return redirect('edit_category', id=id)

        if Category.objects.filter(
            category_name__iexact=category_name
        ).exclude(id=id).exists():
            messages.error(request, 'Category already exists')
            return redirect('edit_category', id=id)

        category.category_name = category_name
        category.description = description
        category.save()

        messages.success(request, 'Category updated successfully')
        return redirect('manage_categories')

    return render(request, 'edit_category.html', {
        'category': category
    })


# ---------------- DELETE CATEGORY ----------------

def delete_category(request, id):

    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':

        category = Category.objects.filter(id=id).first()

        if category:
            category.delete()
            messages.success(request, 'Category deleted successfully')
        else:
            messages.error(request, 'Category not found')

    return redirect('manage_categories')


def manage_requests(request):
    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '')

    requests_list = CollectionRequest.objects.select_related(
        'user', 'category', 'centre'
    ).order_by('-id')

    if search:
        requests_list = requests_list.filter(
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(category__category_name__icontains=search) |
            Q(centre__centre_name__icontains=search) |
            Q(status__icontains=search) |
            Q(pickup_address__icontains=search)
        )

    return render(request, 'manage_requests.html', {
        'requests_list': requests_list,
        'search': search
    })


def view_request(request, id):
    if not check_admin(request):
        return redirect('login')

    request_obj = get_object_or_404(
        CollectionRequest.objects.select_related(
            'user', 'category', 'centre'
        ),
        id=id
    )

    return render(request, 'view_request.html', {
        'request_obj': request_obj
    })

def edit_request(request, id):
    if not check_admin(request):
        return redirect('login')

    request_obj = get_object_or_404(CollectionRequest, id=id)

    if request.method == 'POST':
        try:
            user_id = request.POST.get('user')
            category_id = request.POST.get('category')
            centre_id = request.POST.get('centre')

            request_obj.user = get_object_or_404(User, id=user_id)
            request_obj.category = get_object_or_404(Category, id=category_id)
            request_obj.centre = get_object_or_404(
                CollectionCentre, id=centre_id
            )

            request_obj.quantity = int(request.POST.get('quantity'))
            request_obj.weight = float(request.POST.get('weight'))
            request_obj.pickup_address = request.POST.get('pickup_address')
            request_obj.pickup_date = datetime.strptime(
                request.POST.get('pickup_date'), '%Y-%m-%d'
            ).date()
            request_obj.status = request.POST.get('status')

            if request_obj.quantity <= 0 or request_obj.weight <= 0:
                raise ValueError("Quantity and weight must be greater than zero.")

            if request_obj.status not in [
                'Pending', 'Assigned', 'Collected', 'Cancelled'
            ]:
                raise ValueError("Invalid request status.")

            request_obj.save()

            messages.success(request, 'Request updated successfully!')
            return redirect('manage_requests')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid request details.')

    return render(request, 'edit_request.html', {
        'request_obj': request_obj,
        'users': User.objects.all(),
        'categories': Category.objects.all(),
        'centres': CollectionCentre.objects.all()
    })


def delete_request(request, id):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        request_obj = get_object_or_404(CollectionRequest, id=id)

        has_assignment = Assignment.objects.filter(
            request=request_obj
        ).exists()

        has_collection = Collection.objects.filter(
            request=request_obj
        ).exists()

        has_feedback = Feedback.objects.filter(
            request=request_obj
        ).exists()

        if has_assignment or has_collection or has_feedback:
            messages.error(
                request,
                'Cannot delete this request because related records exist.'
            )
        else:
            request_obj.delete()
            messages.success(request, 'Request deleted successfully!')

    return redirect('manage_requests')


def manage_assignments(request):
    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    assignments = Assignment.objects.select_related(
        'request__user',
        'request__category',
        'request__centre',
        'staff'
    ).order_by('-id')

    if search:
        assignments = assignments.filter(
            Q(staff__name__icontains=search) |
            Q(request__user__name__icontains=search) |
            Q(request__category__category_name__icontains=search) |
            Q(request__centre__centre_name__icontains=search) |
            Q(status__icontains=search)
        )

    return render(request, 'manage_assignments.html', {
        'assignments': assignments,
        'search': search
    })


def add_assignment(request):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        request_id = request.POST.get('collection_request')
        staff_id = request.POST.get('staff')

        collection_request = get_object_or_404(
            CollectionRequest, id=request_id
        )
        staff = get_object_or_404(Staff, id=staff_id)

        with transaction.atomic():
            collection_request = CollectionRequest.objects.select_for_update().get(
                id=collection_request.id
            )

            if collection_request.status != 'Pending':
                messages.error(
                    request,
                    'Only pending requests can be assigned.'
                )
            elif Assignment.objects.filter(
                request=collection_request
            ).exists():
                messages.error(
                    request,
                    'This request is already assigned.'
                )
            else:
                Assignment.objects.create(
                    request=collection_request,
                    staff=staff,
                    status='Assigned'
                )

                collection_request.status = 'Assigned'
                collection_request.save(update_fields=['status'])

                messages.success(
                    request,
                    'Staff assigned successfully!'
                )
                return redirect('manage_assignments')

    available_requests = CollectionRequest.objects.filter(
        status='Pending'
    ).exclude(
        id__in=Assignment.objects.values('request_id')
    ).select_related('user', 'category')

    return render(request, 'add_assignment.html', {
        'requests_list': available_requests,
        'staff_list': Staff.objects.all()
    })


def view_assignment(request, id):
    if not check_admin(request):
        return redirect('login')

    assignment = get_object_or_404(
        Assignment.objects.select_related(
            'request__user',
            'request__category',
            'request__centre',
            'staff'
        ),
        id=id
    )

    return render(request, 'view_assignment.html', {
        'assignment': assignment
    })


def edit_assignment(request, id):
    if not check_admin(request):
        return redirect('login')

    assignment = get_object_or_404(Assignment, id=id)

    if request.method == 'POST':
        staff_id = request.POST.get('staff')
        status = request.POST.get('status')

        if status not in ['Assigned', 'In Progress', 'Completed']:
            messages.error(request, 'Invalid assignment status.')
        else:
            staff = get_object_or_404(Staff, id=staff_id)

            if assignment.request.status in ['Collected', 'Cancelled']:
                messages.error(
                    request,
                    'Collected or cancelled requests cannot be reassigned.'
                )
            else:
                with transaction.atomic():
                    assignment.staff = staff
                    assignment.status = status
                    assignment.save()

                    if status == 'Completed':
                        # Completion of staff work does not automatically
                        # create a Collection record.
                        assignment.request.status = 'Assigned'
                        assignment.request.save(update_fields=['status'])

                messages.success(request, 'Assignment updated successfully!')
                return redirect('manage_assignments')

    return render(request, 'edit_assignment.html', {
        'assignment': assignment,
        'staff_list': Staff.objects.all()
    })


def delete_assignment(request, id):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        with transaction.atomic():
            assignment = get_object_or_404(Assignment, id=id)
            collection_request = assignment.request

            if Collection.objects.filter(
                request=collection_request
            ).exists():
                messages.error(
                    request,
                    'Cannot delete an assignment with a collection record.'
                )
            else:
                assignment.delete()

                if collection_request.status == 'Assigned':
                    collection_request.status = 'Pending'
                    collection_request.save(update_fields=['status'])

                messages.success(
                    request,
                    'Assignment deleted successfully!'
                )

    return redirect('manage_assignments')


def manage_collections(request):
    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    collections = Collection.objects.select_related(
        'request__user',
        'request__category',
        'request__centre'
    ).order_by('-id')

    if search:
        collections = collections.filter(
            Q(request__user__name__icontains=search) |
            Q(request__category__category_name__icontains=search) |
            Q(request__centre__centre_name__icontains=search) |
            Q(status__icontains=search)
        )

    return render(request, 'manage_collections.html', {
        'collections': collections,
        'search': search
    })


def add_collection(request):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        request_id = request.POST.get('collection_request')
        actual_weight = request.POST.get('actual_weight')
        collection_date = request.POST.get('collection_date')
        status = request.POST.get('status')

        try:
            request_obj = get_object_or_404(
                CollectionRequest, id=request_id
            )

            assignment = Assignment.objects.filter(
                request=request_obj,
                status='Completed'
            ).first()

            if not assignment:
                messages.error(
                    request,
                    'Only requests with completed assignments can be collected.'
                )

            elif Collection.objects.filter(request=request_obj).exists():
                messages.error(
                    request,
                    'Collection record already exists for this request.'
                )

            elif request_obj.status == 'Collected':
                messages.error(request, 'This request is already collected.')

            elif request_obj.status == 'Cancelled':
                messages.error(request, 'Cancelled requests cannot be collected.')

            else:
                weight = float(actual_weight)

                if weight <= 0:
                    raise ValueError

                if status not in ['Collected', 'Partially Collected']:
                    messages.error(request, 'Invalid collection status.')
                else:
                    Collection.objects.create(
                        request=request_obj,
                        actual_weight=weight,
                        collection_date=collection_date,
                        status=status
                    )

                    request_obj.status = 'Collected'
                    request_obj.save(update_fields=['status'])

                    messages.success(
                        request,
                        'Collection recorded successfully!'
                    )
                    return redirect('manage_collections')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid collection details.')

    available_requests = CollectionRequest.objects.filter(
        status='Assigned',
        assignment__status='Completed'
    ).exclude(
        id__in=Collection.objects.values('request_id')
    ).distinct().select_related('user', 'category', 'centre')

    return render(request, 'add_collection.html', {
        'requests_list': available_requests,
        'today': timezone.localdate()
    })


def view_collection(request, id):
    if not check_admin(request):
        return redirect('login')

    collection = get_object_or_404(
        Collection.objects.select_related(
            'request__user',
            'request__category',
            'request__centre'
        ),
        id=id
    )

    assignment = Assignment.objects.filter(
        request=collection.request
    ).select_related('staff').first()

    return render(request, 'view_collection.html', {
        'collection': collection,
        'assignment': assignment
    })


def edit_collection(request, id):
    if not check_admin(request):
        return redirect('login')

    collection = get_object_or_404(Collection, id=id)

    if request.method == 'POST':
        try:
            actual_weight = float(request.POST.get('actual_weight'))
            collection_date = request.POST.get('collection_date')
            status = request.POST.get('status')

            if actual_weight <= 0:
                raise ValueError

            if status not in ['Collected', 'Partially Collected']:
                raise ValueError

            collection.actual_weight = actual_weight
            collection.collection_date = collection_date
            collection.status = status
            collection.save()

            collection.request.status = 'Collected'
            collection.request.save(update_fields=['status'])

            messages.success(request, 'Collection updated successfully!')
            return redirect('manage_collections')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid collection details.')

    return render(request, 'edit_collection.html', {
        'collection': collection
    })



def delete_collection(request, id):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        collection = get_object_or_404(Collection, id=id)
        request_obj = collection.request

        if Recycling.objects.filter(collection=collection).exists():
            messages.error(
                request,
                'Cannot delete this collection because recycling records exist.'
            )
        else:
            collection.delete()

            request_obj.status = 'Assigned'
            request_obj.save(update_fields=['status'])

            messages.success(request, 'Collection deleted successfully!')

    return redirect('manage_collections')


def manage_recycling(request):
    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    recycling_list = Recycling.objects.select_related(
        'collection__request__user',
        'collection__request__category',
        'collection__request__centre'
    ).order_by('-id')

    if search:
        recycling_list = recycling_list.filter(
            Q(collection__request__user__name__icontains=search) |
            Q(collection__request__category__category_name__icontains=search) |
            Q(collection__request__centre__centre_name__icontains=search) |
            Q(status__icontains=search)
        )

    return render(request, 'manage_recycling.html', {
        'recycling_list': recycling_list,
        'search': search
    })


def add_recycling(request):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        collection_id = request.POST.get('collection')
        recycled_weight = request.POST.get('recycled_weight')
        recycling_date = request.POST.get('recycling_date')
        status = request.POST.get('status')

        try:
            collection = get_object_or_404(Collection, id=collection_id)

            if Recycling.objects.filter(collection=collection).exists():
                messages.error(
                    request,
                    'Recycling record already exists for this collection.'
                )

            else:
                weight = float(recycled_weight)

                if weight <= 0:
                    raise ValueError

                if weight > collection.actual_weight:
                    messages.error(
                        request,
                        'Recycled weight cannot exceed actual collected weight.'
                    )

                elif status not in ['Processing', 'Completed']:
                    messages.error(request, 'Invalid recycling status.')

                else:
                    Recycling.objects.create(
                        collection=collection,
                        recycled_weight=weight,
                        recycling_date=recycling_date,
                        status=status
                    )

                    messages.success(
                        request,
                        'Recycling record added successfully!'
                    )
                    return redirect('manage_recycling')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid recycling details.')

    available_collections = Collection.objects.exclude(
        id__in=Recycling.objects.values('collection_id')
    ).select_related(
        'request__user',
        'request__category'
    )

    return render(request, 'add_recycling.html', {
        'collections': available_collections,
        'today': timezone.localdate()
    })


def view_recycling(request, id):
    if not check_admin(request):
        return redirect('login')

    recycling = get_object_or_404(
        Recycling.objects.select_related(
            'collection__request__user',
            'collection__request__category',
            'collection__request__centre'
        ),
        id=id
    )

    return render(request, 'view_recycling.html', {
        'recycling': recycling
    })


def edit_recycling(request, id):
    if not check_admin(request):
        return redirect('login')

    recycling = get_object_or_404(Recycling, id=id)

    if request.method == 'POST':
        try:
            weight = float(request.POST.get('recycled_weight'))
            recycling_date = request.POST.get('recycling_date')
            status = request.POST.get('status')

            if weight <= 0 or weight > recycling.collection.actual_weight:
                raise ValueError

            if status not in ['Processing', 'Completed']:
                raise ValueError

            recycling.recycled_weight = weight
            recycling.recycling_date = recycling_date
            recycling.status = status
            recycling.save()

            messages.success(
                request,
                'Recycling record updated successfully!'
            )
            return redirect('manage_recycling')

        except (ValueError, TypeError):
            messages.error(
                request,
                'Enter valid weight, date and status. Recycled weight cannot exceed collected weight.'
            )

    return render(request, 'edit_recycling.html', {
        'recycling': recycling
    })


def delete_recycling(request, id):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        recycling = get_object_or_404(Recycling, id=id)
        recycling.delete()

        messages.success(
            request,
            'Recycling record deleted successfully!'
        )

    return redirect('manage_recycling')


def manage_feedback(request):
    if not check_admin(request):
        return redirect('login')

    search = request.GET.get('search', '').strip()

    feedback_list = Feedback.objects.select_related(
        'user', 'request__category', 'request__centre'
    ).order_by('-id')

    if search:
        feedback_list = feedback_list.filter(
            Q(user__name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(request__id__icontains=search) |
            Q(request__category__category_name__icontains=search) |
            Q(rating__icontains=search) |
            Q(message__icontains=search)
        )

    return render(request, 'manage_feedback.html', {
        'feedback_list': feedback_list,
        'search': search
    })


def view_feedback(request, id):
    if not check_admin(request):
        return redirect('login')

    feedback = get_object_or_404(
        Feedback.objects.select_related(
            'user', 'request__category', 'request__centre'
        ),
        id=id
    )

    return render(request, 'view_feedback.html', {
        'feedback': feedback
    })


def edit_feedback(request, id):
    if not check_admin(request):
        return redirect('login')

    feedback = get_object_or_404(Feedback, id=id)

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
            message = request.POST.get('message', '').strip()

            if rating < 1 or rating > 5:
                raise ValueError

            if not message:
                messages.error(request, 'Feedback message is required.')
            else:
                feedback.rating = rating
                feedback.message = message
                feedback.save()

                messages.success(
                    request,
                    'Feedback updated successfully!'
                )
                return redirect('manage_feedback')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter a valid rating.')

    return render(request, 'edit_feedback.html', {
        'feedback': feedback
    })



def delete_feedback(request, id):
    if not check_admin(request):
        return redirect('login')

    if request.method == 'POST':
        feedback = get_object_or_404(Feedback, id=id)
        feedback.delete()

        messages.success(request, 'Feedback deleted successfully!')

    return redirect('manage_feedback')


def check_user(request):
    return (
        request.session.get('user_type') == 'user'
        and request.session.get('user_id') is not None
    )


def create_collection_request(request):
    if not check_user(request):
        return redirect('login')

    user = get_object_or_404(
        User,
        id=request.session.get('user_id')
    )

    if request.method == 'POST':
        try:
            category = get_object_or_404(
                Category,
                id=request.POST.get('category')
            )

            centre = get_object_or_404(
                CollectionCentre,
                id=request.POST.get('centre')
            )

            quantity = int(request.POST.get('quantity'))
            weight = float(request.POST.get('weight'))
            pickup_address = request.POST.get('pickup_address', '').strip()
            pickup_date = datetime.strptime(
                request.POST.get('pickup_date'), '%Y-%m-%d'
            ).date()

            if quantity <= 0 or weight <= 0:
                raise ValueError

            if not pickup_address:
                messages.error(request, 'Pickup address is required.')

            elif pickup_date < timezone.localdate():
                messages.error(request, 'Please select a future pickup date.')

            else:
                CollectionRequest.objects.create(
                    user=user,
                    category=category,
                    centre=centre,
                    quantity=quantity,
                    weight=weight,
                    pickup_address=pickup_address,
                    pickup_date=pickup_date,
                    status='Pending'
                )

                messages.success(
                    request,
                    'Collection request submitted successfully!'
                )
                return redirect('my_requests')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid request details.')

    return render(request, 'create_collection_request.html', {
        'categories': Category.objects.all(),
        'centres': CollectionCentre.objects.all(),
        'today': timezone.localdate()
    })


def my_requests(request):
    if not check_user(request):
        return redirect('login')

    user = get_object_or_404(
        User,
        id=request.session.get('user_id')
    )

    requests_list = CollectionRequest.objects.filter(
        user=user
    ).select_related(
        'category', 'centre'
    ).order_by('-id')

    feedback_request_ids = Feedback.objects.filter(
        user=user
    ).values_list('request_id', flat=True)

    return render(request, 'my_requests.html', {
        'requests_list': requests_list,
        'feedback_request_ids': feedback_request_ids
    })


def track_request(request, id):
    if not check_user(request):
        return redirect('login')

    user = get_object_or_404(
        User,
        id=request.session.get('user_id')
    )

    request_obj = get_object_or_404(
        CollectionRequest.objects.select_related(
            'category', 'centre'
        ),
        id=id,
        user=user
    )

    assignment = Assignment.objects.filter(
        request=request_obj
    ).select_related('staff').first()

    collection = Collection.objects.filter(
        request=request_obj
    ).first()

    recycling = Recycling.objects.filter(
        collection=collection
    ).first() if collection else None

    return render(request, 'track_request.html', {
        'request_obj': request_obj,
        'assignment': assignment,
        'collection': collection,
        'recycling': recycling
    })


def submit_feedback(request, id):
    if not check_user(request):
        return redirect('login')

    user = get_object_or_404(
        User,
        id=request.session.get('user_id')
    )

    request_obj = get_object_or_404(
        CollectionRequest,
        id=id,
        user=user
    )

    collection = Collection.objects.filter(
        request=request_obj
    ).first()

    if not collection:
        messages.error(
            request,
            'Feedback can be submitted after collection.'
        )
        return redirect('my_requests')

    if Feedback.objects.filter(
        user=user,
        request=request_obj
    ).exists():
        messages.warning(
            request,
            'Feedback already submitted for this request.'
        )
        return redirect('my_requests')

    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
            message = request.POST.get('message', '').strip()

            if rating < 1 or rating > 5 or not message:
                raise ValueError

            Feedback.objects.create(
                user=user,
                request=request_obj,
                rating=rating,
                message=message
            )

            messages.success(request, 'Feedback submitted successfully!')
            return redirect('my_requests')

        except (ValueError, TypeError):
            messages.error(request, 'Please enter valid feedback details.')

    return render(request, 'submit_feedback.html', {
        'request_obj': request_obj
    })


def user_profile(request):
    if not check_user(request):
        return redirect('login')

    user = get_object_or_404(
        User,
        id=request.session.get('user_id')
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, phone, email, address]):
            messages.error(request, 'All fields are required.')

        elif User.objects.filter(email__iexact=email).exclude(
            id=user.id
        ).exists():
            messages.error(request, 'Email already exists.')

        else:
            user.name = name
            user.phone = phone
            user.email = email
            user.address = address
            user.save()

            request.session['user_name'] = user.name

            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')

    return render(request, 'user_profile.html', {
        'user': user
    })


def check_staff(request):
    return (
        request.session.get('user_type') == 'staff'
        and request.session.get('staff_id') is not None
    )


def my_assignments(request):
    if not check_staff(request):
        return redirect('login')

    staff = get_object_or_404(
        Staff,
        id=request.session.get('staff_id')
    )

    assignments = Assignment.objects.filter(
        staff=staff
    ).select_related(
        'request__user',
        'request__category',
        'request__centre'
    ).order_by('-id')

    return render(request, 'my_assignments.html', {
        'assignments': assignments
    })


def staff_view_assignment(request, id):
    if not check_staff(request):
        return redirect('login')

    staff = get_object_or_404(
        Staff,
        id=request.session.get('staff_id')
    )

    assignment = get_object_or_404(
        Assignment.objects.select_related(
            'request__user',
            'request__category',
            'request__centre',
            'staff'
        ),
        id=id,
        staff=staff
    )

    return render(request, 'staff_view_assignment.html', {
        'assignment': assignment
    })


def update_assignment_status(request, id):
    if not check_staff(request):
        return redirect('login')

    staff = get_object_or_404(
        Staff,
        id=request.session.get('staff_id')
    )

    assignment = get_object_or_404(
        Assignment,
        id=id,
        staff=staff
    )

    if request.method == 'POST':
        status = request.POST.get('status')

        allowed_statuses = [
            'In Progress',
            'Completed'
        ]

        if status not in allowed_statuses:
            messages.error(request, 'Invalid assignment status.')

        elif assignment.status == 'Completed':
            messages.error(
                request,
                'This assignment is already completed.'
            )

        elif assignment.request.status in ['Collected', 'Cancelled']:
            messages.error(
                request,
                'This request cannot be updated.'
            )

        else:
            assignment.status = status
            assignment.save(update_fields=['status'])

            messages.success(
                request,
                'Assignment status updated successfully!'
            )

            return redirect(
                'staff_view_assignment',
                id=assignment.id
            )

    return redirect('staff_view_assignment', id=assignment.id)


def staff_profile(request):
    if not check_staff(request):
        return redirect('login')

    staff = get_object_or_404(
        Staff,
        id=request.session.get('staff_id')
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()

        if not all([name, phone, email, address]):
            messages.error(request, 'All fields are required.')

        elif Staff.objects.filter(
            email__iexact=email
        ).exclude(id=staff.id).exists():
            messages.error(request, 'Email already exists.')

        else:
            staff.name = name
            staff.phone = phone
            staff.email = email
            staff.address = address
            staff.save()

            request.session['staff_name'] = staff.name

            messages.success(
                request,
                'Profile updated successfully!'
            )

            return redirect('staff_profile')

    return render(request, 'staff_profile.html', {
        'staff': staff
    })