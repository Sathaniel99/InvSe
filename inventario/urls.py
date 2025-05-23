# inventario/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('login/', views.Main_LoginView.as_view(), name='login'),
    path('logout/', views.Main_LogoutView.as_view(), name='logout'),

    # PAGINAS
    path('', views.home_page, name='home'),
    
    ####################################################################################################
    ##########################                   INVENTARIO                   ##########################
    ####################################################################################################
    path('inventario/', views.main_inventario, name='inventario'),
    path('inventario/create-inventario/', views.create_inventario, name='create-inventario'),
    path('inventario/list-inventario/', views.list_inventario, name='list-inventario'),
    path('inventario/read-inventario/', views.read_inventario, name='read-inventario'),
    path('inventario/update-inventario/', views.update_inventario, name='update-inventario'),
    path('inventario/delete-inventario/', views.delete_inventario, name='delete-inventario'),

    ####################################################################################################
    #########################                    PRODUCTOS                    ##########################
    ####################################################################################################
    path('productos/resumen_productos', views.resumen_productos, name='resumen-productos'),
    path('productos/create-productos/', views.create_productos, name='create-productos'),
    path('productos/list-productos/', views.list_productos, name='list-productos'),
    path('productos/read-productos/', views.read_productos, name='read-productos'),
    path('productos/update-productos/', views.update_productos, name='update-productos'),
    path('productos/delete-productos/', views.delete_productos, name='delete-productos'),

    ####################################################################################################
    ##########################                  PROVEEDORES                   ##########################
    ####################################################################################################
    path('proveedores/resumen-proveedores', views.resumen_proveedores, name='resumen-proveedores'),
    path('proveedores/create-proveedores/', views.create_proveedores.as_view(), name='create-proveedores'),
    path('proveedores/list-proveedores/', views.list_proveedores, name='list-proveedores'),
    path('proveedores/read-proveedores/', views.read_proveedores, name='read-proveedores'),
    path('proveedores/update-proveedores/<int:id>', views.update_proveedores, name='update-proveedores'),
    path('proveedores/delete-proveedores/<int:id>', views.delete_proveedores, name='delete_proveedores'),
    
    ####################################################################################################
    ##########################                    REPORTES                    ##########################
    ####################################################################################################
    path('reportes/', views.main_reportes, name='reportes'),

    ####################################################################################################
    ##########################                   END POINTS                   ##########################
    ####################################################################################################
    path('search-proveedor-id/<int:id>', views.search_proveedor_id, name='search-proveedor'),
    path('delete-proveedores_id/<int:id>', views.delete_proveedores, name='delete-proveedores-api'),
]