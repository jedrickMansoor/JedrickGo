from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.payment.models import Payment
from apps.payment.serializers import PaymentSerializer


class PaymentViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Payment.objects.all().order_by('-created_at')
    serializer_class = PaymentSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Payment.objects.all().order_by('-created_at')
        return Payment.objects.filter(order__account=self.request.user.account).order_by('-created_at')
