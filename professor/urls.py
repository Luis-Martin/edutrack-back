from rest_framework import routers
from professor.api import ProfessorViewSet

router = routers.DefaultRouter()

router.register('', ProfessorViewSet, '')

urlpatterns = router.urls
