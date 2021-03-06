from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.


# middleware -to verify token present in headers and pass user in request object
# create/update bussiness ,receipt details
from rest_framework import status
from rest_framework.decorators import api_view

from customers.models import CustomerDetails
from customers.serializers import CustomersSerializer
from userManagement.models import User
from userManagement.serializers import UserSerializer
from .models import Receipts, Products
from .serializers import ReceiptSerializer, ProductSerializer


def add_one_to_receipt_number(user):
    """
    Returns the next default value for the `ones` field, starts with
    1
    """
    largest = Receipts.objects.filter(user=user).order_by('receipt_number').last()
    if not largest:
        return 1
    return largest.receipt_number + 1


@api_view(['POST'])
def create_receipt(request):
    if request.method == 'POST':
        print(request.user_id)
        data = {
            'user': request.user_id,
            'receipt_number': add_one_to_receipt_number(request.user_id),
            'customer': request.data['customerId']
        }
        print(data)
        serializer = ReceiptSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_product_info_to_receipt(request):
    # send the receipt id
    if request.method == 'POST':
        # user
        data = {
            'receipt': request.data['receiptId'],
            'name': request.data['name'],
            'quantity': request.data['quantity'],
            'amount': request.data['amount']
        }
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_receipt(request):
    # send the receipt id
    if request.method == 'GET':
        try:
            recipt = Receipts.objects.filter(user=request.user_id)
            if recipt:
                user = User.objects.get(id=request.user_id)
                userData = UserSerializer(user, many=False).data
                receipts = ReceiptSerializer(recipt, many=True).data
                for data in receipts:
                    data['user'] = {
                        'id': userData['id'],
                        'name': userData['name'],
                        'email_address': userData['email_address']
                    }
                    products = Products.objects.filter(receipt=data['id'])
                    products_data = ProductSerializer(products, many=True).data
                    data['products'] = products_data
                    print(data['products'])
                    customer = CustomerDetails.objects.get(pk=data['customer'])
                    data['customer'] = CustomersSerializer(customer, many=False).data
                    data['total'] = sum(c['amount'] for c in data['products'])
                return JsonResponse({
                    "message": "Retreived all receipts",
                    "data": receipts}, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "message": "There are no receipts created"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return JsonResponse({
                "message": error}, status=status.HTTP_400_BAD_REQUEST)
