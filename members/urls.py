from django.urls import path, include, re_path
from members import views as user_view
from members.views import ResetPasswordView

urlpatterns = [
    path('register/',user_view.register,name='register'),
    path('login/',user_view.usr_login,name='login'),
    path('google-login/', user_view.google_sso_login, name='google-sso-login'),
    path('google-callback/', user_view.google_sso_callback, name='google-sso-callback'),
    path('change-password/', user_view.change_password, name='change_password'),
    path('logout/',user_view.logout_view,name='logout'),
    path('edit_user/',user_view.edit_user_profile,name='edit-user'),
    path('delete_user_confirm',user_view.DeleteView.as_view(),name="confirm_delete_user"),
    path('delete_user/',user_view.delete_user,name="delete-user"),
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('activate/<uidb64>/<token>', user_view.activate, name='activate'),
]

htmx_urlpatterns = [
    path('check_username/',user_view.check_username,name="check-username"),
    path('check_email/',user_view.check_email,name="check-email"),
    path('deletedp/<int:uid>',user_view.deleteDp,name="deletedp"),
    path('updatedp/<int:uid>',user_view.updateDp,name="updatedp"),
]

urlpatterns += htmx_urlpatterns