from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'reduced_description',
    )

    def reduced_description(self, object):
        """
        Укорачивает описание.
        Не смог найти ничего лучше,
        стаковерфлоу помог таким решением :(.
        """
        return object.description[:100] + '...'

    reduced_description.short_description = 'Описание'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'created',
        'author',
        'text'
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
