from django.shortcuts import render, redirect, get_object_or_404
from management.utils import check_admin
from django.utils.timezone import localtime
from django.contrib.auth.models import User
from django.db.models import Sum, Avg, When, Value, Case
from datetime import datetime



from management.models import HubSpaces
from reservation.models import Reservation
from sales_management.models import DailySales
from staff.models import Transactions
from users.models import Feedback

import sweetify

@check_admin
def index(request):
    user_id = request.session.get("user_id")
    spaces = HubSpaces.objects.all()
    reservations = Reservation.objects.filter(status="Pending").count()
    active_staffs = User.objects.filter(is_staff=True, is_superuser=False).exclude(id=user_id).count()
    daily_sales = DailySales.objects.all().order_by('sales_date')
    # Prepare data for Chart.js
    sales_dates = [sale.sales_date.strftime('%Y-%m-%d') for sale in daily_sales]
    total_sales = [float(sale.total_sales) for sale in daily_sales]
    context = {
        "user_id" : user_id,
        "name" : request.session.get("name"),
        "position" : request.session.get("position"),
        "email" : request.session.get("email"),
        'spaces' : spaces,
        "active_staffs" : active_staffs,
        "reservations" : reservations,
        'sales_dates': sales_dates,
        'total_sales': total_sales,
        
    }
    return render(request, 'admin_dashboard.html', context)


@check_admin
def sales(request):
    current_date = datetime.now()

    reservations = Reservation.objects.filter(status="Pending").count()
    daily_sales = DailySales.objects.all().order_by('sales_date')
    average_sales = daily_sales.aggregate(average_daily_sales=Avg('total_sales'))['average_daily_sales']
    current_month_sales = (
        daily_sales.filter(
            sales_date__year=current_date.year, 
            sales_date__month=current_date.month
        )
        .aggregate(total_sales=Sum('total_sales'))['total_sales']
    )
    sales_dates = [sale.sales_date.strftime('%Y-%m-%d') for sale in daily_sales]
    total_sales = [float(sale.total_sales) for sale in daily_sales]
    
    context = {
        "name" : request.session.get("name"),
        'reservations' : reservations,
        'sales_dates': sales_dates,
        'total_sales': total_sales,
        "average_sales": round(average_sales, 2) if average_sales else 0,
        "current_month_sales": round(current_month_sales, 2) if current_month_sales else 0,
    }

    return render(request, 'admin_sales.html', context)


@check_admin
def transactions(request):
    # Get the date from the request or use today's date as the default
    selected_date = request.GET.get('filter_date', localtime().date())

    if isinstance(selected_date, str):
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()

    # Filter transactions by the selected date
    transactions = Transactions.objects.filter(check_out_time__date=selected_date)

    # Calculate total sales for the selected date
    total_sales = Transactions.objects.filter(
        check_out_time__date=selected_date
    ).aggregate(total_bills=Sum('total_payment'))['total_bills'] or 0

    # Calculate the total time for each transaction
    for transaction in transactions:
        total_time = transaction.check_out_time - transaction.check_in_time
        hours, remainder = divmod(total_time.seconds, 3600)
        minutes = remainder // 60
        transaction.total_time = f"{hours} hours {minutes} minutes"

    total_sales = f"{total_sales:,.2f}"

    # Render the template with context
    context = {
        "name" : request.session.get("name"),
        'transactions': transactions,
        'total_sale': total_sales,
        'selected_date': selected_date,
    }
    return render(request, 'admin_transactions.html', context)


@check_admin
def spaces(request):
    spaces = HubSpaces.objects.all()
    context = {
        "name" : request.session.get("name"),
        'spaces' : spaces,
    }

    return render(request, 'admin_spaces.html', context)


@check_admin
def staff(request):
    user_id = request.session.get('user_id')
    staffs = User.objects.exclude(id=user_id)

    print(staffs)
    context = {
        "name" : request.session.get("name"),
        'staffs' : staffs
    }
    return render(request, 'admin_staff.html', context)


@check_admin
def admin_reservations(request):
    reservations = Reservation.objects.exclude(status="Completed").annotate(
    custom_order=Case(
        When(status="Pending", then=Value(1)),
        When(status="Declined", then=Value(2)),
        When(status="Confirmed", then=Value(3)),
        default=Value(4)  # For other statuses like 'Completed' or 'Cancelled'
        )
    ).order_by('custom_order')
    context = {
        "name" : request.session.get("name"),
        'reservations' : reservations,
    }
    return render(request, 'admin_reservations.html', context)


@check_admin
def update_reservation(request, action, reservation_id):
    

    update_reservation = get_object_or_404(Reservation, reservation_id=reservation_id)
    if action == 'CONFIRM':
        update_reservation.status = 'Confirmed'
        update_reservation.save()
        sweetify.toast(request, "Reservation Confirmed", icon="success", timer=3000)
        
    elif action == 'DECLINED':
        update_reservation.status = 'Cancelled'
        update_reservation.save()
        sweetify.toast(request, "Reservation Cancelled", icon="success", timer=3000)
    
    elif action == 'UNDO':
        update_reservation.status = 'Pending'
        update_reservation.save()
        sweetify.toast(request, "Action Reverted", icon="success", timer=3000)

    else:
        sweetify.toast(request, "Invalid Action", icon="error", timer=3000)

    return redirect('admin_reservations')


@check_admin
def feedbacks(request):
    feedbacks = Feedback.objects.all()
    for feedback in feedbacks:
        feedback.rating = range(feedback.rating)

    context = {
        "name" : request.session.get("name"),
        'feedbacks' : feedbacks
    }

    return render(request, 'admin_feedbacks.html', context)












