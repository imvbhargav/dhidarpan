# Import the requirements
from django.core.mail import send_mail, BadHeaderError
from django.http.response import BadHeaderError
from django.shortcuts import render, redirect
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.dates import MonthArchiveView
from .models import Post, Comment, Category, ProfileInfo
from .forms import CommentForm, ContactForm, PostForm, UpdateForm 
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect 
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.db.models import Q
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Subscribers
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site

# Class based views
# Serves the template for confirming the unsubscribe
class UnsubscribeView(TemplateView):
    template_name = 'unsubscribe.html'

# Serves the about page
class AboutView(TemplateView):
    template_name = 'about.html'

# Serves the Terms and conditions page
class PolicyView(TemplateView):
    template_name = 'policy.html'

# Serves the template for confirming the subscribe
class SubscribeView(TemplateView):
    template_name = 'sub_user.html'

# Serves the template for upadating posts
class UpdatePostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    permission_required = ('blog.add_post', 'blog.change_post')
    def test_func(self):
        return self.request.user.has_perm('blog.add_post') or self.request.user.has_perm('blog.change_post')
    login_url = 'login'
    model = Post
    template_name = 'update_post.html'
    form_class = UpdateForm

# Serves the post archive page
class ArticleMonthArchiveView(MonthArchiveView):
    queryset = Post.objects.all()
    paginate_by = 2
    date_field = "created_on"
    allow_future = True
    template_name = 'post_archive_month.html'

# Function based views
# Function lists the post / Handles home page
def PostList(request):
    search_post = request.GET.get('search')
    if search_post:
        object_list = Post.objects.filter(Q(title__icontains=search_post) | Q(content__icontains=search_post))[:15]
        popular_post = 0
        ol_count = object_list.count()
    else:
        latest_post = Post.objects.filter(status=1).order_by('-created_on')[:1]
        popular_post = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:1]
        latest_tech_list = Post.objects.filter(categories = 1).order_by('-created_on')[:3]
        latest_phil_list = Post.objects.filter(categories = 2).order_by('-created_on')[:2]
        latest_spir_list = Post.objects.filter(categories = 3).order_by('-created_on')[:2]
        latest_fict_list = Post.objects.filter(categories = 4).order_by('-created_on')[:3]
        categories_list = Category.objects.filter(status=1).order_by('-created_on')
        ol_count = -1
    if search_post:
        return_obj = {
                        'post_list': object_list,
                        'ol_count':ol_count
                    }
    else:
        return_obj = {
                        'latest_post':latest_post,
                        'popular_post':popular_post,
                        'latest_tech_list':latest_tech_list,
                        'latest_phil_list':latest_phil_list,
                        'latest_spir_list':latest_spir_list,
                        'latest_fict_list':latest_fict_list,
                        'categories_list':categories_list,
                        'ol_count':ol_count
                    }
    return render(request,
                  'index.html',
                  return_obj)

# Function lists articles by category
def CategoryList(request, cate_slug):
    category = post = get_object_or_404(Category, slug=cate_slug)
    category_list = Post.objects.filter(status=1, categories=category.id).order_by('-created_on')
    paginator = Paginator(category_list, 6)  # 9 posts in each page
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post_list = paginator.page(paginator.num_pages)
    return render(
        request,
        'category.html',
        {
            'page': page,
            'post_list': post_list,
            'category':category,
        }
    )

# Function lists the popular posts
def PopularList(request):
    object_list = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count')
    paginator = Paginator(object_list, 6)  # 6 posts in each page
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post_list = paginator.page(paginator.num_pages)
    return render(request,
                  'popular.html',
                  {'page': page,
                   'post_list': post_list,
                   'ol_count':object_list.count})

# Function lists the posts of logged in user
@login_required(login_url='/members/login/')
def UserPostsView(request):
    usr = request.user
    user_posts_active = Post.objects.filter(author=usr,status=1).order_by('-created_on')
    user_posts_draft = Post.objects.filter(author=usr,status=0).order_by('-created_on')
    draft_count = user_posts_draft.count()
    active_count = user_posts_active.count()
    return render(request, 'post-creation.html',{   'user_posts_active':user_posts_active,
                                                    'user_posts_draft':user_posts_draft,
                                                    'draft_count':draft_count,
                                                    'active_count':active_count,
    })

