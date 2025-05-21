from django.shortcuts import render, get_object_or_404
from .models import Post
from django.views.generic import ListView
from .forms import EmailPostForm
from django.core.mail import send_mail

class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day)

    return render( request, 'blog/post/detail.html', {'post': post } )

def post_share(request, post_id):
    # Retrieve the post by its ID, ensuring it is published
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    sent = False  # Track if the email was sent

    if request.method == 'POST':
        # If form was submitted via POST
        form = EmailPostForm(request.POST)

        if form.is_valid():
            # If form data is valid
            cd = form.cleaned_data  # Get validated and cleaned data

            # Build full URL to the post
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )

            # Create email subject and message
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )

            # Send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=None,  # Use DEFAULT_FROM_EMAIL
                recipient_list=[cd['to']]
            )

            sent = True  # Mark email as sent

    else:
        # If GET request, show empty form
        form = EmailPostForm()

    # Render the share page with the post, form, and sent flag
    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )
