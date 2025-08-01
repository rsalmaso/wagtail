# Settings

The `wagtail.contrib.settings` module allows you to define models that hold
settings which are either common across all site records or specific to each site.

Settings are editable by administrators within the Wagtail admin and can be
accessed in code as well as in templates.

## Installation

Add `wagtail.contrib.settings` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS += [
    'wagtail.contrib.settings',
]
```

**Note:** If you are using `settings` within templates, you will also need to
update your `TEMPLATES` settings (discussed later in this page).

## Defining settings

Create a model that inherits from either:

-   `BaseGenericSetting` for generic settings across all sites
-   `BaseSiteSetting` for site-specific settings

and register it using the `register_setting` decorator:

```python
from django.db import models
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)

@register_setting
class GenericSocialMediaSettings(BaseGenericSetting):
    facebook = models.URLField()

@register_setting
class SiteSpecificSocialMediaSettings(BaseSiteSetting):
    facebook = models.URLField()
```

Links to your settings will appear in the Wagtail admin 'Settings' menu.

(edit_handlers_settings)=

## Edit handlers

Settings use edit handlers much like the rest of Wagtail.
Add a `panels` setting to your model defining all the edit handlers required:

```python
@register_setting
class GenericImportantPages(BaseGenericSetting):
    donate_page = models.ForeignKey(
        'wagtailcore.Page', null=True, on_delete=models.SET_NULL, related_name='+'
    )
    sign_up_page = models.ForeignKey(
        'wagtailcore.Page', null=True, on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('donate_page'),
        FieldPanel('sign_up_page'),
    ]

@register_setting
class SiteSpecificImportantPages(BaseSiteSetting):
    donate_page = models.ForeignKey(
        'wagtailcore.Page', null=True, on_delete=models.SET_NULL, related_name='+'
    )
    sign_up_page = models.ForeignKey(
        'wagtailcore.Page', null=True, on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('donate_page'),
        FieldPanel('sign_up_page'),
    ]
```

You can also customize the edit handlers [like you would do for `Page` model](customizing_the_tabbed_interface) with a custom `edit_handler` attribute:

```python
from wagtail.admin.panels import TabbedInterface, ObjectList

@register_setting
class MySettings(BaseGenericSetting):
    # ...
    first_tab_panels = [
        FieldPanel('field_1'),
    ]
    second_tab_panels = [
        FieldPanel('field_2'),
    ]

    edit_handler = TabbedInterface([
        ObjectList(first_tab_panels, heading='First tab'),
        ObjectList(second_tab_panels, heading='Second tab'),
    ])
```

## Permissions

Settings are editable by superusers, and any users who have been granted "change" permission on the setting model. Additionally, for models extending `BaseSiteSetting`, permissions can be assigned for individual sites through the Groups area of the admin, under Settings.

```{versionadded} 7.1
The ability to assign permissions for individual sites was added.
```

## Appearance

You can change the label used in the menu by changing the
`verbose_name` of your model.

You can add an icon to the menu by passing an `icon` argument to the
`register_setting` decorator:

```python
@register_setting(icon='placeholder')
class GenericSocialMediaSettings(BaseGenericSetting):
    ...
    class Meta:
        verbose_name = "Social media settings for all sites"

@register_setting(icon='placeholder')
class SiteSpecificSocialMediaSettings(BaseSiteSetting):
    ...
    class Meta:
        verbose_name = "Site-specific social media settings"
```

Wagtail’s default icon set can be seen in our [icons overview](icons). All icons available in a given project are displayed in the [styleguide](styleguide).

## Using the settings

Settings can be used in both Python code and in templates.

### Using in Python

#### Generic settings

If you require access to a generic setting in a view, the
`BaseGenericSetting.load()` method allows you to retrieve the generic
settings:

```python
def view(request):
    social_media_settings = GenericSocialMediaSettings.load(request_or_site=request)
    ...
```

The `request_or_site` argument is optional - if this is passed, and is a request object, the result will be cached on the request to avoid repeated database lookups within the same request.

(site_settings)=

#### Site-specific settings

If you require access to a site-specific setting in a view, the
`BaseSiteSetting.for_request()` method allows you to retrieve the site-specific
settings for the current request:

```python
def view(request):
    social_media_settings = SiteSpecificSocialMediaSettings.for_request(request=request)
    ...
```

In places where the request is unavailable, but you know the `Site` you wish to
retrieve settings for, you can use
`BaseSiteSetting.for_site` instead:

```python
def view(request):
    social_media_settings = SiteSpecificSocialMediaSettings.for_site(site=user.origin_site)
    ...