# Function to serve the request to display the full post, takes slug of required post as parameter
def post_detail(request, slug):
    template_name = 'post_detail.html'
    post = get_object_or_404(Post, slug=slug)
    object_list = Post.objects.filter(status=1, categories=post.categories.id).order_by('-created_on')[:5]
    if not post.status:
        if not request.user == post.author:
            return redirect('home')
    likes = post.total_likes()
    liked = False
    followed = False
    if post.likes.filter(id=request.user.id).exists():
        liked = True
    author = User.objects.get(id=post.author.id)
    instance = ProfileInfo.objects.get(user=author)
    if instance.follows.filter(id=request.user.id).exists():
        followed = True 
    comments = post.comments.filter(active=True,parent__isnull=True)
    new_comment = None
    reply_comment = None
    comment_form = CommentForm()

    return render(request, template_name, { 'post': post,
                                            'comments': comments,
                                            'reply_comment': reply_comment,
                                            'new_comment': new_comment,
                                            'comment_form': comment_form,
                                            'total_likes':likes,
                                            'liked':liked,
                                            'usr':author,
                                            'followed':followed,
                                            'more':object_list,
    })

# Function to handle the posting of comment
def post_comment(request, slug):
    template_name = "comments_model.html"
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True,parent__isnull=True)
    new_comment = None
    reply_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            parent_obj = None
            try:
                parent_id = int(request.POST.get('parent_id'))
            except:
                parent_id = None
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                if parent_obj:
                    reply_comment = comment_form.save(commit=False)
                    reply_comment.parent = parent_obj
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            comment_form = CommentForm()
            return render(request, template_name, { 'post':post,
                                                    'comments':comments,
                                                    'comment_form':comment_form,
                                                    'new_comment': new_comment,
                                                    'reply_comment': reply_comment,})
    else:
        comment_form = CommentForm()

    return render(request, template_name, { 'post':post,
                                            'comments':comments,
                                            'comment_form':comment_form,
                                            'new_comment': new_comment,
                                            'reply_comment': reply_comment,})

