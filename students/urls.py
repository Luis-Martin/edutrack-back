from rest_framework import routers
from students.api import StudentViewSet

router = routers.DefaultRouter()

router.register('', StudentViewSet, '')

urlpatterns = router.urls
