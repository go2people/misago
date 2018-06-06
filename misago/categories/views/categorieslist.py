from django.shortcuts import render
from django.urls import reverse

from misago.categories.serializers import CategoryWithPosterSerializer \
    as CategorySerializer
from misago.categories.utils import get_categories_tree

from userprofiles.decorators import (active_login_required,
                                     valid_account_required)


@active_login_required
@valid_account_required
def categories(request):
    categories_tree = get_categories_tree(request.user, join_posters=True)

    request.frontend_context.update({
        'CATEGORIES': CategorySerializer(
            categories_tree, many=True, context={'request': request}).data,
        'CATEGORIES_API': reverse('misago:api:category-list'),
    })
    for category in categories_tree:
        for subcategory in category.subcategories:
            subcategory.subscription = False
    return render(request, 'misago/categories/list.html', {
        'categories': categories_tree,
    })
