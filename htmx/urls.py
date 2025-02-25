from django.urls import path

from . import views

app_name="htmx"

urlpatterns = [

    # Demo page with Tailwind CSS
    path("demo", views.demo, name="demo"),

    # Partials URLS
    path('oneimage/', views.oneimage, name='oneimage'),
    path("answer", views.answer, name="answer"),
    path("answer1", views.answer1, name="answer1"),

    # URLs for Boostrap CSS + navbar demo
    path("demob", views.demo_bootstrap, name="demob"),
    path('example1/', views.example1, name='example1'),
    path('example2/', views.example2, name='example2'),
    path('example3/', views.example3, name='example3'),
    path('example4/', views.example4, name='example4'),
    # path('tasks4project/<int:id>', views.tasks4project, name='tasks4project' ),
    path('member4task/<int:id>', views.member4task, name='member4task' ),
    path('tasks4project/', views.tasks4project, name='tasks4project' ),

    path("jsdemo", views.jsdemo, name="jsdemo"),
    path("response", views.jsresponse, name="response")

]