# Function to add new post, user must be logged in
@login_required(login_url='/members/login/')
def AddPostView(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            slug = form.cleaned_data['slug']
            return HttpResponseRedirect(reverse('post_detail', args=[str(slug)]))
        else:
            return render(request, 'add_post.html',{'form':form,'msg':'Some error occured, Maybe post with TITLE already exists!'})
    form = PostForm()
    return render(request, 'add_post.html',{'form':form})

# Function to serve the profile/admin view, user must be logged in
@login_required(login_url='/members/login/')
def PaLandView(request):
    publishedPosts = Post.objects.filter(status = 1, author=request.user)
    pPostsCount = publishedPosts.count()
    draftPosts = Post.objects.filter(status = 0, author=request.user)
    dPostsCount = draftPosts.count()
    lastPublished = Post.objects.filter(status = 1, author=request.user).order_by('-created_on')[:1]

    pi = ProfileInfo.objects.get(user=request.user)
    isSubscribed = pi.isSubscriber

    return render(request, 'pa-land.html',{'publishedPosts':publishedPosts,
                                           'pPostsCount':pPostsCount,
                                           'draftPosts':draftPosts,
                                           'dPostsCount':dPostsCount,
                                           'lastPublished':lastPublished,
                                           'isSubscribed':isSubscribed})

# Function to display the contact us page
def ContactUs(request):
    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject = "Website Mail"
            msg_name = contact_form.cleaned_data['first_name'] 
            email_address = contact_form.cleaned_data['email_address']
            body = {
                'first_name' : 'Name: ' + msg_name + ' ' +contact_form.cleaned_data['last_name'],
                'email_address' : 'Email: ' + email_address,
                'message' : 'Message: ' + contact_form.cleaned_data['message'],
            }
            message = "\n".join(body.values())

            try:
                send_mail(subject, message, 'mailsenderforbv@gmail.com',['imbhargavjois@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
        contact_form = ContactForm()
        return render(request, "contact.html", {'contact_form': contact_form, 'msg_name':msg_name})
    contact_form = ContactForm()
    return render(request, "contact.html", {'contact_form': contact_form})

# Function to display the profile of other users to user
def profileView(request, usr):
    duser = User.objects.get(username=usr)
    posts = Post.objects.filter(author=duser.id, status=1).order_by('-created_on')
    followed = False
    instance = ProfileInfo.objects.get(user=duser)

    paginator = Paginator(posts, 6)  # 6 posts in each page
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
            # If page is not an integer deliver the first page
        post_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        post_list = paginator.page(paginator.num_pages)

    if instance.follows.filter(id=request.user.id).exists():
        followed = True 
    return render(request, 'profile_view.html',{'usr':duser,'posts':post_list, 'followed':followed,'page':page})

# Function to delete the post, user must be admin/editor or the creator of that post
@login_required(login_url='/members/login/')
def deletePost(request,slug):
    if request.method == 'DELETE':
        Post.objects.get(slug=slug).delete()
        usr=request.user.id
        user_posts_active = Post.objects.filter(author=usr,status=1).order_by('-created_on')
        user_posts_draft = Post.objects.filter(author=usr,status=0).order_by('-created_on')
        draft_count = user_posts_draft.count()
        active_count = user_posts_active.count()
        return render(request, 'post-creation-model.html',{'user_posts_active':user_posts_active,
                                                            'user_posts_draft':user_posts_draft,
                                                            'usr_id':usr,
                                                            'draft_count':draft_count,
                                                            'active_count':active_count,
        })
    if request.method == 'POST':
        Post.objects.get(slug=slug).delete()
        usr=request.user.id
        user_posts_active = Post.objects.filter(status=1).order_by('-created_on')
        user_posts_draft = Post.objects.filter(status=0).order_by('-created_on')
        draft_count = user_posts_draft.count()
        active_count = user_posts_active.count()
        return render(request, 'editor.html',{'active_posts':user_posts_active,
                                                'draft_posts':user_posts_draft,
                                                'draft_count':draft_count,
                                                'active_count':active_count,
        })
    return redirect('pa-land')

# Function handle the request to like a post
def LikeView(request, slug):
    if request.method == "POST":
        instance = Post.objects.get(slug=slug)
        if not instance.likes.filter(id=request.user.id).exists():
            instance.likes.add(request.user)
            instance.save() 
            liked = True
            likes = instance.total_likes()
            return render( request, 'likes.html', context={'post':instance,'liked':liked,'total_likes':likes})
        else:
            instance.likes.remove(request.user)
            instance.save()
            liked = False 
            likes = instance.total_likes()
            return render( request, 'likes.html', context={'post':instance,'liked':liked,'total_likes':likes})

# Function to publish the post, user must be editor/admin
@login_required(login_url='/members/login/')
def Publish(request,slug):
    if request.method == 'POST':
        pst = Post.objects.get(slug=slug)
        pst.status = 1 if pst.status == 0 else 0
        pst.save()
        
        if pst.status:
            email_list = list(User.objects.values_list("email", flat=True))
            d = {'slug':slug}
            htmly = get_template('Notif-Email.html')
            subject, from_email, to = 'Welcome to Dhi Darpan', 'mailsenderforbv@gmail.com', email_list
            html_content = htmly.render(d)
            msg = EmailMultiAlternatives(subject, html_content, from_email, to)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        draft_posts = Post.objects.filter(status=0).order_by('-created_on')
        active_posts = Post.objects.filter(status=1).order_by('-created_on')
        draft_count = draft_posts.count()
        active_count = active_posts.count()
        return render(request, 'editor.html',{'active_posts':active_posts,'draft_posts':draft_posts,'draft_count':draft_count,
                                                'active_count':active_count,})
    return redirect('pa-land')

# Function for showing the posts for editor
@login_required(login_url='/members/login/')
@permission_required('blog.change_post', login_url='/members/login/')
def PublishView(request):
    if request.user.has_perm('blog.change_post'):
        draft_posts = Post.objects.filter(status=0).order_by('-created_on')
        active_posts = Post.objects.filter(status=1).order_by('-created_on')
        draft_count = draft_posts.count()
        active_count = active_posts.count()
        return render(request, 'editor-main.html',{'active_posts':active_posts,'draft_posts':draft_posts,'draft_count':draft_count,
                                                'active_count':active_count,}) 
    return redirect('pa-land')

# Function to show user management for admin
@login_required(login_url='/members/login/')
@permission_required('auth.change_user', login_url='/members/login/')
def ManageUsersView(request):
    users = User.objects.all().exclude(groups__id=1).exclude(groups__id=2)
    authors = User.objects.filter(groups__id=1)
    editors = User.objects.filter(groups__id=2)
    return render(request, 'manage_users.html',{'authors':authors,'editors':editors,'users':users,'users_count':users.count(),
    'authors_count':authors.count(),'editors_count':editors.count(),})

# Function to make a user to author
def MakeAuthor(request,usr):
    if request.method == 'POST':
        myuser = User.objects.get(id=usr)
        users = User.objects.all().exclude(groups__id=1).exclude(groups__id=2).order_by('date_joined')
        authors = User.objects.filter(groups__id=1).order_by('date_joined')
        editors = User.objects.filter(groups__id=2).order_by('date_joined')
        if myuser.groups.filter(id=1).exists():
            myuser.groups.remove(1)
            myuser.save()
        else:
            myuser.groups.add(1)
            myuser.save()
        return render( request, 'manage_user_model.html',{'authors':authors,'editors':editors,'users':users,'users_count':users.count(),
                                'authors_count':authors.count(),'editors_count':editors.count(),})
    return redirect('home')

# Function to make a user to editor
def MakeEditor(request,usr):
    if request.method == 'POST':
        myuser = User.objects.get(id=usr)
        users = User.objects.all().exclude(groups__id=1).exclude(groups__id=2).order_by('date_joined')
        authors = User.objects.filter(groups__id=1).order_by('date_joined')
        editors = User.objects.filter(groups__id=2).order_by('date_joined')
        if myuser.groups.filter(id=2).exists():
            myuser.groups.remove(2)
            myuser.save()
        else:
            myuser.groups.add(2)
            myuser.save()
        return render( request, 'manage_user_model.html',{'authors':authors,'editors':editors,'users':users,'users_count':users.count(),
                                'authors_count':authors.count(),'editors_count':editors.count(),})
    return redirect('home')

# Function to display all the authors of blog
def AuthorsView(request):
    search_post = request.GET.get('search')
    if search_post:
        authors = User.objects.filter(Q(username__icontains=search_post) | Q(first_name__icontains=search_post) | Q(last_name__icontains=search_post))
    else:
        authors = User.objects.filter(groups__id=1)
    return render(request, 'our_authors.html',{'authors':authors,'users_count':authors.count(),})

# Function renders the archive view
def Archive(request):
    return render(request, 'archive.html')

# Function to handles request to follow a user 
def FollowUser(request, username):
    if request.method == "POST":
        author = User.objects.get(username=username)
        instance = ProfileInfo.objects.get(user=author)
        if not instance.follows.filter(id=request.user.id).exists():
            instance.follows.add(request.user)
            instance.save()
            followed = True
            return render( request, 'follow.html', {'usr':author,'followed':followed})
        else:
            instance.follows.remove(request.user)
            instance.save()
            followed = False 
            return render( request, 'follow.html', {'usr':author,'followed':followed})

# Function to handles request to subscribe a user/email to newsletter
def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)

        if not email:
            messages.error(request, "You must type email to subscribe to a Newsletter")
            return render( request, 'newsletter.html') 

        subscribe_user = Subscribers.objects.filter(email=email).first()
        if subscribe_user:
            messages.error(request, f"{email} email address is already subscriber.")
            return render( request, 'newsletter.html') 

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return render( request, 'newsletter.html') 

        mail_subject = 'Succesfully Subscribed to Dhi Darpan Newsletter.'
        message = render_to_string('newsletter-sub.html', {
            'email': email,
            'domain': get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http'
        })
        send_email = EmailMessage(mail_subject, message, to=[email])
        if not send_email.send():
            messages.error(request, f'Problem sending confirmation email to {email}, check if you typed it correctly.')
            return render( request, 'newsletter.html')

        subscribe_model_instance = Subscribers()
        subscribe_model_instance.email = email
        subscribe_model_instance.save()

        if get_user_model().objects.filter(email=email).first():
            user = get_user_model().objects.filter(email=email).first()
            profileInfo = ProfileInfo.objects.get(user=user)
            profileInfo.isSubscriber = True
            profileInfo.save()

        messages.success(request, f'{email} email was successfully subscribed to our newsletter!')
        return render( request, 'newsletter.html')

# Function handles the view to unsubscribe the user/email from newsletter
def unsubscribeView(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        subscribe_user = Subscribers.objects.filter(email=email)

        try:
            validate_email(email)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return render( request, 'unsubcribe.html') 
        if not subscribe_user:
            messages.error(request, f"{email} is not a subscriber.")
            return render( request, 'unsubcribe.html')
        
        mail_subject = 'Succesfully unsubscribed from Dhi Darpan Newsletter.'
        message = render_to_string('newsletter-unsub.html', {
            'email': email,
            'domain': get_current_site(request).domain,
            'protocol': 'https' if request.is_secure() else 'http'
        })
        send_email = EmailMessage(mail_subject, message, to=[email])
        if not send_email.send():
            messages.error(request, f'Problem unsubscribing {email}, try again later.')
            return render( request, 'unsubcribe.html')

        subscribe_user.delete()

        if get_user_model().objects.filter(email=email).first():
            user = get_user_model().objects.filter(email=email).first()
            profileInfo = ProfileInfo.objects.get(user=user)
            profileInfo.isSubscriber = False
            profileInfo.save()

        messages.success(request, f"{email} has been successfully unsubscribed.")
        return render( request, 'unsubcribe.html')
    else:
        return render( request, 'unsubcribe.html')