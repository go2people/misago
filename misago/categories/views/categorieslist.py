from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from misago.categories.serializers import CategoryWithPosterSerializer as CategorySerializer
from misago.categories.utils import get_categories_tree


@login_required
def categories(request):
    categories_tree = get_categories_tree(request.user, join_posters=True)

    request.frontend_context.update({
        'CATEGORIES': CategorySerializer(categories_tree, many=True, context={'request': request}).data,
        'CATEGORIES_API': reverse('misago:api:category-list'),
    })
    for category in categories_tree:
        for subcategory in category.subcategories:
            subcategory.subscription = False
    return render(request, 'misago/categories/list.html', {
        'categories': categories_tree,
    })
