from django.conf.urls import url
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^jwt-auth/', obtain_jwt_token),
    url(r'^jwt-refresh/', refresh_jwt_token),
    url(r'^jwt-verify/', verify_jwt_token),
]