```

(using_settings_in_django_templates)=

### Using in Django templates

Add the `wagtail.contrib.settings.context_processors.settings`
context processor to your settings:

```python
TEMPLATES = [
    {
        ...

        'OPTIONS': {
            'context_processors': [
                ...

                'wagtail.contrib.settings.context_processors.settings',
            ]
        }
    }
]
```

Then access the generic settings through `{{ settings }}`:

```html+django
{{ settings.app_label.GenericSocialMediaSettings.facebook }}
{{ settings.app_label.SiteSpecificSocialMediaSettings.facebook }}
```

**Note:** Replace `app_label` with the label of the app containing your
settings model.

If you are not in a `RequestContext`, then context processors will not have
run, and the `settings` variable will not be available. To get the
`settings`, use the provided `{% get_settings %}` template tag.

```html+django
{% load wagtailsettings_tags %}
{% get_settings %}
{{ settings.app_label.GenericSocialMediaSettings.facebook }}
{{ settings.app_label.SiteSpecificSocialMediaSettings.facebook }}
```

By default, the tag will create or update a `settings` variable in the
context. If you want to assign to a different context variable instead, use
`{% get_settings as other_variable_name %}`:

```html+django
{% load wagtailsettings_tags %}
{% get_settings as wagtail_settings %}
{{ wagtail_settings.app_label.GenericSocialMediaSettings.facebook }}
{{ wagtail_settings.app_label.SiteSpecificSocialMediaSettings.facebook }}
```

### Using in Jinja2 templates

Add `wagtail.contrib.settings.jinja2tags.settings` extension to your
Jinja2 settings:

```python
TEMPLATES = [
    ...

    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'OPTIONS': {
            'extensions': [
                ...

                'wagtail.contrib.settings.jinja2tags.settings',
            ],
        },
    }
]
```

Then access the settings through the `settings()` template function:

```html+jinja
{{ settings("app_label.GenericSocialMediaSettings").facebook }}
{{ settings("app_label.SiteSpecificSocialMediaSettings").facebook }}
```

**Note:** Replace `app_label` with the label of the app containing your
settings model.

If there is no `request` available in the template at all, you can use the
settings for the default site instead:

```html+jinja
{{ settings("app_label.GenericSocialMediaSettings", use_default_site=True).facebook }}
{{ settings("app_label.SiteSpecificSocialMediaSettings", use_default_site=True).facebook }}
```

**Note:** You can not reliably get the correct settings instance for the
current site from this template tag if the request object is not available.
This is only relevant for multi-site instances of Wagtail.

You can store the settings instance in a variable to save some typing,
if you have to use multiple values from one model:

```html+jinja
{% with generic_social_settings=settings("app_label.GenericSocialMediaSettings") %}
    Follow us on Facebook at {{ generic_social_settings.facebook }},
    or Instagram at @{{ generic_social_settings.instagram }}.
{% endwith %}

{% with site_social_settings=settings("app_label.SiteSpecificSocialMediaSettings") %}
    Follow us on Facebook at {{ site_social_settings.facebook }},
    or Instagram at {{ site_social_settings.instagram }}.
{% endwith %}
```

Or, alternately, using the `set` tag:

```html+jinja
{% set generic_social_settings=settings("app_label.GenericSocialMediaSettings") %}
{% set site_social_settings=settings("app_label.SiteSpecificSocialMediaSettings") %}
```

## Utilizing `select_related` to improve efficiency

For models with foreign key relationships to other objects (for example pages),
which are very often needed to output values in templates, you can set
the `select_related` attribute on your model to have Wagtail utilize
Django's [`QuerySet.select_related()`](django.db.models.query.QuerySet.select_related)
method to fetch the settings object and related objects in a single query.
With this, the initial query is more complex, but you will be able to
freely access the foreign key values without any additional queries,
making things more efficient overall.

Building on the `GenericImportantPages` example from the previous section, the
following shows how `select_related` can be set to improve efficiency:

```python
@register_setting
class GenericImportantPages(BaseGenericSetting):

    # Fetch these pages when looking up GenericImportantPages for or a site
    select_related = ["donate_page", "sign_up_page"]

    donate_page = models.ForeignKey(
        'wagtailcore.Page', null=True, on_delete=models.SET_NULL, related_name='+'
    )
    sign_up_page = models.ForeignKey(
        'wagtailcore.Page', null=True, on_delete=models.SET_NULL, related_name='+'
    )

    panels = [
        FieldPanel('donate_page'),
        FieldPanel('sign_up_page'),
    ]
