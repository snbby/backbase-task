from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter

from my_currency.viewsets import (ConvertAmountViewSet,
                                  CurrenciesV1ModelViewSet,
                                  CurrenciesV2ModelViewSet,
                                  CurrencyRatesViewSet, LaunchAsyncHistoryTask,
                                  ProvidersModelviewSet)

routerv1 = DefaultRouter()
routerv1.register('currencies', CurrenciesV1ModelViewSet, basename='currencies-v1')
routerv1.register('providers', ProvidersModelviewSet, basename='providers')
routerv1.register('currency-rates', CurrencyRatesViewSet, basename='currency-rates')
routerv1.register('convert-amount', ConvertAmountViewSet, basename='convert-amount')
routerv1.register('launch-history-task', LaunchAsyncHistoryTask, basename='launch-history-task')

routerv2 = DefaultRouter()
routerv2.register('currencies', CurrenciesV2ModelViewSet, basename='currencies-v2')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(routerv1.urls)),
    path('api/v2/', include(routerv2.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
