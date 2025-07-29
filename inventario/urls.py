# inventario/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # AUTH
    path('login/', views.Main_LoginView.as_view(), name='login'),
    path('logout/', views.Main_LogoutView.as_view(), name='logout'),
    # configurar mi usuario
    path('config/', views.self_account_config, name='self-config'),
    # configurar un usuario
    path('user/', views.self_account_config, name='user-config'),
    # configurar el servidor
    path('server-config/', views.self_account_config, name='server-config'),
    


    # PAGINAS
    path('', views.home_page, name='home'),
    
    ####################################################################################################
    ##########################                   INVENTARIO                   ##########################
    ####################################################################################################
    path('inventario/revisar-inventario/', views.revisar_inventario, name='revisar-inventario'),
    path('inventario/list-inventario/', views.list_inventario, name='list-inventario'),
    path('inventario/read-inventario/<int:id>', views.read_inventario, name='read-inventario'),
    path('inventario/update-inventario/<int:id>', views.update_inventario, name='update-inventario'),
    path('inventario/delete-inventario/<int:id>', views.delete_inventario, name='delete-inventario'),

    ####################################################################################################
    #########################                  ACTIVOS FIJOS                  ##########################
    ####################################################################################################
    path('inventario/entrada-activos', views.entrada_activos, name='entrada-activos'),
    path('inventario/ajuste-activos', views.ajuste_activos, name='ajuste-activos'),
    path('inventario/salida-activos/<int:id>', views.salida_activos, name='salida-activos'),
    path('inventario/sin-local-activos', views.sin_local_activos, name='sin-local-activos'),
    
    # ENDPOINTS
    path('inventario/actual-inventario-api/<int:id>', views.actual_inventario_api, name='actual_inventario_api'),
    path('inventario/revisar-inventario-api/<int:id>', views.revisar_inventario_api, name='revisar_inventario_api'),
    path('inventario/historial-inventario-api/<int:id>', views.historial_inventario_api, name='historial_inventario_api'),

    ####################################################################################################
    #########################                    PRODUCTOS                    ##########################
    ####################################################################################################
    path('productos/resumen_productos', views.resumen_productos, name='resumen-productos'),
    path('productos/create-productos/', views.create_productos, name='create-productos'),
    path('productos/list-productos/', views.list_productos, name='list-productos'),
    path('productos/update-productos/<int:id>', views.update_productos, name='update-productos'),
    path('productos/delete-productos/<int:id>', views.delete_productos, name='delete-productos'),
    path('productos/show-productos/<int:id>', views.show_productos, name='show-productos'),
    path('productos/edit-productos/<int:id>', views.edit_productos, name='edit-productos'),
    path('productos/solicitados', views.productos_solicitados, name='productos-solicitados'),
    
    ####################################################################################################
    ##########################                   SOLICITUDES                  ##########################
    ####################################################################################################
    path('productos/solicitar-productos/', views.solicitar_productos, name='solicitar-productos'),
    path('productos/solicitudes-productos/', views.solicitudes_productos_tabla, name='solicitudes-productos-tabla'),
    path('productos/vaciar-carrito/', views.vaciar_carrito_api, name='vaciar-carrito-api'),
    path('productos/eliminar-solicitudes-productos-creados/<int:id>', views.eliminar_solicitudes_productos_tabla, name='eliminar-solicitudes-productos-creados'),
    
    # ENDPOINTS
    path('productos/solicitudes-productos-api/', views.solicitudes_productos_api, name='solicitudes-productos-api'),
    path('productos/preparar_solicitud/<int:id>/<int:cant>', views.preparar_solicitud_api, name='preparar_solicitud-api'),
    path('productos/agregar-item-solicitud-api/<int:id>/<int:cant>', views.agregar_a_la_solicitud_api, name='agregar-item_solicitud-api'),
    path('productos/ver-solicitud-api/', views.ver_solicitud, name='ver_solicitud'),
    path('productos/eliminar-item-api/<str:producto_id>/', views.eliminar_item_solicitud_api, name='eliminar-item-solicitud-api'),
    path('productos/confirmar-solicitud-api/', views.confirmar_solicitud_api, name='confirmar-solicitud-api'),
    path('productos/ver-solicitud-creada-api/<int:id>', views.ver_solicitud_creada, name='ver-solicitud-creada-api'),
    path('productos/rechazar-solicitud/<int:id>', views.rechazar_solicitud, name='rechazar-solicitud-api'),
    path('productos/aprobar-solicitud/<int:id>', views.aprobar_solicitud, name='aprobar-solicitud-api'),


    ####################################################################################################
    ##########################                  PROVEEDORES                   ##########################
    ####################################################################################################
    path('proveedores/resumen-proveedores', views.resumen_proveedores, name='resumen-proveedores'),
    path('proveedores/create-proveedores/', views.create_proveedores.as_view(), name='create-proveedores'),
    path('proveedores/list-proveedores/', views.list_proveedores, name='list-proveedores'),
    path('proveedores/update-proveedores/<int:id>', views.update_proveedores, name='update-proveedores'),
    path('proveedores/delete-proveedores/<int:id>', views.delete_proveedores, name='delete-proveedores-api'),
    path('proveedores/show-proveedor/<int:id>', views.show_proveedor, name='show-proveedor'),
    
    ####################################################################################################
    ##########################                    REPORTES                    ##########################
    ####################################################################################################
    path('reportes/', views.main_reportes, name='reportes'),

    ####################################################################################################
    ##########################                   END POINTS                   ##########################
    ####################################################################################################
    path('update-user', views.update_self_user, name='update-self-user'),
    path('update-password', views.update_self_password, name='update-self-password'),
    path('alertas-stock-api', views.alertas_stock_api, name='alertas-stock-api'),
    path('alertas-stocks-api-filter', views.alertas_stocks_api_filter, name='alertas-stocks-api-filter'),
    path('alertas-stocks-api-delete/<int:id>', views.alertas_stocks_api_delete, name='alertas-stocks-api-delete'),
]