```

With these additions, the following template code will now trigger
a single database query instead of three (one to fetch the settings,
and two more to fetch each page):

```html+django
{% load wagtailcore_tags %}
{% pageurl settings.app_label.GenericImportantPages.donate_page %}
{% pageurl settings.app_label.GenericImportantPages.sign_up_page %}
```

## Utilizing the `page_url` setting shortcut

If, like in the previous section, your settings model references pages,
and you often need to output the URLs of those pages in your project,
you can likely use the setting model's `page_url` shortcut to do that more
cleanly. For example, instead of doing the following:

```html+django
{% load wagtailcore_tags %}
{% pageurl settings.app_label.GenericImportantPages.donate_page %}
{% pageurl settings.app_label.GenericImportantPages.sign_up_page %}
```

You could write:

```html+django
{{ settings.app_label.GenericImportantPages.page_url.donate_page }}
{{ settings.app_label.GenericImportantPages.page_url.sign_up_page }}
```

Using the `page_url` shortcut has a few of advantages over using the tag:

1.  The 'specific' page is automatically fetched to generate the URL,
    so you don't have to worry about doing this (or forgetting to do this)
    yourself.
2.  The results are cached, so if you need to access the same page URL
    in more than one place (for example in a form and in footer navigation), using
    the `page_url` shortcut will be more efficient.
3.  It's more concise, and the syntax is the same whether using it in templates
    or views (or other Python code), allowing you to write more consistent
    code.

When using the `page_url` shortcut, there are a couple of points worth noting:

1.  The same limitations that apply to the `{% pageurl %}` tag apply to the
    shortcut: If the settings are accessed from a template context where the
    current request is not available, all URLs returned will include the
    site's scheme/domain, and URL generation will not be quite as efficient.
2.  If using the shortcut in views or other Python code, the method will
    raise an `AttributeError` if the attribute you request from `page_url`
    is not an attribute on the settings object.
3.  If the settings object DOES have the attribute, but the attribute returns
    a value of `None` (or something that is not a `Page`), the shortcut
    will return an empty string.

(enabling_previews_for_settings)=

## Enabling previews for settings

[Similar to snippets](wagtailsnippets_making_snippets_previewable), if a setting model inherits from {class}`~wagtail.models.PreviewableMixin`, Wagtail will automatically add a live preview panel in the editor. In addition to inheriting the mixin, the model must also override {meth}`~wagtail.models.PreviewableMixin.get_preview_template` or {meth}`~wagtail.models.PreviewableMixin.serve_preview`.

When the setting is used within the preview template [via the context processor](using_settings_in_django_templates), Wagtail will automatically reflect any changes to the settings within the preview. This allows you to reuse your existing templates, such as the template of a Wagtail {class}`~wagtail.models.Page`, and see how the settings affect the page in real-time.

All features provided by the `PreviewableMixin` are available, including the ability to have different {attr}`~wagtail.models.PreviewableMixin.preview_modes` and to use the {meth}`~wagtail.models.PreviewableMixin.get_preview_context` method to add additional context variables.

```python
from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    BaseSiteSetting,
    register_setting,
)
from wagtail.models import PreviewableMixin

from myproject.blog.models import BlogPage
from myproject.home.models import HomePage


@register_setting
class GenericSocialMediaSettings(PreviewableMixin, BaseGenericSetting):
    def get_preview_template(self, preview_mode):
        # Custom template specifically for this setting's preview
        return "settings/generic/social_media.html"


@register_setting
class SiteSpecificSocialMediaSettings(PreviewableMixin, BaseSiteSetting):
    preview_modes = [("home", "Home page"), ("blog", "Blog page")]
    _models_for_preview = {
        "home": HomePage,
        "blog": BlogPage,
    }

    def get_preview_context(self, request, mode_name):
        # Add a Page instance to the context for the preview
        context = super().get_preview_context(request, mode_name)
        context["page"] = (
            self._models_for_preview[mode_name]
            .objects.descendant_of(self.site.root_page, inclusive=True)
            .first()
        )
        return context

    def get_preview_template(self, request, mode_name):
        # Reuse the Page model's template for the preview
        return self._models_for_preview[mode_name].template
```

```{versionadded} 7.1
The ability to enable previews for settings was added.
```
