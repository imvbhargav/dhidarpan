from . import views
from django.urls import path, re_path
from .feeds import LatestPostsFeed
from .views import UserPostsView, UpdatePostView, deletePost

urlpatterns = [
    path('',views.PostList, name='home'),
    path('add_post/',views.AddPostView,name='add_post'),
    path('user-posts/',UserPostsView,name="user-posts"),
    path('post/edit/<str:slug>',UpdatePostView.as_view(),name="update_post"),
    path('editor/',views.PublishView,name='editor'),
    path('manage-users/',views.ManageUsersView,name='manage_users'),
    path("feed/rss", LatestPostsFeed(),name="post_feed"),
    path('about/',views.AboutView.as_view(),name='about'),
    path('profile/<str:usr>',views.profileView,name='profile'),
    path('our-authors/',views.AuthorsView,name="our-authors"),
    path('subscribe_user/',views.SubscribeView.as_view(),name="subscribe_user"),
    path('post-admin/',views.PaLandView,name='pa-land'),
    path('contact/',views.ContactUs, name='contact'),
    path('policy/',views.PolicyView.as_view(), name='policy'),
    path('archive',views.Archive,name="archive"),
    path('popular',views.PopularList,name="popular"),
    path('category/<str:cate_slug>',views.CategoryList,name="category"),
    path('unsubscribe/',views.unsubscribeView,name="unsubscribe"),
    path('<slug:slug>/',views.post_detail, name='post_detail'),
    path('<int:year>/<int:month>/',
         views.ArticleMonthArchiveView.as_view(month_format='%m'),
         name="post_archive_month"),
]

htmx_urlpatterns = [
    path('delete_post/<str:slug>/',deletePost,name="delete-post"),
    path('like/<str:slug>',views.LikeView,name='like_post'),
    path('follow/<str:username>',views.FollowUser,name='follow_user'),
    path('publish/<str:slug>',views.Publish,name='publish'),
    path('subscribe', views.subscribe, name='subscribe'),
    path('mkauth/<int:usr>',views.MakeAuthor,name="mkauthor"),
    path('mkedit/<int:usr>',views.MakeEditor,name="mkeditor"),
    path('post_comment/<slug:slug>',views.post_comment,name="post_comment"),
]

urlpatterns += htmx_urlpatterns